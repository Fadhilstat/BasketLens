"""A reviewer-friendly association example chosen only with training-era evidence.

Holdout measurements are joined after selection. This is descriptive research,
not a revenue, conversion, profit, or causal effect estimate.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import math

import pandas as pd


@dataclass(frozen=True)
class CaseEvidence:
    antecedent: str
    consequent: str
    antecedent_name: str
    consequent_name: str
    train_joint_count: int
    train_confidence: float
    train_lift: float
    holdout_fires: int
    holdout_hits: int
    holdout_confidence: float | None
    holdout_lift: float | None


def select_portfolio_case(
    rules: pd.DataFrame, evaluation: pd.DataFrame, names: dict[str, str]
) -> CaseEvidence | None:
    """Select the top one-to-one rule using training counts, confidence and lift.

    Chronologically later outcomes are never used to select or rank examples.
    Return None when the input does not contain a trustworthy case.
    """
    required_rules = {"antecedent", "consequent", "joint_count", "confidence", "lift"}
    required_eval = {"antecedent", "consequent", "fires", "hits",
                     "holdout_confidence", "holdout_lift"}
    if (rules.empty or evaluation.empty or not required_rules.issubset(rules.columns)
            or not required_eval.issubset(evaluation.columns)):
        return None
    eligible = rules.loc[
        ~rules["antecedent"].astype(str).str.contains("||", regex=False)
        & ~rules["consequent"].astype(str).str.contains("||", regex=False)
    ].copy()
    if eligible.empty:
        return None
    for column in ("joint_count", "confidence", "lift"):
        eligible[column] = pd.to_numeric(eligible[column], errors="coerce")
    eligible = eligible.loc[
        eligible["joint_count"].ge(1)
        & eligible["confidence"].between(0, 1)
        & eligible["lift"].ge(0)
        & eligible[["joint_count", "confidence", "lift"]].apply(
            lambda col: col.map(math.isfinite)).all(axis=1)
    ]
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["joint_count", "confidence", "lift", "antecedent", "consequent"],
        ascending=[False, False, False, True, True], kind="mergesort",
    ).iloc[0]
    left, right = str(chosen["antecedent"]), str(chosen["consequent"])
    later = evaluation.loc[
        evaluation["antecedent"].astype(str).eq(left)
        & evaluation["consequent"].astype(str).eq(right)
    ]
    if len(later) != 1:
        return None
    later_row = later.iloc[0]
    try:
        fires, hits = int(later_row["fires"]), int(later_row["hits"])
        if fires < 0 or hits < 0 or hits > fires:
            return None
        conf = float(later_row["holdout_confidence"])
        lift = float(later_row["holdout_lift"])
    except (TypeError, ValueError, OverflowError):
        return None
    if fires > 0 and (not math.isfinite(conf) or conf < 0 or conf > 1):
        return None
    if math.isfinite(lift) and lift < 0:
        return None
    return CaseEvidence(
        antecedent=left,
        consequent=right,
        antecedent_name=str(names.get(left, left)).strip(),
        consequent_name=str(names.get(right, right)).strip(),
        train_joint_count=int(chosen["joint_count"]),
        train_confidence=float(chosen["confidence"]),
        train_lift=float(chosen["lift"]),
        holdout_fires=fires,
        holdout_hits=hits,
        holdout_confidence=conf if fires > 0 else None,
        holdout_lift=lift if math.isfinite(lift) else None,
    )


def portfolio_case_html(case: CaseEvidence) -> str:
    """Escaped read-only narrative suitable for a public Streamlit Markdown panel."""
    left, right = escape(case.antecedent_name), escape(case.consequent_name)
    left_sku, right_sku = escape(case.antecedent), escape(case.consequent)
    later_pct = (f"{case.holdout_confidence:.1%}" if case.holdout_confidence is not None
                 else "No later firings")
    later_lift = f"{case.holdout_lift:.2f}x" if case.holdout_lift is not None else "N/A"
    return (
        '<section class="bl-decision-brief" aria-label="Analyst decision brief">'
        '<div class="bl-case-top"><div class="bl-case-eyebrow">'
        'CASE STUDY / CHOSEN FROM EARLIER BASKETS</div>'
        '<h3>An association worth testing, not a forecast</h3>'
        f'<p class="bl-case-names">{left} ({left_sku}) '
        f'<span aria-hidden="true">→</span> {right} ({right_sku})</p></div>'
        '<div class="bl-case-results">'
        f'<div><span>Earlier baskets together</span><strong>{case.train_joint_count:,}</strong></div>'
        f'<div><span>Earlier confidence / lift</span><strong>{case.train_confidence:.1%} / '
        f'{case.train_lift:.2f}x</strong></div>'
        f'<div><span>Later co-occurrence</span><strong>{case.holdout_hits:,} of '
        f'{case.holdout_fires:,}</strong></div>'
        f'<div><span>Later confidence / lift</span><strong>{later_pct} / '
        f'{later_lift}</strong></div></div>'
        '<p class="bl-case-caveat">Decision: check margin and stock, then consider '
        'a controlled placement or bundling experiment. Observed co-occurrence '
        'does not demonstrate incremental conversion, sales or profit.</p></section>'
    )
