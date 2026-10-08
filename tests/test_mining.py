import math
import pandas as pd
from basketlens.mining import RuleConfig, mine_pairwise, recommend


def baskets_for_test():
    transactions = {"1":["A","B"], "2":["A","B"], "3":["A","C"],
                    "4":["B","C"], "5":["A","B"], "6":["A"]}
    baskets = pd.DataFrame({"basket_id":list(transactions)})
    items = pd.DataFrame([{"basket_id":ident, "stock_code":sku}
                          for ident,values in transactions.items() for sku in values])
    return baskets, items


def test_pairwise_support_denominator_includes_single_item_baskets():
    baskets, items = baskets_for_test()
    cfg = RuleConfig(algorithm="pairwise", min_support=0.01, max_products=3,
                     min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0)
    rules, meta = mine_pairwise(baskets, items, cfg)
    ab = rules.loc[rules["antecedent"].eq("A") & rules["consequent"].eq("B")].iloc[0]
    assert meta["train_baskets"] == 6
    assert int(ab.joint_count) == 3
    assert math.isclose(ab.support, 0.5)
    assert math.isclose(ab.confidence, 3/5)
    assert math.isclose(ab.lift, (3/5) / (4/6))
    assert len(rules.loc[rules["antecedent"].eq("B") & rules["consequent"].eq("A")]) == 1


def test_recommendations_only_unseen_products():
    baskets, items = baskets_for_test()
    rules, _ = mine_pairwise(baskets, items, RuleConfig(min_support=.01, max_products=3,
                                min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0))
    result = recommend(rules, ["A"])
    assert set(result["consequent"]) == {"B", "C"}
    assert recommend(rules, ["A","B","C"]).empty
    assert recommend(rules, []).empty


def test_candidate_coverage_describes_top_product_cap():
    baskets, items = baskets_for_test()
    rules, meta = mine_pairwise(baskets, items, RuleConfig(min_support=.01, max_products=2,
                                min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0))
    assert meta["training_products_all"] == 3
    assert meta["candidate_products"] == 2
    assert 0 <= meta["candidate_pair_coverage"] <= meta["candidate_basket_coverage"] <= 1
    assert len(rules) > 0
