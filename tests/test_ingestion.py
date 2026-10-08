"""Round-trip legacy source column names through multi-year Excel ingestion."""
import pandas as pd
from basketlens.ingestion import load_transactions


def test_two_sheet_excel_ingestion(tmp_path):
    old = pd.DataFrame({
        "Invoice":[123456], "StockCode":["12345A"], "Description":["VASE"],
        "Quantity":[2], "InvoiceDate":["2009-12-02 12:10:00"],
        "Price":[3.0], "Customer ID":[30001], "Country":["United Kingdom"]
    })
    new = pd.DataFrame({
        "Invoice":[123456], "StockCode":["56789"], "Description":["CUP"],
        "Quantity":[1], "InvoiceDate":["2010-12-02 12:10:00"],
        "Price":[7.0], "Customer ID":[None], "Country":["Germany"]
    })
    path = tmp_path / "legacy_example.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        old.to_excel(writer, sheet_name="Year 2009-2010", index=False)
        new.to_excel(writer, sheet_name="Year 2010-2011", index=False)
    rows = load_transactions(path)
    assert len(rows) == 2
    assert rows["source_sheet"].nunique() == 2
    assert set(rows["source_row"]) == {2}
    assert set(rows["stock_code"].astype(str)) == {"12345A", "56789"}
