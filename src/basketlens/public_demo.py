"""Generate and validate a compact, aggregate-only public BasketLens exhibit.

The UCI source workbook and invoice-level tables never leave the CI job.
Only training-selected candidate rules and aggregate metrics are exported.
"""
from __future__ import annotations

import base64
import binascii
import gzip
import hashlib
import json
from pathlib import Path

import pandas as pd

SCHEMA = "basketlens.public-demo.v1"
FRAMES = ("products", "countries", "monthly", "monthly_country", "rules", "evaluation", "basket_rollup")
PUBLIC_FILENAME = "basketlens_public_v1.b64"
FORBIDDEN_FIELDS = {"basket_id", "invoice_no", "customer_id", "source_row", "email", "first_name", "last_name"}
MAX_COMPRESSED_BYTES = 6_000_000


def _rows(frame: pd.DataFrame) -> list[dict]:
    if FORBIDDEN_FIELDS & set(frame.columns):
        raise ValueError(f"Public exhibit includes forbidden columns: {FORBIDDEN_FIELDS & set(frame.columns)}")
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")


def _select_rules(rules: pd.DataFrame, pair_limit: int, multi_limit: int) -> pd.DataFrame:
    """Select rule candidates using earlier-training information only."""
    ordering = ["joint_count", "confidence", "lift", "antecedent", "consequent"]
    ascending = [False, False, False, True, True]
    ordered = rules.sort_values(ordering, ascending=ascending, kind="mergesort")
    pairs = ordered[~ordered["antecedent"].astype(str).str.contains("||", regex=False)].head(pair_limit)
    multi = ordered[ordered["antecedent"].astype(str).str.contains("||", regex=False)].head(multi_limit)
    return pd.concat([pairs, multi], ignore_index=True)


