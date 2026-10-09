"""M5.4 regression checks for the quality view, typography and single CSS source."""
from pathlib import Path

from basketlens.dashboard_ui import quality_pipeline

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "app/assets/basketlens.css").read_text(encoding="utf-8")
APP = (ROOT / "app/streamlit_app.py").read_text(encoding="utf-8")
SMOKE = (ROOT / "scripts/browser_smoke.py").read_text(encoding="utf-8")


def test_quality_stages_are_real_ordered_content():
    html = quality_pipeline()
    assert html.startswith('<ol class="bl-flow" aria-label="Validation sequence">')
    assert html.count("<li>") == 5
    assert html.count("</li>") == 5
    for label in ("Invoice records", "Eligibility checks", "One basket per invoice",
                  "Rules from earlier orders", "Check against later orders"):
        assert label in html
    assert "href=" not in html and "onclick=" not in html


def test_readable_quality_metrics_and_scoped_css():
    assert 'with st.container(key="quality_kpis"):' in APP
    for tag in ("stMetricValue", "stMetricLabel", "stTable", "stTabContent"):
        assert tag in CSS
    assert ".st-key-quality_kpis" in CSS
    assert ".bl-flow li" in CSS
    assert 'font-size: 14.5px !important' in CSS
    assert "width: max-content" in CSS
    assert 'box-sizing: border-box' in CSS
    assert "prefers-reduced-motion: reduce" in CSS
    assert "\u2014" not in CSS


def test_browser_gate_checks_real_dom_not_just_static_mockups():
    assert 'get_by_role("tablist")' in SMOKE
    assert 'get_by_role("list", name="Validation sequence")' in SMOKE
    assert 'quality_kpis' in SMOKE
    assert 'quality.png' in SMOKE
    assert '("wide", 1920, 1080)' in SMOKE


def test_original_data_contract_and_modern_streamlit_width():
    for required in ("snapshot_from_rollup(rollup)", "recommend_with_holdout(",
                     "filter_rule_view(", "quality_reason_label(",
                     "st.download_button(", "st.plotly_chart("):
        assert required in APP
    assert "use_container_width=True" not in APP
    assert 'width="stretch"' in APP
