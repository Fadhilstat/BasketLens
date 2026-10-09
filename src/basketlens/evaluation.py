"""Point-in-time rule validation, explicitly not uplift or causal evaluation."""
from __future__ import annotations

from collections import defaultdict
import pandas as pd
import numpy as np


def temporal_split(baskets: pd.DataFrame, train_fraction: float = 0.8
                  ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """Chronological partition, never split baskets sharing the cutoff timestamp."""
    if not 0.5 <= train_fraction < 1:
        raise ValueError("train_fraction must be in [0.5, 1)")
    if len(baskets) < 4:
        raise ValueError("At least 4 baskets are required for temporal evaluation")
    sorted_baskets = baskets.sort_values(["invoice_date", "basket_id"]).reset_index(drop=True)
    cutoff = pd.Timestamp(sorted_baskets.iloc[int(len(sorted_baskets) * train_fraction)]["invoice_date"])
    train = sorted_baskets.loc[sorted_baskets["invoice_date"] < cutoff].copy()
    test = sorted_baskets.loc[sorted_baskets["invoice_date"] >= cutoff].copy()
    if train.empty or test.empty:
        raise ValueError("Cannot split baskets by time: too few distinct invoice timestamps")
    assert train["invoice_date"].max() < test["invoice_date"].min()
    assert set(train["basket_id"]).isdisjoint(set(test["basket_id"]))
    return train, test, cutoff


def evaluate_rules(rules: pd.DataFrame, test_baskets: pd.DataFrame,
                   test_items: pd.DataFrame) -> pd.DataFrame:
    """Measure each training rule's later conditional co-occurrence rate.

    Confidence is a conditional proportion, not proof a recommendation causes a sale.
    Blank holdout confidence means the rule never fired in the holdout period.
    """
    columns = ["antecedent", "consequent", "train_confidence", "train_lift",
               "holdout_baskets", "fires", "hits", "holdout_confidence",
               "holdout_baseline_support", "holdout_lift", "holdout_coverage"]
    if rules.empty:
        return pd.DataFrame(columns=columns)
    num_baskets = len(test_baskets)
    if num_baskets == 0:
        raise ValueError("Holdout baskets are required")
    known_ids = set(test_baskets["basket_id"].astype(str))
    occurrences: dict[str, set[str]] = defaultdict(set)
    for basket_id, sku in test_items[["basket_id", "stock_code"]].itertuples(index=False, name=None):
        key = str(basket_id)
        if key in known_ids:
            occurrences[str(sku)].add(key)

    def basket_intersection(key: str) -> set[str]:
        sets = [occurrences.get(p, set()) for p in str(key).split("||")]
        return set.intersection(*sets) if sets else set()

    rows = []
    for row in rules.itertuples(index=False):
        fired = basket_intersection(row.antecedent)
        target = basket_intersection(row.consequent)
        hits = len(fired & target)
        baseline = len(target) / num_baskets
        holdout_conf = hits / len(fired) if fired else np.nan
        holdout_lift = (holdout_conf / baseline) if fired and baseline > 0 else np.nan
        rows.append({
            "antecedent": row.antecedent, "consequent": row.consequent,
            "train_confidence": float(row.confidence), "train_lift": float(row.lift),
            "holdout_baskets": num_baskets, "fires": len(fired), "hits": hits,
            "holdout_confidence": holdout_conf,
            "holdout_baseline_support": baseline, "holdout_lift": holdout_lift,
            "holdout_coverage": len(fired) / num_baskets,
        })
    return pd.DataFrame(rows, columns=columns)
