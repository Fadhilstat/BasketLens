"""Load official UCI workbooks or an exported CSV with source-row lineage."""
from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

SCHEMA_ALIASES = {
    "invoice": "invoice_no", "invoiceno": "invoice_no", "invoicenumber": "invoice_no",
    "stockcode": "stock_code", "description": "description", "quantity": "quantity",
    "invoicedate": "invoice_date", "price": "unit_price", "unitprice": "unit_price",
    "customerid": "customer_id", "country": "country",
}
REQUIRED = {"invoice_no", "stock_code", "description", "quantity", "invoice_date", "unit_price", "country"}


def standardize_columns(frame: pd.DataFrame, sheet: str) -> pd.DataFrame:
    """Normalize both Online Retail II year sheets, retaining immutable row positions."""
    new_names = {}
    for col in frame.columns:
        key = re.sub(r"[^a-z0-9]", "", str(col).lower())
        if key in SCHEMA_ALIASES:
            new_names[col] = SCHEMA_ALIASES[key]
    data = frame.rename(columns=new_names).copy()
    if data.columns.duplicated().any():
        raise ValueError(f"Duplicate canonical column in {sheet}")
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns in {sheet}: {', '.join(sorted(missing))}")
    if "customer_id" not in data:
        data["customer_id"] = pd.NA
    data["source_sheet"] = sheet
    data["source_row"] = range(2, len(data) + 2)
    return data[["invoice_no", "stock_code", "description", "quantity", "invoice_date",
                 "unit_price", "customer_id", "country", "source_sheet", "source_row"]]


def load_transactions(path: str | Path, max_rows_per_sheet: int | None = None) -> pd.DataFrame:
    """Load two annual sheets without confusing identical invoice numbers across sheets."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Input not found: {path}")
    if path.suffix.lower() == ".csv":
        return standardize_columns(pd.read_csv(path, nrows=max_rows_per_sheet, low_memory=False), "CSV")
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("Input must be .xlsx or .csv. Convert .xls to .xlsx first.")
    if path.suffix.lower() == ".xls":
        raise ValueError("Legacy .xls is not supported directly. Export as .xlsx or .csv.")
    with pd.ExcelFile(path, engine="openpyxl") as book:
        frames = [standardize_columns(pd.read_excel(book, sheet_name=name,
                          nrows=max_rows_per_sheet), name) for name in book.sheet_names]
    if not frames:
        raise ValueError("Excel workbook has no sheets")
    return pd.concat(frames, ignore_index=True)
