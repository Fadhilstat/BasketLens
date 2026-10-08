"""Auditable sale eligibility and conservative non-merchandise exclusions."""
from __future__ import annotations

import re
import numpy as np
import pandas as pd

SERVICE_CODES = frozenset({
    "POST", "DOT", "C2", "BANK CHARGES", "AMAZONFEE",
    "PADS", "CRUK", "ADJUST", "DCGSSBOY", "DCGSSGIRL"
})
SERVICE_DESCRIPTIONS = frozenset({
    "POSTAGE", "DOTCOM POSTAGE", "BANK CHARGES", "DISCOUNT", "MANUAL",
    "CARRIAGE", "AMAZON FEE"
})


def normalize_identifier(series: pd.Series) -> pd.Series:
    """Avoid float-formatted invoice/SKU strings while keeping codes like 85123A."""
    result = series.astype("string").str.strip().str.upper()
    result = result.str.replace(r"^(\d+)\.0$", r"\1", regex=True)
    return result.mask(result.isin(["", "NAN", "NONE", "NULL", "<NA>"]))


def clean_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return valid positive merchandise sale lines and exclusive rejection counts.

    Exact-looking duplicates are reported but not removed: repeated invoice lines
    can represent legitimate purchases. Customer IDs are not persisted.
    """
    if raw.empty:
        raise ValueError("Input has no transaction records")
    work = raw.copy()
    work["invoice_no"] = normalize_identifier(work["invoice_no"])
    work["stock_code"] = normalize_identifier(work["stock_code"])
    work["description"] = (work["description"].astype("string").str.strip()
                            .str.replace(r"\s+", " ", regex=True).str.upper())
    work["description"] = work["description"].mask(work["description"].isin(["", "NAN", "NONE", "NULL", "<NA>"]))
    work["country"] = work["country"].astype("string").str.strip().fillna("Unknown")
    work.loc[work["country"].eq(""), "country"] = "Unknown"
    work["quantity"] = pd.to_numeric(work["quantity"], errors="coerce")
    work["unit_price"] = pd.to_numeric(work["unit_price"], errors="coerce")
    work["invoice_date"] = pd.to_datetime(work["invoice_date"], errors="coerce")
    missing_customers = int(normalize_identifier(work["customer_id"]).isna().sum())
    duplicated_lines = int(work.duplicated(subset=["invoice_no", "stock_code", "description",
                                            "quantity", "invoice_date", "unit_price", "source_sheet"]).sum())
    is_service = work["stock_code"].isin(SERVICE_CODES) | work["description"].isin(SERVICE_DESCRIPTIONS)
    valid_quantity = pd.Series(np.isfinite(work["quantity"].to_numpy(dtype=float, na_value=np.nan)),
                               index=work.index) & work["quantity"].gt(0)
    valid_price = pd.Series(np.isfinite(work["unit_price"].to_numpy(dtype=float, na_value=np.nan)),
                            index=work.index) & work["unit_price"].gt(0)
    # Precedence makes the counts add up exactly to total records.
    cases = [
        work["invoice_no"].isna(),
        work["invoice_no"].fillna("").str.startswith("C"),
        work["invoice_date"].isna(),
        work["stock_code"].isna() | work["description"].isna(),
        ~valid_quantity.fillna(False),
        ~valid_price.fillna(False),
        is_service.fillna(False),
    ]
    labels = ["missing_invoice", "cancellation", "invalid_date", "missing_product",
              "nonpositive_quantity", "nonpositive_price", "non_merchandise"]
    work["quality_reason"] = np.select([c.fillna(False).to_numpy(dtype=bool) for c in cases],
                                        labels, default="valid_sale")
    counts = work["quality_reason"].value_counts().to_dict()
    report = {
        "input_rows": int(len(work)), "valid_rows": int(counts.get("valid_sale", 0)),
        "excluded_rows": int(len(work) - counts.get("valid_sale", 0)),
        "missing_customer_id_rows": missing_customers,
        "potential_exact_duplicate_rows": duplicated_lines,
        "reason_counts": {key: int(counts.get(key, 0)) for key in [*labels, "valid_sale"]},
        "policy": "Positive quantity, positive price, dated invoice, non-cancelled merchandise lines",
    }
    sales = work.loc[work["quality_reason"].eq("valid_sale")].copy()
    if sales.empty:
        raise ValueError("No valid merchandise lines after quality filters")
    sales["basket_id"] = sales["source_sheet"].astype(str) + "::" + sales["invoice_no"].astype(str)
    sales["line_revenue_gbp"] = sales["quantity"] * sales["unit_price"]
    sales["source_row"] = sales["source_row"].astype("int64")
    return sales[["basket_id", "invoice_no", "stock_code", "description", "quantity",
                  "unit_price", "invoice_date", "country", "line_revenue_gbp",
                  "source_sheet", "source_row"]].reset_index(drop=True), report


def build_baskets(sales: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Deduplicate SKUs per invoice for support without dropping single-item baskets."""
    header = sales.groupby("basket_id", sort=False).agg(
        invoice_date=("invoice_date", "min"), country=("country", "first"),
        basket_revenue_gbp=("line_revenue_gbp", "sum"),
        units=("quantity", "sum"), item_count=("stock_code", "nunique"),
    ).reset_index()
    inconsistencies = sales.groupby("basket_id", sort=False).agg(
        date_count=("invoice_date", "nunique"), country_count=("country", "nunique")
    )
    items = sales.groupby(["basket_id", "stock_code"], as_index=False, sort=False).agg(
        quantity=("quantity", "sum"), line_revenue_gbp=("line_revenue_gbp", "sum"),
        description=("description", "first")
    )
    report = {
        "basket_count": int(len(header)),
        "single_item_baskets": int(header["item_count"].eq(1).sum()),
        "date_inconsistent_invoices": int(inconsistencies["date_count"].gt(1).sum()),
        "country_inconsistent_invoices": int(inconsistencies["country_count"].gt(1).sum()),
    }
    return header, items, report


def quarantine_inconsistent_baskets(sales: pd.DataFrame, policy: str = "fail") -> tuple[pd.DataFrame, dict]:
    """Handle incoherent source invoices before building basket associations.

    ``fail`` prevents accidental inclusion; ``quarantine`` drops every line of
    each inconsistent invoice and reports the exact loss of analytical coverage.
    Neither policy silently repairs timestamps or country assignments.
    """
    if policy not in {"fail", "quarantine"}:
        raise ValueError("Inconsistent basket policy must be 'fail' or 'quarantine'")
    grouped = sales.groupby("basket_id", sort=False).agg(
        date_count=("invoice_date", "nunique"), country_count=("country", "nunique")
    )
    date_bad = grouped["date_count"].gt(1)
    country_bad = grouped["country_count"].gt(1)
    bad_ids = grouped.index[date_bad | country_bad]
    removed = sales["basket_id"].isin(bad_ids)
    report = {
        "date_inconsistent_source_baskets": int(date_bad.sum()),
        "country_inconsistent_source_baskets": int(country_bad.sum()),
        "quarantined_source_baskets": int(len(bad_ids)) if policy == "quarantine" else 0,
        "quarantined_rows": int(removed.sum()) if policy == "quarantine" else 0,
        "policy": policy,
    }
    if len(bad_ids) and policy == "fail":
        raise ValueError(f"{len(bad_ids)} source invoices have conflicting dates/countries. "
                         "Inspect inputs or explicitly use --inconsistent-policy quarantine.")
    if removed.any():
        sales = sales.loc[~removed].copy()
        if sales.empty:
            raise ValueError("All eligible baskets were quarantined; cannot continue")
    return sales, report
