"""Real mlxtend FP-Growth integration, enabled when the package is installed.

The toy baskets are synthetic test data; no source-transaction claim is made.
"""
import math

import pandas as pd
import pytest

pytest.importorskip("mlxtend")

from basketlens.mining import RuleConfig, mine_fpgrowth, mine_pairwise


def test_fpgrowth_emits_multi_product_rules_and_matches_pairwise_math():
    cart = {
        "1": "ABC", "2": "ABC", "3": "ABC", "4": "AB",
        "5": "AC", "6": "BC", "7": "A", "8": "B"
    }
    baskets = pd.DataFrame({"basket_id": list(cart)})
    items = pd.DataFrame([(invoice, sku) for invoice, skus in cart.items() for sku in skus],
                         columns=["basket_id", "stock_code"])
    cfg = RuleConfig(algorithm="fpgrowth", max_products=3, min_item_count=1,
                     min_joint_count=1, min_support=.125, min_confidence=0,
                     min_lift=0, max_itemset_len=3)
    rules, meta = mine_fpgrowth(baskets, items, cfg)
    assert meta["candidate_products"] == 3
    ab_to_c = rules.loc[(rules["antecedent"] == "A||B") &
                        (rules["consequent"] == "C")].iloc[0]
    assert ab_to_c["joint_count"] == 3
    assert math.isclose(ab_to_c["support"], 3/8)
    assert math.isclose(ab_to_c["confidence"], 3/4)
    baseline, _ = mine_pairwise(baskets, items, RuleConfig(
        algorithm="pairwise", max_products=3, min_item_count=1,
        min_joint_count=1, min_support=.125, min_confidence=0, min_lift=0))
    ab_fpgrowth = rules.loc[(rules["antecedent"] == "A") & (rules["consequent"] == "B")].iloc[0]
    ab_pairwise = baseline.loc[(baseline["antecedent"] == "A") &
                               (baseline["consequent"] == "B")].iloc[0]
    for field in ("joint_count", "support", "confidence", "lift", "leverage"):
        assert math.isclose(ab_fpgrowth[field], ab_pairwise[field])
