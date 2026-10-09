"""Guard against asymmetric validation-stage cards and connectors."""
from pathlib import Path
from basketlens.dashboard_ui import quality_pipeline

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "app/assets/basketlens.css").read_text(encoding="utf-8")
SMOKE = (ROOT / "scripts/browser_smoke.py").read_text(encoding="utf-8")


def test_five_semantic_stages_unchanged():
    html = quality_pipeline()
    assert html.count("<li>") == 5
    assert html.count("</li>") == 5
    for number in ("01", "02", "03", "04", "05"):
        assert number in html
    assert "aria-label=\"Validation sequence\"" in html


def test_fixed_icon_and_label_grid_prevent_asymmetric_cards():
    section = CSS.split("/* M5.6: geometrically centered methodology steps and connectors. */", 1)[-1]
    assert "grid-template-columns: minmax(0, 1fr) 34px 12px 36px minmax(0, 1fr)" in section
    assert "grid-column: 2;" in section
    assert "grid-column: 4;" in section
    assert "grid-column: 1 / -1;" in section
    assert "min-height: 120px;" in section
    assert "width: 100%;" in section
    assert "margin: 0;" in section
    assert "justify-self: stretch;" in section
    assert "align-content: center;" in section
    assert "align-items: stretch;" in section
    assert "overflow-wrap: anywhere" in CSS


def test_only_connector_is_absolutely_positioned():
    before, release = CSS.split("/* M5.6: geometrically centered methodology steps and connectors. */", 1)
    assert "position: absolute" not in before
    assert release.count("position: absolute;") == 1
    assert 'li:not(:last-child)::after' in release
    assert 'top: 50%' in release
    assert 'transform: translateY(-50%)' in release
    assert 'right: calc(-1 * (var(--bl-flow-gap) / 2 + 8px))' in release


def test_responsive_flow_has_centered_tablet_last_row_and_mobile_column():
    section = CSS.split("/* M5.6: geometrically centered methodology steps and connectors. */", 1)[-1]
    assert "repeat(6, minmax(0, 1fr))" in section
    assert ".bl-flow li:nth-child(4) { grid-column: 2 / span 2; }" in section
    assert ".bl-flow li:nth-child(5) { grid-column: 4 / span 2; }" in section
    assert "grid-template-columns: 1fr;" in section
    assert ".bl-flow li:not(:last-child)::after { display: none; }" in section


def test_real_browser_checks_actual_card_and_arrow_centers():
    for expected in ("flow cards have uneven heights", "flow cards have uneven widths",
                     "index/icon off-center", "label off-center", "connector", "gap_center"):
        assert expected in SMOKE
    assert "REAL_DATA_BROWSER_QA_PASS wide desktop mobile M6" in SMOKE
