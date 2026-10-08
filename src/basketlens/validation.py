"""Independent integrity checks for generated BasketLens research artifacts.

A successful check verifies internal arithmetic and output consistency. It does
not establish that the input dataset is authentic or that the source is complete.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ARTIFACT_FILES = (
    "manifest.json", "quality.json", "rules.csv", "evaluation.csv",
    "basket_summary.csv.gz", "products.csv", "countries.csv", "monthly.csv",
    "monthly_country.csv"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Artifact validation failed: {message}")


def _all_close(actual, expected, message: str, *, atol: float = 1e-10) -> None:
    result = np.isclose(np.asarray(actual, dtype=float), np.asarray(expected, dtype=float),
                        rtol=1e-8, atol=atol, equal_nan=True)
    _require(bool(np.all(result)), message)


def validate_artifacts(output_dir: str | Path) -> dict:
    """Validate arithmetic invariants in an existing analytics export."""
    path = Path(output_dir)
    for filename in ARTIFACT_FILES:
        _require((path / filename).is_file(), f"missing {filename}")

    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    quality = json.loads((path / "quality.json").read_text(encoding="utf-8"))
    baskets = pd.read_csv(path / "basket_summary.csv.gz", parse_dates=["invoice_date"])
    countries = pd.read_csv(path / "countries.csv")
    monthly = pd.read_csv(path / "monthly.csv")
    monthly_country = pd.read_csv(path / "monthly_country.csv")
    products = pd.read_csv(path / "products.csv", dtype={"stock_code": str})
    rules = pd.read_csv(path / "rules.csv", dtype={"antecedent": str, "consequent": str})
    evaluation = pd.read_csv(path / "evaluation.csv", dtype={"antecedent": str, "consequent": str})

    _require(bool(re.fullmatch(r"[0-9a-f]{64}", manifest.get("source_sha256", ""))),
             "source SHA256 is missing or invalid")
    _require(manifest["basket_count_all"] == len(baskets), "manifest basket count mismatch")
    _require(manifest["train_baskets"] + manifest["holdout_baskets"] == len(baskets),
             "train and holdout do not cover all baskets")
    _require(baskets["basket_id"].notna().all() and baskets["basket_id"].is_unique,
             "basket IDs must be unique and populated")
    _require(baskets["invoice_date"].notna().all(), "basket dates are invalid")
    _require(baskets["basket_revenue_gbp"].gt(0).all(), "baskets have nonpositive sales value")
    _require(baskets["item_count"].ge(1).all(), "baskets have no products")
    _require(sum(quality["reason_counts"].values()) == quality["input_rows"],
             "quality reasons do not add to the source record count")
    _require(quality["valid_rows"] + quality["excluded_rows"] == quality["input_rows"],
             "eligible and excluded rows do not add to the source record count")
    conflicts = quality.get("source_invoice_conflicts", {})
    quarantined = int(conflicts.get("quarantined_rows", 0))
    _require(quality.get("analysis_eligible_rows", quality["valid_rows"] - quarantined)
             == quality["valid_rows"] - quarantined,
             "quarantined invoice rows not reconciled with analysis eligible rows")

    for summary_name, summary in (("countries", countries), ("monthly", monthly),
                                  ("monthly_country", monthly_country)):
        _require(int(summary["baskets"].sum()) == len(baskets),
                 f"{summary_name} basket totals mismatch")
        _all_close(summary["sales_gbp"].sum(), baskets["basket_revenue_gbp"].sum(),
                   f"{summary_name} sales totals mismatch", atol=0.01)
    _all_close(products["sales_gbp"].sum(), baskets["basket_revenue_gbp"].sum(),
               "product sales totals mismatch", atol=0.01)

    _require(len(rules) == manifest["rule_count"], "manifest rule count mismatch")
    _require(len(evaluation) == manifest["evaluated_rule_count"] == len(rules),
             "holdout evaluation count mismatch")
    key_columns = ["antecedent", "consequent"]
    _require(not rules.duplicated(key_columns).any(), "duplicated rules")
    _require(not evaluation.duplicated(key_columns).any(), "duplicated evaluated rules")
    _require(set(zip(rules["antecedent"], rules["consequent"])) ==
             set(zip(evaluation["antecedent"], evaluation["consequent"])),
             "rule/evaluation keys differ")

    if not rules.empty:
        n_train = int(manifest["train_baskets"])
        _require((rules["train_baskets"] == n_train).all(), "inconsistent rule denominators")
        _require((rules["antecedent_count"] > 0).all() and
                 (rules["consequent_count"] > 0).all(), "zero product appearance count")
        _require((rules["joint_count"] <= rules[["antecedent_count", "consequent_count"]].min(axis=1)).all(),
                 "joint appearances exceed marginal appearances")
        _require(rules["joint_count"].gt(0).all(), "nonpositive rule co-occurrences")
        _all_close(rules["support"], rules["joint_count"] / n_train, "support arithmetic mismatch")
        _all_close(rules["antecedent_support"], rules["antecedent_count"] / n_train,
                   "antecedent support arithmetic mismatch")
        _all_close(rules["consequent_support"], rules["consequent_count"] / n_train,
                   "consequent support arithmetic mismatch")
        _all_close(rules["confidence"], rules["joint_count"] / rules["antecedent_count"],
                   "training confidence arithmetic mismatch")
        _all_close(rules["lift"], rules["confidence"] / rules["consequent_support"],
                   "training lift arithmetic mismatch")
        _all_close(rules["leverage"], rules["support"] -
                   rules["antecedent_support"] * rules["consequent_support"],
                   "training leverage arithmetic mismatch")

        holdout_n = int(manifest["holdout_baskets"])
        _require((evaluation["holdout_baskets"] == holdout_n).all(),
                 "inconsistent holdout denominators")
        _require(evaluation["fires"].between(0, holdout_n).all(), "out-of-range rule firings")
        _require(evaluation["hits"].between(0, holdout_n).all(), "out-of-range rule hits")
        _require((evaluation["hits"] <= evaluation["fires"]).all(),
                 "rule hits exceed firings")
        _require(evaluation["holdout_baseline_support"].between(0, 1).all(),
                 "invalid holdout baseline")
        _all_close(evaluation["holdout_coverage"], evaluation["fires"] / holdout_n,
                   "holdout coverage arithmetic mismatch")
        with_fires = evaluation["fires"] > 0
        no_fires = ~with_fires
        _require(evaluation.loc[no_fires, "holdout_confidence"].isna().all(),
                 "holdout confidence should be missing without firings")
        _all_close(evaluation.loc[with_fires, "holdout_confidence"],
                   evaluation.loc[with_fires, "hits"] / evaluation.loc[with_fires, "fires"],
                   "holdout confidence arithmetic mismatch")
        valid_lift = with_fires & evaluation["holdout_baseline_support"].gt(0)
        _all_close(evaluation.loc[valid_lift, "holdout_lift"],
                   evaluation.loc[valid_lift, "holdout_confidence"] /
                   evaluation.loc[valid_lift, "holdout_baseline_support"],
                   "holdout lift arithmetic mismatch")
        _require(evaluation.loc[~valid_lift, "holdout_lift"].isna().all(),
                 "holdout lift should be missing when undefined")
        joined = evaluation.merge(rules[key_columns + ["confidence", "lift"]],
                                  on=key_columns, how="inner", validate="one_to_one")
        _all_close(joined["train_confidence"], joined["confidence"],
                   "evaluation training confidence mismatch")
        _all_close(joined["train_lift"], joined["lift"],
                   "evaluation training lift mismatch")

    for filename in ("basket_summary.csv.gz", "products.csv", "countries.csv",
                     "monthly.csv", "monthly_country.csv", "rules.csv", "evaluation.csv"):
        cols = pd.read_csv(path / filename, nrows=0).columns.str.lower().tolist()
        _require("customer_id" not in cols and "customerid" not in cols,
                 f"personal identifiers leaked into {filename}")

    return {"status": "PASS", "basket_count": int(len(baskets)),
            "rule_count": int(len(rules)), "evaluated_rule_count": int(len(evaluation)),
            "checks": ["file_presence", "source_hash_format", "basket_identity",
                       "quality_counts", "aggregation_consistency", "rule_math",
                       "holdout_math", "privacy_columns"]}
