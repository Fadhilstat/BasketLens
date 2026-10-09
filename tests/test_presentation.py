"""Human-readable views must preserve arithmetic and avoid future-data leakage."""
import pandas as pd
import pytest

from basketlens.presentation import (
    compact_rule_table, example_basket_seed, filter_rule_view, lift_meaning, product_name,
    quality_reason_label, snapshot_from_rollup,
)


def test_snapshot_from_aggregates_matches_original_baskets():
    rollup = pd.DataFrame([
        {"country": "UK", "item_count": 1, "basket_count": 3, "sales_gbp": 30.0},
        {"country": "UK", "item_count": 2, "basket_count": 2, "sales_gbp": 50.0},
        {"country": "DE", "item_count": 3, "basket_count": 5, "sales_gbp": 120.0},
    ])
    whole = snapshot_from_rollup(rollup)
    assert whole.baskets == 10
    assert whole.sales_gbp == 200
    assert whole.average_gbp == 20
    assert whole.multi_product_share == pytest.approx(.7)
    uk = snapshot_from_rollup(rollup[rollup.country == "UK"])
    assert uk.baskets == 5
    assert uk.sales_gbp == 80
    assert uk.multi_product_share == pytest.approx(.4)


def test_empty_snapshot_and_invalid_values():
    schema = ["item_count", "basket_count", "sales_gbp"]
    empty = snapshot_from_rollup(pd.DataFrame(columns=schema))
    assert empty.baskets == 0 and empty.average_gbp is None
    assert empty.multi_product_share is None
    with pytest.raises(ValueError, match="Invalid basket count"):
        snapshot_from_rollup(pd.DataFrame({"item_count": [2], "basket_count": [-1], "sales_gbp": [10]}))
    with pytest.raises(ValueError, match="Invalid positive sale"):
        snapshot_from_rollup(pd.DataFrame({"item_count": [1], "basket_count": [2], "sales_gbp": [float("inf")]}))
    with pytest.raises(ValueError, match="Missing basket rollup"):
        snapshot_from_rollup(pd.DataFrame({"basket_count": [2], "item_count": [1]}))


def test_rule_search_and_rank_use_only_training_data():
    rules = pd.DataFrame([
        {"antecedent": "SKU1", "consequent": "SKU2", "joint_count": 40,
         "confidence": .4, "lift": 1.4},
        {"antecedent": "SKU2", "consequent": "SKU3", "joint_count": 25,
         "confidence": .9, "lift": 3.0},
        {"antecedent": "SKU1||SKU2", "consequent": "SKU3", "joint_count": 10,
         "confidence": .8, "lift": 2.0},
    ])
    names = {"SKU1": "Blue Mugs", "SKU2": "White Plates", "SKU3": "Red Candles"}
    full = filter_rule_view(rules, names, minimum_lift=1.2, minimum_joint=1)
    assert list(full["joint_count"]) == [40, 25, 10]
    filtered = filter_rule_view(rules, names, minimum_lift=1.0, minimum_joint=20,
                                search="mUGS")
    assert len(filtered) == 1
    assert filtered.iloc[0]["consequent_label"] == "White Plates (SKU2)"
    escaped_search = filter_rule_view(rules, names, search="SKU1||SKU2")
    assert len(escaped_search) == 1
    assert escaped_search.iloc[0]["antecedent"] == "SKU1||SKU2"
    hidden = filter_rule_view(rules, names, minimum_joint=100)
    assert hidden.empty
    compact = compact_rule_table(full)
    assert compact.iloc[0]["Confidence (%)"] == pytest.approx(40)
    assert compact.iloc[0]["Lift (x)"] == pytest.approx(1.4)
    assert "Purchased together" in compact.columns


def test_glossary_does_not_claim_uplift():
    assert "1.50" in lift_meaning(1.5)
    assert "together" in lift_meaning(1)
    assert "less frequent" in lift_meaning(.6)
    assert "unavailable" in lift_meaning(float("nan"))
    assert "revenue" not in lift_meaning(1.3)
    assert product_name("SKU1||SKU2", {"SKU1": "A", "SKU2": "B"}) == "A (SKU1) + B (SKU2)"
    assert quality_reason_label("cancellation") == "Cancelled or returned item"
    assert quality_reason_label("test_new_reason") == "Test new reason"


def test_example_basket_uses_training_counts_with_literal_multisku_split():
    rules = pd.DataFrame([
        {"antecedent": "SKU1||SKU2", "joint_count": 90},
        {"antecedent": "SKU3", "joint_count": 40},
    ])
    assert example_basket_seed(rules, ["SKU1", "SKU3"]) == "SKU1"
    assert example_basket_seed(rules, ["SKU3"]) == "SKU3"
    assert example_basket_seed(rules, []) is None
    assert example_basket_seed(pd.DataFrame(columns=rules.columns), ["SKU1"]) is None


def test_pair_highlights_deduplicate_symmetry_and_keep_direction():
    from basketlens.presentation import top_unique_pairs
    import pandas as pd
    rules = pd.DataFrame([
        {"antecedent": "A", "consequent": "B", "antecedent_size": 1,
         "consequent_size": 1, "joint_count": 13, "confidence": .6, "lift": 2.5},
        {"antecedent": "B", "consequent": "A", "antecedent_size": 1,
         "consequent_size": 1, "joint_count": 13, "confidence": .2, "lift": 2.5},
        {"antecedent": "A", "consequent": "C", "antecedent_size": 1,
         "consequent_size": 1, "joint_count": 9, "confidence": .4, "lift": 1.8},
        {"antecedent": "A||B", "consequent": "C", "antecedent_size": 2,
         "consequent_size": 1, "joint_count": 90, "confidence": .8, "lift": 7.8},
    ])
    found = top_unique_pairs(rules, {"A": "RED BAG", "B": "BLUE BAG", "C": "HEART"}, limit=4)
    assert len(found) == 2
    assert found[0]["antecedent"] == "Red Bag"
    assert found[0]["consequent"] == "Blue Bag"
    assert found[0]["baskets"] == 13
    assert found[0]["confidence_pct"] == 60.0
    assert found[0]["lift"] == 2.5
    assert found[1]["antecedent_sku"] == "A"
    assert top_unique_pairs(rules.iloc[:0], {}, limit=3) == []