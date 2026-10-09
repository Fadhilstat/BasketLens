"""Small, escaped HTML view helpers for the BasketLens research dashboard.

They carry presentation only. All values originate from the validated analytics
snapshot. There are no synthetic KPI claims or decorative fake controls.
"""
from __future__ import annotations

from html import escape
from math import isfinite
from typing import Any

SOURCE_URL = "https://archive.ics.uci.edu/dataset/502/online+retail+ii"
CODE_URL = "https://github.com/Fadhilstat/BasketLens"
METHOD_URL = CODE_URL + "/blob/main/docs/methodology.md"


def _safe(value: Any) -> str:
    return escape(str(value), quote=True)


def _symbol(which: str, size: int = 20) -> str:
    """Tiny, accessible-hidden SVG symbols. No icon fonts or external request."""
    shapes = {
        "basket": '<path d="M4 10h16l-2 10H6L4 10Z"/><path d="m8 10 4-7 4 7M9 14v3m6-3v3"/>',
        "receipt": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6M9 12h6"/>',
        "chart": '<path d="M4 20V5M4 20h16"/><path d="m7 15 4-5 3 3 5-7"/>',
        "layers": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 9h8M8 13h8M8 17h4"/>',
        "link": '<path d="M10 13a5 5 0 0 0 7.1 0l2-2A5 5 0 0 0 12 4l-1.2 1.2"/>'
                '<path d="M14 11a5 5 0 0 0-7.1 0l-2 2A5 5 0 0 0 12 20l1.2-1.2"/>',
        "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/>'
                '<path d="M4 17a2.5 2.5 0 0 1 2.5-2.5H20"/>',
        "github": '<path d="M9 19c-4 1-4-2-6-2m12 4v-3.1a2.7 2.7 0 0 0-.8-2.1'
                  ' /><path d="M9 21v-3.1a2.7 2.7 0 0 1 .8-2.1C6.3 15.4 5 13.8 5 11'
                  'c0-1 .3-1.8 1-2.5-.3-1.1-.2-2.1 0-3 0 0 1.2-.2 3 1.5a10 10 0 0 1 6 0'
                  'c1.8-1.7 3-1.5 3-1.5.2.9.3 1.9 0 3 .7.7 1 1.5 1 2.5 0 2.8-1.3 4.4-4.8 4.8"/>',
    }
    if which not in shapes:
        raise ValueError("Unsupported icon")
    return (f'<svg aria-hidden="true" width="{int(size)}" height="{int(size)}" '
            'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round">' + shapes[which] + '</svg>')


def dashboard_header(start: str, end: str, public: bool) -> str:
    """A single, flowing header with real accessible links, without overlay rails."""
    mode = "Curated public research" if public else "Local analyst workspace"
    return (
        '<header class="bl-topbar">'
        '<div class="bl-brand">'
        '<span class="bl-brand-mark">' + _symbol("basket", 23) + '</span>'
        '<div class="bl-brand-copy"><h1>Basket<span>Lens</span></h1>'
        '<small>Retail intelligence</small></div></div>'
        '<div class="bl-topbar-right">'
        f'<span class="bl-mode-dot">{_safe(mode)}</span>'
        '<nav class="bl-header-links" aria-label="Research resources">'
        f'<a class="bl-text-link" href="{SOURCE_URL}" target="_blank" '
        'rel="noopener noreferrer" aria-label="Open official UCI dataset">Dataset</a>'
        f'<a class="bl-text-link" href="{METHOD_URL}" target="_blank" '
        'rel="noopener noreferrer" aria-label="Open research methodology">Method</a>'
        f'<a class="bl-link-button" href="{CODE_URL}" target="_blank" '
        'rel="noopener noreferrer" aria-label="Open project source code">GitHub '
        + _symbol("github", 16) + '</a>'
        '</nav></div></header>'
    )


