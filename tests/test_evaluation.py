from datetime import datetime, timedelta
import pandas as pd
import pytest
from basketlens.evaluation import temporal_split, evaluate_rules
from basketlens.mining import RuleConfig, mine_pairwise


def test_temporal_split_never_leaks_same_timestamp():
    dates = [datetime(2010,1,1) + timedelta(days=i//2) for i in range(10)]
    baskets = pd.DataFrame({"basket_id":[str(i) for i in range(10)], "invoice_date":dates})
    train, test, cutoff = temporal_split(baskets, 0.8)
    assert len(train) == 8
    assert len(test) == 2
    assert train.invoice_date.max() < cutoff <= test.invoice_date.min()
    assert set(train.basket_id).isdisjoint(test.basket_id)


def test_temporal_cutoff_requires_multiple_times():
    baskets = pd.DataFrame({"basket_id":["1","2","3","4"],
                            "invoice_date":pd.to_datetime(["2010-01-01"]*4)})
    with pytest.raises(ValueError, match="Cannot split"):
        temporal_split(baskets)


def test_holdout_confidence_and_lift_are_conditional_not_uplift():
    train = pd.DataFrame({"basket_id":["t1", "t2", "t3", "t4"]})
    train_items = pd.DataFrame({"basket_id":["t1","t1","t2","t2","t3","t4"],
                                "stock_code":["A","B","A","B","A","C"]})
    rules, _ = mine_pairwise(train, train_items, RuleConfig(min_support=.01, max_products=3,
                              min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0))
    holdout = pd.DataFrame({"basket_id":["h1", "h2"]})
    items = pd.DataFrame({"basket_id":["h1","h1","h2"], "stock_code":["A","B","C"]})
    scored = evaluate_rules(rules, holdout, items)
    row = scored.loc[scored.antecedent.eq("A") & scored.consequent.eq("B")].iloc[0]
    assert row.fires == 1
    assert row.hits == 1
    assert row.holdout_confidence == 1
    assert row.holdout_baseline_support == .5
    assert row.holdout_lift == 2
