"""Release audit on complete UCI transactions and headless Streamlit dashboard.

Only aggregate evidence is reported; no invoice lines or customer identifiers are exported.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from basketlens.validation import validate_artifacts


def check_equivalent_pairs(pairwise: pd.DataFrame, fpgrowth: pd.DataFrame) -> int:
    fp_pairs = fpgrowth.loc[fpgrowth["antecedent_size"].eq(1) & fpgrowth["consequent_size"].eq(1)]
    keys = ["antecedent", "consequent"]
    if pairwise.duplicated(keys).any() or fp_pairs.duplicated(keys).any():
        raise ValueError("Duplicate 1-to-1 rules")
    a = pairwise.set_index(keys).sort_index()
    b = fp_pairs.set_index(keys).sort_index()
    if not a.index.equals(b.index):
        raise ValueError("Pairwise and FP-Growth produced different one-to-one rule keys")
    for column in ("train_baskets", "antecedent_count", "consequent_count", "joint_count"):
        if not (a[column] == b[column]).all():
            raise ValueError(f"Inconsistent itemset counts for {column}")
    for column in ("support", "confidence", "lift", "leverage"):
        if not np.allclose(a[column].to_numpy(dtype=float), b[column].to_numpy(dtype=float),
                           rtol=1e-8, atol=1e-10):
            raise ValueError(f"Inconsistent rule metrics for {column}")
    if not len(a):
        raise ValueError("No qualifying pairwise rules from full source")
    return len(a)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise", required=True, type=Path)
    parser.add_argument("--fpgrowth", required=True, type=Path)
    parser.add_argument("--report", default=Path("reports"), type=Path)
    args = parser.parse_args()
    for directory in (args.pairwise, args.fpgrowth):
        validate_artifacts(directory)
    pair_meta = json.loads((args.pairwise / "manifest.json").read_text(encoding="utf-8"))
    fp_meta = json.loads((args.fpgrowth / "manifest.json").read_text(encoding="utf-8"))
    quality = json.loads((args.fpgrowth / "quality.json").read_text(encoding="utf-8"))
    if pair_meta["method"]["algorithm"] != "pairwise" or fp_meta["method"]["algorithm"] != "fpgrowth":
        raise ValueError("Incorrect algorithm used for audit")
    for metadata in (pair_meta, fp_meta):
        if metadata["partial_data"] or metadata["row_limit_per_sheet"] is not None:
            raise ValueError("Cannot certify source data when only a partial sample was used")
    if quality["input_rows"] < 1_000_000:
        raise ValueError("Too few lines for the full two-year UCI workbook")
    for field in ("source_sha256", "train_baskets", "holdout_baskets", "basket_count_all", "cutoff_utc_naive"):
        if pair_meta[field] != fp_meta[field]:
            raise ValueError(f"Source/split inconsistency: {field}")
    pairs = pd.read_csv(args.pairwise / "rules.csv", dtype={"antecedent": str, "consequent": str})
    fp = pd.read_csv(args.fpgrowth / "rules.csv", dtype={"antecedent": str, "consequent": str})
    matched = check_equivalent_pairs(pairs, fp)
    conflicts = quality.get("source_invoice_conflicts", {})
    report = {
        "status": "PASS",
        "source": "UCI Online Retail II",
        "source_sha256": fp_meta["source_sha256"],
        "input_rows": int(quality["input_rows"]),
        "eligible_lines": int(quality["analysis_eligible_rows"]),
        "excluded_lines": int(quality["excluded_rows"]),
        "quarantined_lines": int(conflicts.get("quarantined_rows", 0)),
        "inconsistent_invoice_policy": fp_meta["inconsistent_invoice_policy"],
        "all_baskets": int(fp_meta["basket_count_all"]),
        "train_baskets": int(fp_meta["train_baskets"]),
        "holdout_baskets": int(fp_meta["holdout_baskets"]),
        "cutoff": fp_meta["cutoff_utc_naive"],
        "pairwise_rules": len(pairs),
        "fpgrowth_rules": len(fp),
        "matched_one_to_one_rules": matched,
        "multi_antecedent_rules": int(fp["antecedent_size"].gt(1).sum()),
        "candidate_mining": fp_meta["candidate_mining"],
        "rejection_reasons": quality["reason_counts"],
        "scope": "Descriptive historical association, no causal uplift inference",
    }
    args.report.mkdir(parents=True, exist_ok=True)
    (args.report / "real_dataset_audit.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print("REAL_DATASET_AUDIT_PASS " + json.dumps(report, sort_keys=True))

    from streamlit.testing.v1 import AppTest
    os.environ["BASKETLENS_DATA_DIR"] = str(args.fpgrowth.resolve())
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"), default_timeout=90).run()
    if app.exception:
        raise AssertionError(f"Streamlit runtime raised exceptions: {app.exception}")
    if len(app.metric) < 3:
        raise AssertionError("Missing essential dashboard KPIs")
    if app.multiselect:
        options = list(app.multiselect[0].options)
        if options:
            app.multiselect[0].set_value([options[0]]).run()
            if app.exception:
                raise AssertionError(f"Basket selector raised exceptions: {app.exception}")
    print("REAL_DATA_STREAMLIT_HEADLESS_PASS")


if __name__ == "__main__":
    main()
