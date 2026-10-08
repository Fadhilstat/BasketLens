"""Statistical evidence labels and cart rank tests with synthetic baskets only."""
import math

import pandas as pd
import pytest

from basketlens.insights import annotate_evidence, recommend_with_holdout, wilson_interval
from basketlens.mining import RuleConfig, mine_pairwise


def test_wilson_interval_extremes_and_invalid_counts():
    low, high = wilson_interval(0, 100)
    assert low == 0.0
    assert 0 < high < 0.05
    low, high = wilson_interval(100, 100)
    assert 0.95 < low < 1
    assert high == 1.0
    assert all(math.isnan(v) for v in wilson_interval(0, 0))
    with pytest.raises(ValueError, match="0 <= hits"):
        wilson_interval(4, 3)


def test_evidence_is_descriptive_not_statistical_significance():
    rows = pd.DataFrame({
        "antecedent": ["A", "B", "C"], "consequent": ["D", "E", "F"],
        "fires": [80, 80, 4], "hits": [40, 5, 4],
        "holdout_lift": [2.0, 0.6, 3.0],
        "holdout_confidence": [0.5, 0.0625, 1.0],
    })
    result = annotate_evidence(rows, min_fires=20)
    assert result["evidence_label"].tolist() == [
        "Repeated association", "Not repeated above baseline", "Limited observations"
    ]
    assert result.loc[0, "holdout_confidence_low_95"] < 0.5
    assert result.loc[0, "holdout_confidence_high_95"] > 0.5


def test_holdout_ranking_can_override_training_lift():
    baskets = pd.DataFrame({"basket_id": [str(i) for i in range(1, 7)]})
    items = pd.DataFrame([(b, product) for b, products in {
        "1": "AB", "2": "AB", "3": "AC", "4": "AC", "5": "A", "6": "A"
    }.items() for product in products], columns=["basket_id", "stock_code"])
    rules, _ = mine_pairwise(baskets, items, RuleConfig(
        min_support=.01, min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0
    ))
    chosen = rules.loc[rules["antecedent"].eq("A")].copy()
    evaluation = pd.DataFrame({
        "antecedent": ["A", "A"], "consequent": ["B", "C"],
        "fires": [50, 5], "hits": [25, 5], "holdout_lift": [1.4, 5.0],
        "holdout_confidence": [.5, 1.0],
    })
    recommendations = recommend_with_holdout(chosen, evaluation, ["A"], min_fires=20)
    assert recommendations["consequent"].tolist() == ["B", "C"]
    assert recommendations["evidence_label"].iloc[0] == "Repeated association"
    assert recommend_with_holdout(chosen, evaluation, []).empty
