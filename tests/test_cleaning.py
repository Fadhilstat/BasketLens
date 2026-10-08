import pandas as pd
from basketlens.ingestion import standardize_columns
from basketlens.cleaning import clean_transactions, build_baskets


def test_uci_year_schema_aliases_and_invoice_identity(raw_fixture):
    assert "invoice_no" in raw_fixture.columns
    assert "unit_price" in raw_fixture.columns
    sales, q = clean_transactions(raw_fixture)
    baskets, items, checks = build_baskets(sales)
    assert q["input_rows"] == 24
    assert q["valid_rows"] == 20
    assert q["reason_counts"]["cancellation"] == 1
    assert q["reason_counts"]["non_merchandise"] == 1
    assert q["reason_counts"]["nonpositive_quantity"] == 1
    assert q["reason_counts"]["nonpositive_price"] == 1
    assert sum(q["reason_counts"].values()) == q["input_rows"]
    assert q["missing_customer_id_rows"] == len(raw_fixture)
    assert len(baskets) == 10
    assert len(items) == 20
    assert baskets["item_count"].eq(2).all()
    assert checks["date_inconsistent_invoices"] == 0
    assert "customer_id" not in sales
    assert baskets["basket_revenue_gbp"].sum() == 40.0


def test_invoice_code_collisions_are_namespaced(raw_fixture):
    duplicate = raw_fixture.iloc[:2].copy()
    duplicate["source_sheet"] = "Year 2010-2011"
    both = pd.concat([raw_fixture, duplicate], ignore_index=True)
    sales, _ = clean_transactions(both)
    baskets, _, _ = build_baskets(sales)
    assert len(baskets) == 11
    assert "Year 2009-2010::100001" in set(baskets["basket_id"])
    assert "Year 2010-2011::100001" in set(baskets["basket_id"])


def test_missing_required_fields_rejected():
    try:
        standardize_columns(pd.DataFrame({"Invoice": [1]}), "bad")
        raise AssertionError("Should reject incomplete schema")
    except ValueError as error:
        assert "Missing columns" in str(error)
