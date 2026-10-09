"""Stable data-driven consulting narrative, without holdout selection leakage."""
import pandas as pd

from basketlens.portfolio_case import portfolio_case_html, select_portfolio_case


def _frames():
    rules = pd.DataFrame([
        {"antecedent": "A", "consequent": "B", "joint_count": 20,
         "confidence": 0.64, "lift": 4.4},
        {"antecedent": "B", "consequent": "A", "joint_count": 20,
         "confidence": 0.78, "lift": 4.4},
        {"antecedent": "C", "consequent": "D", "joint_count": 8,
         "confidence": 0.98, "lift": 15.0},
        {"antecedent": "A||B", "consequent": "C", "joint_count": 1000,
         "confidence": 0.99, "lift": 44.0},
    ])
    evaluation = pd.DataFrame([
        {"antecedent": "A", "consequent": "B", "fires": 10, "hits": 2,
         "holdout_confidence": .2, "holdout_lift": 1.2},
        {"antecedent": "B", "consequent": "A", "fires": 15, "hits": 11,
         "holdout_confidence": 11 / 15, "holdout_lift": 4.3},
        {"antecedent": "C", "consequent": "D", "fires": 1000, "hits": 950,
         "holdout_confidence": .95, "holdout_lift": 7.0},
    ])
    return rules, evaluation


def test_training_only_selection_does_not_cherry_pick_holdout():
    rules, later = _frames()
    case = select_portfolio_case(rules, later, {"B": "Product B", "A": "Product A"})
    assert case.antecedent == "B" and case.consequent == "A"
    assert case.train_joint_count == 20
    assert case.holdout_fires == 15 and case.holdout_hits == 11


def test_bad_input_and_zero_holdout():
    rules, later = _frames()
    assert select_portfolio_case(rules, pd.DataFrame(), {}) is None
    bad = later.copy()
    bad.loc[bad["antecedent"].eq("B"), "hits"] = 100
    assert select_portfolio_case(rules, bad, {}) is None
    zero = later.copy()
    zero.loc[zero["antecedent"].eq("B"), ["fires", "hits"]] = 0
    case = select_portfolio_case(rules, zero, {})
    assert case and case.holdout_confidence is None


def test_escaping_and_no_false_impact_claim():
    rules, later = _frames()
    case = select_portfolio_case(rules, later, {"A": '<script>alert("a")</script>',
                                                     "B": "Bag & Basket"})
    html = portfolio_case_html(case)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "Bag &amp; Basket" in html
    assert "11 of 15" in html
    assert "73.3%" in html
    assert "does not demonstrate incremental conversion, sales or profit" in html


def test_no_eligible_rules():
    rules, later = _frames()
    assert select_portfolio_case(pd.DataFrame(), later, {}) is None
    invalid = rules.copy()
    invalid.loc[:, "joint_count"] = -1
    assert select_portfolio_case(invalid, later, {}) is None
