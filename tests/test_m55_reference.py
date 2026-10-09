"""M5.5 release contract for screenshot-approved methodology layout."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "app/assets/basketlens.css").read_text(encoding="utf-8")
APP = (ROOT / "app/streamlit_app.py").read_text(encoding="utf-8")
SMOKE = (ROOT / "scripts/browser_smoke.py").read_text(encoding="utf-8")


def test_native_quality_metrics_and_data_source_stay_intact():
    assert 'with st.container(key="quality_kpis"):' in APP
    assert 'quality_reason_label(' in APP
    assert 'quality_pipeline()' in APP
    assert "st.metric(" not in CSS


def test_reference_quality_cards_preserve_all_four_real_labels():
    assert ".st-key-quality_kpis" in CSS
    assert '[data-testid="stMetric"]::before' in CSS
    for number in (1, 2, 3, 4):
        assert f'[data-testid="stColumn"]:nth-child({number}) [data-testid="stMetric"]::before' in CSS
    assert "data:image/svg+xml" in CSS


def test_process_visuals_remain_ordered_not_fake_buttons():
    assert '.bl-flow li:nth-child(5)::before' in CSS
    assert '.bl-flow li:not(:last-child)::after' in CSS
    assert 'get_by_role("list", name="Validation sequence")' in SMOKE


def test_ledger_is_readable_and_numeric():
    assert '[data-testid="stTable"]' in CSS
    assert 'font-variant-numeric:tabular-nums' in CSS
    assert 'text-align:right !important' in CSS
    assert "evidence counts must align right" in SMOKE


def test_mobile_tabs_and_motion_accessibility():
    assert 'grid-template-columns:repeat(2,minmax(0,1fr))' in CSS
    assert '@media (max-width:480px)' in CSS
    assert "prefers-reduced-motion" in CSS
    assert ":focus-visible" in CSS
    assert "all tabs need visible two-column layout" in SMOKE


def test_no_nonfunctional_decorative_navigation_or_unsafe_copy():
    for banned in ("position: absolute", "backdrop-filter", "—", "#8b5cf6"):
        assert banned not in CSS
    assert 'aria-selected="true"' in CSS
    assert 'st.plotly_chart(' in APP
    assert 'st.download_button(' in APP
