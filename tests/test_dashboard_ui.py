"""M5 dashboard chrome renders real links, safe values and readable explanations."""
from basketlens.dashboard_ui import (
    SOURCE_URL, CODE_URL, dashboard_header, dashboard_intro,
    highlight_kpi_text, panel_title, study_status,
)


def test_header_uses_real_resources_and_is_accessible():
    page = dashboard_header("Dec 2009", "Dec 2011", public=True)
    assert "<h1>Basket<span>Lens</span></h1>" in page
    assert 'aria-label="Research resources"' in page
    assert 'aria-label="Open official UCI dataset"' in page
    assert SOURCE_URL in page and CODE_URL in page
    assert "Curated public research" in page
    assert page.count("href=") == 4
    assert "Welcome Back" not in page and "wallet" not in page.lower()


def test_header_escapes_source_metadata():
    markup = dashboard_header('<img src=x onerror="alert(1)">', "Dec 2011", True)
    assert "&lt;img" in markup
    assert '<img src=x' not in markup
    assert 'onerror="alert(1)"' not in markup


def test_intro_readable_and_rule_count_disclosed():
    public = dashboard_intro("Dec 2009", "Dec 2011", 1500)
    assert "Find the story in every basket" in public
    assert "1,500 training-selected rules" in public
    assert "2009" in public and "2011" in public
    local = dashboard_intro("Dec 2009", "Dec 2011", None)
    assert "Full verified analytics workspace" in local


def test_scope_line_is_honest_and_escaped():
    s = highlight_kpi_text(12, .25, country='<UK & Eire>')
    assert "12 eligible baskets" in s
    assert "25.0%" in s
    assert "&lt;UK &amp; Eire&gt;" in s
    assert "not proof of an effective promotion" in s
    empty = highlight_kpi_text(0, None, country="Nowhere")
    assert "No eligible baskets match" in empty


def test_panels_escape_metadata_and_status_has_no_fake_claims():
    panel = panel_title('<script>alert(1)</script>', "Data > 2020", overline="Trend")
    assert "&lt;script&gt;" in panel
    assert "&gt;" in panel
    assert "<script>" not in panel
    ribbon = study_status(40280, 1500)
    assert "40,280 historical baskets" in ribbon
    assert "1,500 rules to explore" in ribbon
    assert "Observational, not experimental" in ribbon


def test_design_is_responsive_and_respects_reduced_motion():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    css = (root / "app" / "assets" / "basketlens.css").read_text()
    assert "@media (max-width: 800px)" in css
    assert "@media (max-width: 480px)" in css
    assert "prefers-reduced-motion: reduce" in css
    assert ":focus-visible" in css
    assert "bl-resource-rail { display:none; }" in css
    assert "max-width: 100%" in css
    assert "backdrop-filter" not in css
    assert "\u2014" not in css