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
                for label, width, height in [("desktop", 1440, 900), ("mobile", 390, 844)]:
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            device_scale_factor=1)
                    page.goto("http://127.0.0.1:8501", wait_until="domcontentloaded", timeout=60000)
                    page.get_by_role("heading", name="BasketLens").wait_for(timeout=90000)
                    page.locator(".bl-topbar").wait_for(timeout=90000)
                    page.get_by_role("heading", name="Find the story in every basket.").wait_for(timeout=90000)
                    page.get_by_role("tab", name="Sales overview").wait_for(timeout=90000)
                    page.get_by_text("Start with what the baskets tell us").wait_for(timeout=60000)
                    page.get_by_role("combobox", name="Show sales for").wait_for(timeout=30000)
                    page.locator('[data-testid="stMetric"]').first.wait_for(timeout=30000)
                    page.get_by_text("Sales over time", exact=True).wait_for(timeout=60000)
                    rail = page.get_by_role("navigation", name="Research resources")
                    if label == "desktop" and not rail.is_visible():
                        raise AssertionError("Desktop shortcut rail is missing")
                    if label == "mobile" and rail.is_visible():
                        raise AssertionError("Shortcut rail overlaps mobile content")
                    if page.get_by_text("This app has encountered an error").count():
                        raise AssertionError(f"{label}: Streamlit runtime error")
                    page.get_by_role("tab", name="Association explorer").click(timeout=30000)
                    page.get_by_text("Which products appeared together?").wait_for(timeout=60000)
                    page.get_by_text("Product affinity map").wait_for(timeout=60000)
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
                    page.screenshot(path=str(args.report / f"{label}.png"),
                                    full_page=True, animations="disabled")
                    page.get_by_role("tab", name="Build a basket").click(timeout=30000)
                    page.get_by_text("Choose one or more products").wait_for(timeout=60000)
                    if is_public:
                        page.get_by_role("button", name="Fill an example basket").click(timeout=30000)
                        page.get_by_text("related product candidates").wait_for(timeout=60000)
                    page.get_by_role("tab", name="Data quality & methodology").click(timeout=30000)
                    page.get_by_text("What can we trust in this analysis?").wait_for(timeout=60000)
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
        print("REAL_DATA_BROWSER_QA_PASS desktop mobile M5 chrome search basket tabs keyboard viewport")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()