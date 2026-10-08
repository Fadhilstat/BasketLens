"""Browser-level desktop and mobile smoke test against the real-data dashboard.

Runs only in the temporary CI runner. Screenshots show aggregate UCI results.
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
    os.environ["BASKETLENS_DATA_DIR"] = str(args.data.resolve())
    args.report.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(app_path),
         "--server.headless=true", "--server.address=127.0.0.1",
         "--server.port=8501", "--browser.gatherUsageStats=false"],
        cwd=str(root), env=dict(os.environ), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError("Streamlit server exited before health check")
            try:
                with urlopen("http://127.0.0.1:8501/_stcore/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(1)
        else:
            raise TimeoutError("Streamlit server failed health check")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for label, width, height in [("desktop", 1440, 900), ("mobile", 390, 844)]:
                    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                    page.goto("http://127.0.0.1:8501", wait_until="domcontentloaded", timeout=60000)
                    page.get_by_role("heading", name="BasketLens").wait_for(timeout=90000)
                    page.get_by_role("tab", name="Sales overview").wait_for(timeout=90000)
                    if page.locator("text=This app has encountered an error").count():
                        raise AssertionError(f"{label}: Streamlit showed a runtime error")
                    page.get_by_role("tab", name="Association explorer").click(timeout=30000)
                    page.get_by_text("Product affinity map").wait_for(timeout=60000)
                    page.screenshot(path=str(args.report / f"{label}.png"), full_page=True, animations="disabled")
                    page.get_by_role("tab", name="Build a basket").click(timeout=30000)
                    page.get_by_text("Choose one or more products").wait_for(timeout=30000)
                    page.keyboard.press("Tab")
                    if not page.evaluate("document.activeElement !== document.body"):
                        raise AssertionError(f"{label}: no keyboard focus detected")
                    page.close()
            finally:
                browser.close()
        print("REAL_DATA_BROWSER_QA_PASS desktop mobile tabs keyboard screenshot")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
