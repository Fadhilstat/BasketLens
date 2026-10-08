"""Explainable holdout evidence for retail product association candidates.

These descriptive measures cannot estimate incremental conversion, profit, or the
causal effect of presenting a recommendation to a shopper.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from basketlens.mining import matching_rules

Z_95 = 1.959963984540054
EVIDENCE_COLUMNS = [
    "holdout_confidence_low_95", "holdout_confidence_high_95", "evidence_label"
]


def wilson_interval(hits: int, observations: int, z: float = Z_95) -> tuple[float, float]:
    """Approximate binomial confidence interval; undefined without observations."""
    if observations < 0 or hits < 0 or hits > observations:
        raise ValueError("Expected 0 <= hits <= observations")
    if observations == 0:
        return float("nan"), float("nan")
    p = hits / observations
    z2 = z * z
    denominator = 1 + z2 / observations
    center = (p + z2 / (2 * observations)) / denominator
    halfwidth = z * math.sqrt(p * (1 - p) / observations + z2 / (4 * observations ** 2)) / denominator
    return (0.0 if hits == 0 else max(0.0, center - halfwidth),
            1.0 if hits == observations else min(1.0, center + halfwidth))


def annotate_evidence(evaluation: pd.DataFrame, min_fires: int = 20) -> pd.DataFrame:
    """Add descriptive repeat-evidence labels and Wilson intervals.

    A repeated association means the holdout lift is > 1 with at least
    ``min_fires`` antecedent appearances. This is not a significance test.
    """
    if min_fires < 1:
        raise ValueError("min_fires must be positive")
    out = evaluation.copy()
    for column in EVIDENCE_COLUMNS:
        if column not in out.columns:
            out[column] = pd.Series(index=out.index, dtype="object" if column == "evidence_label" else float)
    if out.empty:
        return out
    if (out["hits"] < 0).any() or (out["fires"] < out["hits"]).any():
        raise ValueError("Invalid rule hit/firing counts")
    intervals = [wilson_interval(int(hits), int(fires))
                 for hits, fires in zip(out["hits"], out["fires"])]
    out["holdout_confidence_low_95"] = [row[0] for row in intervals]
    out["holdout_confidence_high_95"] = [row[1] for row in intervals]
    sufficient = out["fires"] >= min_fires
    observed_again = sufficient & out["holdout_lift"].gt(1)
    out["evidence_label"] = np.select(
        [~sufficient, observed_again],
        ["Limited observations", "Repeated association"],
        default="Not repeated above baseline"
    )
    return out


def recommend_with_holdout(
    rules: pd.DataFrame, evaluation: pd.DataFrame,
    cart: list[str], limit: int = 10, min_fires: int = 20
) -> pd.DataFrame:
    """Rank eligible cart associations by later evidence before training lift.

    Does not present later co-occurrence as a measured recommendation response.
    """
    candidates = matching_rules(rules, cart)
    if candidates.empty:
        return candidates.assign(**{column: pd.Series(dtype="object" if column == "evidence_label" else float)
                                   for column in EVIDENCE_COLUMNS})
    scored = annotate_evidence(evaluation, min_fires)
    values = ["antecedent", "consequent", "fires", "hits", "holdout_confidence",
              "holdout_lift", *EVIDENCE_COLUMNS]
    matched = candidates.merge(scored[values], on=["antecedent", "consequent"],
                               how="left", validate="one_to_one")
    matched["evidence_label"] = matched["evidence_label"].fillna("Not evaluated")
    priorities = {"Repeated association": 0, "Not repeated above baseline": 1,
                  "Limited observations": 2, "Not evaluated": 3}
    matched["evidence_priority"] = matched["evidence_label"].map(priorities).astype(int)
    result = matched.sort_values(
        ["evidence_priority", "matched_items", "fires", "holdout_confidence_low_95",
         "joint_count", "lift", "antecedent"],
        ascending=[True, False, False, False, False, False, True],
        na_position="last"
    )
    return result.drop_duplicates("consequent").head(limit).drop(columns="evidence_priority").reset_index(drop=True)
