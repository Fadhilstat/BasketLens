"""Small, testable presentation helpers for the BasketLens research interface.

These helpers only transform recorded observations. No causal effect is inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class BasketSnapshot:
    """Eligible positive-sale baskets, not reconciled net revenue."""

    baskets: int
    sales_gbp: float
    average_gbp: float | None
    multi_product_share: float | None


def snapshot_from_rollup(rollup: pd.DataFrame) -> BasketSnapshot:
    """Calculate visible sales KPIs from a country-filtered basket aggregate."""
    required = {"basket_count", "sales_gbp", "item_count"}
    if not required.issubset(rollup.columns):
        raise ValueError(f"Missing basket rollup columns: {sorted(required - set(rollup.columns))}")
    if rollup.empty:
        return BasketSnapshot(baskets=0, sales_gbp=0.0, average_gbp=None,
                              multi_product_share=None)
    if not rollup["basket_count"].map(lambda x: math.isfinite(float(x)) and x >= 0).all():
        raise ValueError("Invalid basket count")
    if not rollup["sales_gbp"].map(lambda x: math.isfinite(float(x)) and x >= 0).all():
        raise ValueError("Invalid positive sale amount")
    total = int(rollup["basket_count"].sum())
    sales = float(rollup["sales_gbp"].sum())
    multi = int(rollup.loc[rollup["item_count"].ge(2), "basket_count"].sum())
    return BasketSnapshot(baskets=total, sales_gbp=sales,
                          average_gbp=sales / total if total else None,
                          multi_product_share=multi / total if total else None)


def product_name(value: str, lookup: dict[str, str], limit: int | None = None) -> str:
    """Show product labels instead of relying on opaque stock codes."""
    skus = str(value).split("||")
    labels = []
    for sku in skus:
        description = str(lookup.get(sku, "Unknown product")).strip()
        if limit is not None and len(description) > limit:
            description = description[:max(0, limit - 1)].rstrip() + "…"
        labels.append(f"{description} ({sku})")
    return " + ".join(labels)


def filter_rule_view(rules: pd.DataFrame, lookup: dict[str, str], *,
                     minimum_lift: float = 1.0, minimum_joint: int = 1,
                     search: str = "") -> pd.DataFrame:
    """Filter published rules without fitting or re-ranking the analytical model.

    Search is literal, case insensitive and includes both product codes and names.
    Display order is determined by training co-occurrence, not holdout outcomes.
    """
    if minimum_joint < 1 or minimum_lift < 0:
        raise ValueError("Invalid rule display filters")
    filtered = rules.loc[rules["lift"].ge(minimum_lift) &
                         rules["joint_count"].ge(minimum_joint)].copy()
    if filtered.empty:
        return filtered.assign(pair_label=pd.Series(dtype=str),
                               antecedent_label=pd.Series(dtype=str),
                               consequent_label=pd.Series(dtype=str))
    filtered["antecedent_label"] = filtered["antecedent"].astype(str).map(
        lambda code: product_name(code, lookup))
    filtered["consequent_label"] = filtered["consequent"].astype(str).map(
        lambda code: product_name(code, lookup))
    filtered["pair_label"] = (filtered["antecedent_label"] + " + " +
                              filtered["consequent_label"])
    query = search.strip()
    if query:
        readable_match = filtered["pair_label"].str.contains(query, case=False, regex=False, na=False)
        raw_match = (filtered["antecedent"].astype(str).str.contains(query, case=False, regex=False, na=False) |
                     filtered["consequent"].astype(str).str.contains(query, case=False, regex=False, na=False))
        filtered = filtered.loc[readable_match | raw_match].copy()
    return filtered.sort_values(["joint_count", "confidence", "lift", "antecedent", "consequent"],
                                ascending=[False, False, False, True, True],
                                kind="mergesort").reset_index(drop=True)


def example_basket_seed(rules: pd.DataFrame, allowed_skus: list[str]) -> str | None:
    """Pick a frequent earlier-period antecedent, never using holdout labels."""
    if rules.empty or not allowed_skus:
        return None
    available = set(allowed_skus)
    ordered = rules.sort_values(["joint_count", "antecedent"],
                                ascending=[False, True], kind="mergesort")
    for antecedent in ordered["antecedent"].astype(str):
        first = antecedent.split("||")[0]
        if first in available:
            return first
    return None


def compact_rule_table(view: pd.DataFrame) -> pd.DataFrame:
    """Return human-oriented table columns with explicit historical units."""
    if view.empty:
        return pd.DataFrame(columns=["Earlier basket contains", "Also contains",
                                     "Purchased together", "Confidence (%)", "Lift (x)"])
    table = view[["antecedent_label", "consequent_label", "joint_count",
                  "confidence", "lift"]].copy()
    table.columns = ["Earlier basket contains", "Also contains",
                     "Purchased together", "Confidence (%)", "Lift (x)"]
    table["Confidence (%)"] = table["Confidence (%)"].astype(float) * 100
    return table


def lift_meaning(lift: float) -> str:
    """Explain comparative co-occurrence while avoiding revenue/uplift claims."""
    if not math.isfinite(float(lift)) or lift < 0:
        return "Lift is unavailable for this observation."
    if math.isclose(lift, 1.0, abs_tol=0.01):
        return "These products appeared together about as often as expected from their individual frequencies."
    if lift > 1:
        return (f"These products appeared together about {lift:.2f} times as often as expected "
                "from their individual frequencies in earlier orders.")
    return (f"These products appeared together about {lift:.2f} times as often as expected "
            "from their individual frequencies, which is less frequent than the baseline.")


QUALITY_REASONS = {
    "cancellation": "Cancelled or returned item",
    "missing_product": "Missing product detail",
    "non_merchandise": "Postage or non-product service",
    "nonpositive_price": "Price not above zero",
    "nonpositive_quantity": "Quantity not above zero",
    "invalid_date": "Date could not be read",
    "missing_invoice": "Invoice number missing",
    "valid_sale": "Eligible positive-sale item",
}


def quality_reason_label(reason: str) -> str:
    """Friendly, accurate data-quality labels for a nontechnical audience."""
    return QUALITY_REASONS.get(reason, reason.replace("_", " ").capitalize())