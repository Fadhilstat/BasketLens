"""M5.3 style contract protects native workflow and quiet responsive motion."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app" / "streamlit_app.py").read_text(encoding="utf-8")
STYLE = (ROOT / "app" / "assets" / "basketlens.css").read_text(encoding="utf-8")


def test_css_uses_a_single_consolidated_stylesheet_and_scoped_keys():
    assert '"basketlens.css"' in APP
    assert '"refinement-m53.css"' not in APP
    for key in ("sales_kpis", "sales_trend_panel", "basket_mix_panel", "product_mix_panel"):
        assert f'key="{key}"' in APP
        assert f".st-key-{key}" in STYLE


def test_visual_system_has_motion_and_no_inaccessible_slop():
    assert "prefers-reduced-motion: reduce" in STYLE
    assert ":focus-visible" in STYLE
    assert "@media (max-width: 800px)" in STYLE
    assert "@media (max-width: 480px)" in STYLE
    assert "scroll-snap-type: x proximity" in STYLE
    assert "background-image: url(\"data:image/svg+xml" in STYLE
    for dangerous in ("backdrop-filter", "margin-left:-", "\u2014"):
        assert dangerous not in STYLE
    legacy, connectors = STYLE.split("/* M5.6: geometrically centered methodology steps and connectors. */", 1)
    assert "position: absolute" not in legacy
    assert connectors.count("position: absolute;") == 1


def test_analytics_and_export_apis_remain_intact():
    for expected in ('snapshot_from_rollup(rollup)', 'st.tabs([', 'st.plotly_chart(',
                     'st.download_button(', 'filter_rule_view(', 'recommend_with_holdout(',
                     'st.selectbox(', 'st.metric('):
        # Metric calls are made on columns, not the top-level st object.
        if expected != 'st.metric(':
            assert expected in APP
    assert 'col1.metric(' in APP and 'col4.metric(' in APP
