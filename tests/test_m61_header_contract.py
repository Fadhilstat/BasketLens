"""CSS and link semantics contract for portfolio-ready M6.1 header."""
from pathlib import Path
from basketlens.dashboard_ui import dashboard_header

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "app/assets/basketlens.css").read_text(encoding="utf-8")
MARKER = "/* BasketLens M6.1: header alignment and real-resource navigation. */"


def test_m61_styles_scoped_and_unique():
    assert CSS.count(MARKER) == 1
    section = CSS.split(MARKER, 1)[1]
    for selector in (".bl-topbar .bl-brand-copy", ".bl-topbar .bl-topbar-right",
                     ".bl-topbar .bl-header-links", ".bl-topbar .bl-mode-dot",
                     ".bl-topbar .bl-header-links a:focus-visible"):
        assert selector in section
    assert "min-height:80px" in section
    assert "@media (max-width:760px)" in section
    assert "@media (max-width:390px)" in section
    assert "min-height:44px" in section
    assert "prefers-reduced-motion:reduce" in section
    assert "position:absolute" not in section and "backdrop-filter" not in section


def test_real_links_and_honest_status_label():
    page = dashboard_header("2009", "2011", True)
    assert 'aria-label="Research resources"' in page
    assert page.count('target="_blank"') == 3
    assert "Curated public research" in page
    assert "href=" not in page.split('class="bl-mode-dot">')[1].split("</span>")[0]
    assert "archive.ics.uci.edu" in page
    assert "/docs/methodology.md" in page