def dashboard_intro(start: str, end: str, public_rule_count: int | None) -> str:
    scope = (f"A focused view of {public_rule_count:,} training-selected rules" if public_rule_count is not None
             else "Full verified analytics workspace")
    return (
        '<section class="bl-intro-hero">'
        '<div><div class="bl-overline">Research dashboard <span class="bl-overline-sep"></span> '
        'Historical retail</div>'
        '<h2>Find the story in every basket.</h2>'
        '<p>Understand the sales picture, see which products travel together, '
        'and investigate the evidence behind each pairing.</p></div>'
        '<div class="bl-intro-side"><span class="bl-period-symbol">' + _symbol("chart", 18) + '</span>'
        f'<div><strong>{_safe(start)} - {_safe(end)}</strong><small>{_safe(scope)}</small></div></div>'
        '</section>'
    )


def study_status(valid_baskets: int, shown_rules: int | None) -> str:
    rule_message = f"{shown_rules:,} rules to explore" if shown_rules is not None else "Complete analysis"
    return (
        '<div class="bl-research-ribbon">'
        '<span class="bl-research-dot" aria-hidden="true"></span>'
        f'<span>{valid_baskets:,} historical baskets</span><i aria-hidden="true"></i>'
        f'<span>{_safe(rule_message)}</span><i aria-hidden="true"></i>'
        '<span>Observational, not experimental</span></div>'
    )


def panel_title(title: str, description: str, *, overline: str = "") -> str:
    prefix = f'<span class="bl-panel-overline">{_safe(overline)}</span>' if overline else ""
    return (f'<div class="bl-panel-heading">{prefix}<h3>{_safe(title)}</h3>'
            f'<p>{_safe(description)}</p></div>')


def highlight_kpi_text(baskets: int, share: float | None, *, country: str) -> str:
    """Unambiguous scope: this is observational basket composition, not uplift."""
    if baskets < 1 or share is None:
        message = "No eligible baskets match this country selection. Try another location."
    else:
        message = (f"Across {baskets:,} eligible baskets in {country}, {share:.1%} "
                   "contained two or more distinct products. That is a useful starting "
                   "point for investigating pairings, not proof of an effective promotion.")
    return (f'<aside class="bl-context-note"><span class="bl-context-icon">'
            + _symbol("receipt", 21) + '</span><div><strong>What the numbers say</strong>'
            f'<p>{_safe(message)}</p></div></aside>')


def pairing_cards(items: list[dict]) -> str:
    """Render trustworthy pair highlights using escaped text and recorded metrics."""
    if not items:
        return '<div class="bl-pair-grid bl-pair-grid--empty"></div>'
    cards = []
    for number, row in enumerate(items, start=1):
        left, right = _safe(row["antecedent"]), _safe(row["consequent"])
        left_code, right_code = _safe(row["antecedent_sku"]), _safe(row["consequent_sku"])
        count = int(row["baskets"])
        confidence = float(row["confidence_pct"])
        lift = float(row["lift"])
        if count < 0 or not (isfinite(confidence) and 0 <= confidence <= 100) or not (isfinite(lift) and lift >= 0):
            raise ValueError("Invalid rule metrics for the card view")
        cards.append(
            '<article class="bl-pair-card" role="listitem">'
            f'<div class="bl-pair-label">PAIR {number:02d}</div>'
            '<div class="bl-pair-title">'
            f'{left} <span class="bl-pair-plus">+</span> {right}</div>'
            '<div class="bl-pair-metrics">'
            f'<span><strong>{count:,}</strong> baskets together</span>'
            f'<span><strong>{lift:.2f}x</strong> lift</span></div>'
            f'<p class="bl-pair-caption">{confidence:.1f}% of earlier baskets with '
            f'{left} ({left_code}) also contained {right} ({right_code}).</p>'
            '</article>'
        )
    return '<div class="bl-pair-grid" role="list">' + ''.join(cards) + '</div>'