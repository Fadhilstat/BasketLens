"""All inputs are synthetic fixtures, not observed UCI business results."""
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from basketlens.cleaning import clean_transactions, quarantine_inconsistent_baskets
from basketlens.ingestion import standardize_columns


def test_conflicting_invoice_fail_closed_or_explicit_quarantine(raw_fixture):
    conflicting = raw_fixture.iloc[:2].copy()
    conflicting.loc[conflicting.index[-1], "invoice_date"] += timedelta(minutes=1)
    blended = pd.concat([raw_fixture, conflicting], ignore_index=True)
    sales, quality = clean_transactions(blended)
    assert quality["valid_rows"] == 22
    with pytest.raises(ValueError, match="source invoices have conflicting dates"):
        quarantine_inconsistent_baskets(sales)
    clean, report = quarantine_inconsistent_baskets(sales, policy="quarantine")
    # Original 2 matching rows plus the 2 replayed rows are removed together.
    assert report["date_inconsistent_source_baskets"] == 1
    assert report["quarantined_source_baskets"] == 1
    assert report["quarantined_rows"] == 4
    assert len(clean) == 18


def test_nonfinite_price_and_quantity_cannot_pollute_sales():
    frame = pd.DataFrame({
        "Invoice": ["1001", "1002", "1003", "1004"],
        "StockCode": ["A", "B", "C", "D"],
        "Description": ["Mug", "Tray", "Plate", "Vase"],
        "Quantity": [1, np.inf, 2, 1], "InvoiceDate": ["2010-01-02"] * 4,
        "Price": [2, 3, np.inf, 4], "Customer ID": [None] * 4,
        "Country": ["UK"] * 4,
    })
    sales, report = clean_transactions(standardize_columns(frame, "one-year"))
    assert len(sales) == 2
    assert report["reason_counts"]["nonpositive_quantity"] == 1
    assert report["reason_counts"]["nonpositive_price"] == 1
    assert np.isfinite(sales["line_revenue_gbp"]).all()
