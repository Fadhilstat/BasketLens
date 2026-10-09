"""Aggregations for explainable, privacy-conscious retail dashboards."""
from __future__ import annotations
import pandas as pd


def summaries(sales: pd.DataFrame, baskets: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build SKU, country and month facts without persisting customer identifiers."""
    catalog = sales.groupby("stock_code", sort=False).agg(
        description=("description", lambda s: s.value_counts().index[0]),
        units_sold=("quantity", "sum"),
        sales_gbp=("line_revenue_gbp", "sum"),
        typical_price_gbp=("unit_price", "median"),
        basket_count=("basket_id", "nunique"),
    ).reset_index().sort_values("sales_gbp", ascending=False)
    country = baskets.groupby("country", sort=False).agg(
        baskets=("basket_id", "count"), sales_gbp=("basket_revenue_gbp", "sum"),
        units=("units", "sum"), avg_distinct_items=("item_count", "mean")
    ).reset_index().sort_values("sales_gbp", ascending=False)
    month_baskets = baskets.assign(month=baskets["invoice_date"].dt.to_period("M").astype(str))
    monthly = month_baskets.groupby("month", sort=True).agg(
        baskets=("basket_id", "count"), sales_gbp=("basket_revenue_gbp", "sum"),
        units=("units", "sum"), avg_distinct_items=("item_count", "mean")
    ).reset_index()
    monthly_country = month_baskets.groupby(["month", "country"], sort=True).agg(
        baskets=("basket_id", "count"), sales_gbp=("basket_revenue_gbp", "sum"),
        units=("units", "sum"), avg_distinct_items=("item_count", "mean")
    ).reset_index()
    return {"products": catalog, "countries": country, "monthly": monthly,
            "monthly_country": monthly_country}
