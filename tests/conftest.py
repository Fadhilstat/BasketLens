"""Synthetic test fixtures ONLY. Not business results or a replacement for UCI data."""
from __future__ import annotations
from datetime import datetime, timedelta
import pandas as pd
import pytest
from basketlens.ingestion import standardize_columns

@pytest.fixture
def raw_fixture() -> pd.DataFrame:
    rows = []
    start = datetime(2010, 1, 1)
    basket_sets = ["AB", "AB", "AC", "BC", "AB", "AB", "AC", "AB", "BC", "AB"]
    for i, products in enumerate(basket_sets):
        for stock in products:
            rows.append({"Invoice": f"{100001+i}", "StockCode": stock,
                         "Description": {"A":"Mug", "B":"Tray", "C":"Plate"}[stock],
                         "Quantity": 1, "InvoiceDate": start + timedelta(days=i),
                         "Price": 2.0, "Customer ID": None, "Country": "United Kingdom"})
    rows += [
        {"Invoice": "C100099", "StockCode": "A", "Description": "Mug", "Quantity": -1,
         "InvoiceDate": start, "Price": 2, "Customer ID": None, "Country": "United Kingdom"},
        {"Invoice": "100100", "StockCode": "POST", "Description": "POSTAGE", "Quantity": 1,
         "InvoiceDate": start, "Price": 2, "Customer ID": None, "Country": "United Kingdom"},
        {"Invoice": "100101", "StockCode": "A", "Description": "Mug", "Quantity": 1,
         "InvoiceDate": start, "Price": 0, "Customer ID": None, "Country": "United Kingdom"},
        {"Invoice": "100102", "StockCode": "B", "Description": "Tray", "Quantity": -2,
         "InvoiceDate": start, "Price": 3, "Customer ID": None, "Country": "United Kingdom"},
    ]
    return standardize_columns(pd.DataFrame(rows), "Year 2009-2010")
