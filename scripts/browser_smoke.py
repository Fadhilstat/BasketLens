"""Browser smoke for the real-data and public BasketLens experience.

Executed on temporary GitLab CI, with screenshots of aggregate-only results.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--report", default=Path("reports/screenshots"), type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    app_path = root / "app" / "streamlit_app.py"
    target = args.data.resolve()
    is_public = not (target / "manifest.json").exists()
    env = dict(os.environ, BASKETLENS_DATA_DIR=str(target))
    args.report.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(app_path),
         "--server.headless=true", "--server.address=127.0.0.1",
         "--server.port=8501", "--browser.gatherUsageStats=false"],
        cwd=str(root), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError("Streamlit exited before its health check")
            try:
                with urlopen("http://127.0.0.1:8501/_stcore/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(1)
        else:
            raise TimeoutError("Streamlit did not become healthy")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for label, width, height in [("wide", 1920, 1080), ("desktop", 1440, 900), ("mobile", 390, 844)]:
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            device_scale_factor=1)
                    page.goto("http://127.0.0.1:8501", wait_until="domcontentloaded", timeout=60000)
                    page.get_by_role("heading", name="BasketLens").wait_for(timeout=90000)
                    page.locator(".bl-topbar").wait_for(timeout=90000)
                    page.get_by_role("heading", name="Find the story in every basket.").wait_for(timeout=90000)
                    page.get_by_role("tab", name="Sales overview").wait_for(timeout=90000)
                    page.get_by_text("Start with what the baskets tell us").wait_for(timeout=60000)
                    page.get_by_role("combobox", name="Show sales for").wait_for(timeout=30000)
                    page.get_by_text("Sales over time", exact=True).wait_for(timeout=60000)
                    # M6 editorial case is genuinely derived from public and full UCI rules.
                    portfolio_brief = page.locator(".bl-decision-brief")
                    portfolio_brief.wait_for(timeout=30000)
                    if portfolio_brief.count() != 1:
                        raise AssertionError(f"{label}: decision brief missing")
                    if portfolio_brief.locator(".bl-case-results > div").count() != 4:
                        raise AssertionError(f"{label}: decision evidence incomplete")
                    if "does not demonstrate incremental conversion" not in portfolio_brief.inner_text():
                        raise AssertionError(f"{label}: causal limitation missing")

                    # Streamlit batches widget messages; one visible metric does
                    # not establish that the entire four-column layout has rendered.
                    try:
                        page.wait_for_function(
                            "() => document.querySelectorAll('[data-testid=stMetric]').length >= 4",
                            timeout=90000,
                        )
                    except Exception as exc:
                        page.screenshot(path=str(args.report / f"{label}-missing-metrics.png"),
                                        full_page=False, animations="disabled")
                        raise AssertionError(
                            f"{label}: fewer than 4 overview metrics after render wait"
                        ) from exc
                    metric_count = page.locator('[data-testid="stMetric"]').count()
                    if metric_count < 4:
                        raise AssertionError(f"{label}: expected 4 data-backed KPI cards")
                    # Real Streamlit computed-style contract for M5.3.
                    if page.locator(".st-key-sales_kpis").count() != 1:
                        raise AssertionError(f"{label}: scoped KPI group missing")
                    for panel_key in ("sales_trend_panel", "basket_mix_panel", "product_mix_panel"):
                        if page.locator(".st-key-" + panel_key).count() != 1:
                            raise AssertionError(f"{label}: missing analytics panel {panel_key}")
                    metric_radius = page.locator('[data-testid="stMetric"]').first.evaluate(
                        "el => parseFloat(getComputedStyle(el).borderTopLeftRadius)")
                    if metric_radius < 17:
                        raise AssertionError(f"{label}: KPI surface is not rounded")
                    tab_radius = page.get_by_role("tab", name="Sales overview").evaluate(
                        "el => parseFloat(getComputedStyle(el).borderTopLeftRadius)")
                    if tab_radius < 10:
                        raise AssertionError(f"{label}: tab treatment missing")
                    tab_surface = page.get_by_role("tablist").first.evaluate(
                        "el => getComputedStyle(el).backgroundColor")
                    if tab_surface in {"rgba(0, 0, 0, 0)", "transparent"}:
                        raise AssertionError(f"{label}: navigation track is invisible")
                    tab_font = page.get_by_role("tab", name="Sales overview").evaluate(
                        "el => parseFloat(getComputedStyle(el).fontSize)")
                    if tab_font < 14:
                        raise AssertionError(f"{label}: tab labels are too small")
                    if label in {"wide", "desktop"}:
                        first_icon = page.locator(".st-key-sales_kpis [data-testid='stMetric']").first.evaluate(
                            "el => getComputedStyle(el, '::before').backgroundImage")
                        if "data:image/svg+xml" not in first_icon:
                            raise AssertionError("Desktop KPI icon treatment did not render")

                    page.screenshot(path=str(args.report / f"{label}-overview.png"),
                                    full_page=False, animations="disabled")
                    # Layout regression: the old absolute-positioned icon rail
                    # crossed the hero heading in the live Streamlit app.
                    if page.locator(".bl-resource-rail").count():
                        raise AssertionError("Absolute shortcut rail should not exist")
                    nav = page.get_by_role("navigation", name="Research resources")
                    if nav.get_by_role("link").count() != 3:
                        raise AssertionError("The header must expose three working resource links")
                    topbar_box = page.locator(".bl-topbar").bounding_box()
                    hero_box = page.locator(".bl-intro-hero").bounding_box()
                    if topbar_box is None or hero_box is None:
                        raise AssertionError("Header or hero layout is not visible")
                    if topbar_box["y"] + topbar_box["height"] > hero_box["y"] + 3:
                        raise AssertionError(f"{label}: header overlaps the hero")
                    if abs(topbar_box["x"] - hero_box["x"]) > 20:
                        raise AssertionError(f"{label}: header and content do not align")
                    if page.get_by_text("This app has encountered an error").count():
                        raise AssertionError(f"{label}: Streamlit runtime error")
                    page.get_by_role("tab", name="Association explorer").click(timeout=30000)
                    page.get_by_text("Which products appeared together?").wait_for(timeout=60000)
                    page.get_by_text("Most frequent product pairings").wait_for(timeout=60000)
                    page.locator(".bl-pair-card").first.wait_for(timeout=60000)
                    page.get_by_text("Optional: product connection network").wait_for(timeout=60000)
                    if is_public:
                        search = page.get_by_role("textbox", name="Search by product or SKU")
                        search.fill("___NOT_AN_ACTUAL_STOCK_CODE___")
                        search.press("Enter")
                        page.get_by_role("tab", name="Association explorer").click(timeout=30000)
                        page.get_by_text("No rules match your search and thresholds").wait_for(timeout=60000)
                        search = page.get_by_role("textbox", name="Search by product or SKU")
                        search.fill("")
                        search.press("Enter")
                        page.get_by_role("tab", name="Association explorer").click(timeout=30000)
                        page.get_by_text("A pairing worth examining").wait_for(timeout=60000)
                    page.screenshot(path=str(args.report / f"{label}-pairings.png"),
                                    full_page=False, animations="disabled")
                    page.get_by_role("tab", name="Build a basket").click(timeout=30000)
                    page.get_by_text("Choose one or more products").wait_for(timeout=60000)
                    if is_public:
                        page.get_by_role("button", name="Fill an example basket").click(timeout=30000)
                        page.get_by_text("related product candidates").wait_for(timeout=60000)
                    page.get_by_role("tab", name="Data quality & methodology").click(timeout=30000)
                    page.get_by_text("What can we trust in this analysis?").wait_for(timeout=60000)
                    # M5.5 approves real Streamlit presentation, not a mock screenshot.
                    quality_cards = page.locator(".st-key-quality_kpis [data-testid='stMetric']")
                    if quality_cards.count() != 4:
                        raise AssertionError(f"{label}: four quality cards are required")
                    flow_steps = page.get_by_role("list", name="Validation sequence").locator("li")
                    if flow_steps.count() != 5:
                        raise AssertionError(f"{label}: five methodological stages are required")
                    # M5.6: check rendered card geometry, not just CSS declarations.
                    if label in {"wide", "desktop"}:
                        symmetry = page.get_by_role(
                            "list", name="Validation sequence").evaluate("""list => {
                            return [...list.querySelectorAll(':scope > li')].map(node => {
                                const box = node.getBoundingClientRect();
                                const badge = node.querySelector('.bl-flow-index').getBoundingClientRect();
                                const text = node.querySelector('.bl-flow-copy').getBoundingClientRect();
                                const arrow = getComputedStyle(node, '::after');
                                return {
                                    x: box.x, y: box.y, width: box.width,
                                    height: box.height, center: box.x + box.width / 2,
                                    badgeCenter: badge.x + badge.width / 2,
                                    labelCenter: text.x + text.width / 2,
                                    connectorRight: Number.parseFloat(arrow.right),
                                    connectorWidth: Number.parseFloat(arrow.width),
                                    connectorPosition: arrow.position
                                };
                            });
                        }""")
                        if len(symmetry) != 5:
                            raise AssertionError(f"{label}: five symmetrical stages required")
                        if max(x["y"] for x in symmetry) - min(x["y"] for x in symmetry) > 2:
                            raise AssertionError(f"{label}: flow cards are not level")
                        if max(x["height"] for x in symmetry) - min(x["height"] for x in symmetry) > 2:
                            raise AssertionError(f"{label}: flow cards have uneven heights")
                        if max(x["width"] for x in symmetry) - min(x["width"] for x in symmetry) > 2:
                            raise AssertionError(f"{label}: flow cards have uneven widths")
                        for i, stage in enumerate(symmetry):
                            if abs(stage["center"] - stage["labelCenter"]) > 2:
                                raise AssertionError(f"{label}: stage {i+1} label off-center")
                            if abs(stage["badgeCenter"] + 24 - stage["center"]) > 2:
                                raise AssertionError(f"{label}: stage {i+1} index/icon off-center")
                            if i < 4:
                                if stage["connectorPosition"] != "absolute":
                                    raise AssertionError(f"{label}: connector positioning missing")
                                arrow_center = (stage["x"] + stage["width"]
                                                - stage["connectorRight"]
                                                - stage["connectorWidth"] / 2)
                                gap_center = ((stage["x"] + stage["width"]
                                               + symmetry[i+1]["x"]) / 2)
                                if abs(arrow_center - gap_center) > 3:
                                    raise AssertionError(
                                        f"{label}: connector {i+1} off-center: "
                                        f"arrow={arrow_center:.2f} gap={gap_center:.2f}, "
                                        f"card x={stage['x']:.2f} w={stage['width']:.2f}, "
                                        f"right={stage['connectorRight']:.2f}, "
                                        f"width={stage['connectorWidth']:.2f}, "
                                        f"next x={symmetry[i+1]['x']:.2f}")

                    if label != "mobile":
                        quality_icon = quality_cards.first.evaluate(
                            "el => getComputedStyle(el, '::before').backgroundImage"
                        )
                        if "data:image/svg+xml" not in quality_icon:
                            raise AssertionError(f"{label}: quality card pictogram missing")
                    if label == "mobile":
                        tablist = page.get_by_role("tablist").first
                        layout = tablist.evaluate("el => getComputedStyle(el).gridTemplateColumns")
                        if len(layout.split()) != 2:
                            raise AssertionError(f"{label}: all tabs need visible two-column layout")
                    if page.locator('[data-testid="stTable"] table').count():
                        align = page.locator('[data-testid="stTable"] tbody td:last-child').first.evaluate(
                            "el => getComputedStyle(el).textAlign")
                        if align != "right":
                            raise AssertionError(f"{label}: evidence counts must align right")

                    quality_kpis = page.locator(".st-key-quality_kpis [data-testid='stMetric']")
                    try:
                        page.wait_for_function(
                            "() => document.querySelectorAll('.st-key-quality_kpis [data-testid=stMetric]').length === 4",
                            timeout=60000,
                        )
                    except Exception as exc:
                        page.screenshot(path=str(args.report / f"{label}-quality-missing.png"),
                                        full_page=False, animations="disabled")
                        raise AssertionError(f"{label}: missing quality KPI after render wait") from exc
                    quality_value = quality_kpis.first.locator(
                        '[data-testid="stMetricValue"]').evaluate(
                        "el => parseFloat(getComputedStyle(el).fontSize)")
                    if quality_value < 24:
                        raise AssertionError(f"{label}: quality metric value is too small")
                    flow = page.get_by_role("list", name="Validation sequence")
                    flow.locator("li").first.wait_for(timeout=30000)
                    if flow.locator("li").count() != 5:
                        raise AssertionError(f"{label}: validation steps lost")
                    page.screenshot(path=str(args.report / f"{label}-quality.png"),
                                    full_page=False, animations="disabled")
                    page.get_by_text("Read the methodology, definitions and limitations").wait_for(
                        timeout=30000)
                    page.keyboard.press("Tab")
                    if not page.evaluate("document.activeElement !== document.body"):
                        raise AssertionError(f"{label}: no keyboard focus detected")
                    horizontal_overflow = page.evaluate(
                        "document.documentElement.scrollWidth > document.documentElement.clientWidth + 16"
                    )
                    if horizontal_overflow:
                        raise AssertionError(f"{label}: horizontal page overflow")
                    page.close()
            finally:
                browser.close()
        print("REAL_DATA_BROWSER_QA_PASS wide desktop mobile M6 dynamic decision case plus M5.6 symmetrical methodology")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()