def build_public_demo(source: str | Path, target: str | Path,
                      pair_limit: int = 1200, multi_limit: int = 300) -> dict:
    """Produce a deterministic, de-identified exhibit from verified full-run outputs."""
    source, target = Path(source), Path(target)
    if pair_limit < 1 or multi_limit < 0:
        raise ValueError("Invalid rule selection limits")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    quality = json.loads((source / "quality.json").read_text(encoding="utf-8"))
    if manifest.get("partial_data"):
        raise ValueError("Cannot publish partial dataset as a full historical exhibit")
    if manifest.get("inconsistent_invoice_policy") != "quarantine":
        raise ValueError("Public exhibit requires an audited invoice conflict policy")
    if manifest.get("method", {}).get("algorithm") != "fpgrowth":
        raise ValueError("Expected full FP-Growth analytics source")
    rules = pd.read_csv(source / "rules.csv", dtype={"antecedent": str, "consequent": str})
    evaluation = pd.read_csv(source / "evaluation.csv", dtype={"antecedent": str, "consequent": str})
    selected = _select_rules(rules, pair_limit, multi_limit)
    selected_evaluation = selected[["antecedent", "consequent"]].merge(
        evaluation, how="left", on=["antecedent", "consequent"], validate="one_to_one", indicator=True
    )
    if not selected_evaluation["_merge"].eq("both").all():
        raise ValueError("Missing holdout evaluation for a selected rule")
    selected_evaluation = selected_evaluation.drop(columns="_merge")
    baskets = pd.read_csv(source / "basket_summary.csv.gz",
                          usecols=["country", "item_count", "basket_revenue_gbp"],
                          dtype={"country": str})
    rollup = baskets.groupby(["country", "item_count"], dropna=False, as_index=False).agg(
        basket_count=("basket_revenue_gbp", "size"),
        sales_gbp=("basket_revenue_gbp", "sum"),
    )
    if int(rollup["basket_count"].sum()) != int(manifest["basket_count_all"]):
        raise ValueError("Public aggregate does not reconcile to total baskets")
    catalog = pd.read_csv(source / "products.csv", dtype={"stock_code": str})
    rule_skus = set()
    for column in ("antecedent", "consequent"):
        for terms in selected[column].astype(str):
            rule_skus.update(terms.split("||"))
    leading_skus = set(catalog.nlargest(40, "sales_gbp")["stock_code"])
    public_catalog = catalog.loc[catalog["stock_code"].isin(rule_skus | leading_skus)].copy()
    frames = {
        name: (public_catalog if name == "products" else selected if name == "rules" else
               selected_evaluation if name == "evaluation" else rollup if name == "basket_rollup" else
               pd.read_csv(source / f"{name}.csv"))
        for name in FRAMES
    }
    publication = {
        "schema": SCHEMA,
        "source": "UCI Online Retail II (Daqing Chen, 2019), CC BY 4.0, DOI 10.24432/C5CG6D",
        "scope": "Historical descriptive analysis. Training-selected subset of association rules.",
        "privacy": "No customer IDs, invoice numbers, raw invoice rows or item-level purchases",
        "full_rule_count": len(rules),
        "visible_rule_count": len(selected),
        "pair_limit": pair_limit,
        "multi_limit": multi_limit,
        "selection": "Training joint count, confidence and lift, descending. No holdout-based selection.",
    }
    pack = {"schema": SCHEMA, "manifest": manifest, "quality": quality,
            "publication": publication, "tables": {name: _rows(frame) for name, frame in frames.items()}}
    serialized = json.dumps(pack, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    compressed = gzip.compress(serialized, mtime=0)
    if len(compressed) > MAX_COMPRESSED_BYTES:
        raise ValueError("Public exhibit is unexpectedly large")
    target.mkdir(parents=True, exist_ok=True)
    (target / PUBLIC_FILENAME).write_text(base64.b64encode(compressed).decode("ascii") + "\n", encoding="ascii")
    (target / f"{PUBLIC_FILENAME}.sha256").write_text(hashlib.sha256(compressed).hexdigest() + "\n", encoding="ascii")
    return {"status": "PASS", "compressed_bytes": len(compressed),
            "full_rule_count": len(rules), "visible_rule_count": len(selected),
            "baskets": int(rollup["basket_count"].sum()), "source_sha256": manifest["source_sha256"]}


def load_public_demo(encoded_path: str | Path) -> dict:
    """Verify the bundled bytes, schema, counts, joins and absence of identifiers."""
    path = Path(encoded_path)
    try:
        compressed = base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
    except binascii.Error as error:
        raise ValueError("Invalid public exhibit encoding") from error
    if len(compressed) > MAX_COMPRESSED_BYTES:
        raise ValueError("Public exhibit exceeds size limit")
    expected = path.with_name(path.name + ".sha256").read_text(encoding="ascii").strip()
    if hashlib.sha256(compressed).hexdigest() != expected:
        raise ValueError("Public exhibit checksum mismatch")
    pack = json.loads(gzip.decompress(compressed).decode("utf-8"))
    if pack.get("schema") != SCHEMA or set(pack.get("tables", {})) != set(FRAMES):
        raise ValueError("Unexpected public exhibit schema")
    tables = {name: pd.DataFrame(pack["tables"][name]) for name in FRAMES}
    if any(FORBIDDEN_FIELDS & set(df.columns) for df in tables.values()):
        raise ValueError("Forbidden fields in public exhibit")
    manifest, quality = pack["manifest"], pack["quality"]
    if int(tables["basket_rollup"]["basket_count"].sum()) != int(manifest["basket_count_all"]):
        raise ValueError("Public exhibit basket totals do not reconcile")
    for name in ("rules", "evaluation"):
        if len(tables[name]) != int(pack["publication"]["visible_rule_count"]):
            raise ValueError(f"Public exhibit {name} count mismatch")
    if not tables["rules"][["antecedent", "consequent"]].equals(
            tables["evaluation"][["antecedent", "consequent"]]):
        raise ValueError("Public exhibit rule evaluation keys differ")
    return {"manifest": manifest, "quality": quality, "publication": pack["publication"], **tables}
