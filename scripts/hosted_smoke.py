"""Anonymous browser QA for a deployed BasketLens Streamlit app.

python scripts/hosted_smoke.py --url https://basketlens-retail.streamlit.app/
Requires Playwright with Chromium. Reports deliberately omit login payloads.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlsplit

VIEWPORTS = (("desktop", 1440, 900), ("mobile", 390, 844))
DEFAULT_URL = "https://basketlens-retail.streamlit.app/"


class ReleaseNotReady(RuntimeError):
    pass


def validate_app_url(raw: str) -> str:
    parts = urlsplit(raw.strip())
    host = (parts.hostname or "").lower()
    try:
        has_port = parts.port is not None
    except ValueError as exc:
        raise ValueError("Invalid port") from exc
    if (parts.scheme != "https" or not host.endswith(".streamlit.app")
            or host == ".streamlit.app" or parts.username or parts.password
            or has_port or parts.query or parts.fragment or parts.path not in ("", "/")):
        raise ValueError("Provide a clean HTTPS *.streamlit.app root URL")
    return "https://" + host + "/"


def login_redirect(url: str) -> bool:
    parts = urlsplit(url)
    path = parts.path.lower().rstrip("/")
    return (path in ("/-/login", "/login", "/auth")
            or path.startswith(("/-/login/", "/login/", "/auth/"))
            or "auth.streamlit" in (parts.hostname or "").lower())


def sanitized_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    path = "/-/login" if login_redirect(url) else "/"
    return parts.scheme + "://" + host + path


def assert_layout(header: dict | None, hero: dict | None) -> None:
    if not header or not hero:
        raise ReleaseNotReady("Missing page geometry")
    if header["y"] + header["height"] > hero["y"] + 3:
        raise ReleaseNotReady("Header overlaps introduction")
    if abs(header["x"] - hero["x"]) > 20:
        raise ReleaseNotReady("Header and hero misaligned")


def overflow(page) -> bool:
    return bool(page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth + 16"
    ))


def check_viewport(page, label: str, report_dir: Path) -> dict:
    if login_redirect(page.url):
        raise ReleaseNotReady("Anonymous access redirected to login")
    try:
        page.get_by_role("heading", name="BasketLens").wait_for(timeout=45000)
        page.get_by_role("tab", name="Sales overview").wait_for(timeout=30000)
        page.locator('[data-testid="stMetric"]').first.wait_for(timeout=30000)
    except Exception as exc:
        raise ReleaseNotReady("Dashboard did not load for anonymous visitor") from exc
    if login_redirect(page.url):
        raise ReleaseNotReady("Anonymous access redirected to login")
    if page.get_by_text("This app has encountered an error").count():
        raise ReleaseNotReady("Streamlit error displayed")
    if page.locator(".bl-resource-rail").count():
        raise ReleaseNotReady("Floating navigation rail returned")
    count = page.locator('[data-testid="stMetric"]').count()
    if count < 4:
        raise ReleaseNotReady("Fewer than four KPIs")
    assert_layout(page.locator(".bl-topbar").bounding_box(),
                  page.locator(".bl-intro-hero").bounding_box())
    if page.get_by_role("navigation", name="Research resources").get_by_role("link").count() != 3:
        raise ReleaseNotReady("Research navigation links missing")
    if overflow(page):
        raise ReleaseNotReady("Overview horizontal overflow")
    page.screenshot(path=str(report_dir / (label + "-overview.png")), animations="disabled")
    page.get_by_role("tab", name="Association explorer").click()
    page.locator(".bl-pair-card").first.wait_for(timeout=30000)
    pairs = page.locator(".bl-pair-card").count()
    if pairs != 4:
        raise ReleaseNotReady("Expected four unique pairing cards")
    page.get_by_role("textbox", name="Search by product or SKU").wait_for(timeout=15000)
    if overflow(page):
        raise ReleaseNotReady("Pairings horizontal overflow")
    page.screenshot(path=str(report_dir / (label + "-pairings.png")), animations="disabled")
    page.get_by_role("tab", name="Build a basket").click()
    page.get_by_role("button", name="Fill an example basket").click()
    page.get_by_text("related product candidates").wait_for(timeout=30000)
    page.get_by_role("tab", name="Data quality & methodology").click()
    page.get_by_text("What can we trust in this analysis?").wait_for(timeout=30000)
    page.keyboard.press("Tab")
    if not page.evaluate("document.activeElement !== document.body"):
        raise ReleaseNotReady("Keyboard focus missing")
    if overflow(page):
        raise ReleaseNotReady("Research workflow horizontal overflow")
    return {"viewport": label, "status": "PASS", "kpis": count, "pair_cards": pairs}


def run(url: str, report_dir: Path) -> dict:
    url = validate_app_url(url)
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {"check": "BasketLens anonymous hosted QA",
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "app": url, "status": "FAIL", "viewports": []}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for label, width, height in VIEWPORTS:
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            locale="en-GB", device_scale_factor=1)
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        report["viewports"].append(check_viewport(page, label, report_dir))
                    except Exception as exc:
                        reason = (str(exc) if isinstance(exc, ReleaseNotReady)
                                  else "Browser navigation or interactive QA failed")
                        report["viewports"].append({
                            "viewport": label, "status": "FAIL", "reason": reason,
                            "final_url_sanitized": sanitized_url(page.url)})
                        try:
                            page.screenshot(path=str(report_dir / (label + "-failure.png")),
                                            animations="disabled")
                        except Exception:
                            pass
                    finally:
                        page.close()
            finally:
                browser.close()
    except Exception:
        report["viewports"].append({"viewport": "setup", "status": "FAIL",
                                    "reason": "Playwright/Chromium not available"})
    report["status"] = ("PASS" if len(report["viewports"]) == len(VIEWPORTS)
                        and all(x["status"] == "PASS" for x in report["viewports"])
                        else "FAIL")
    (report_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n",
                                               encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--report", type=Path, default=Path("reports/hosted-smoke"))
    args = parser.parse_args()
    try:
        result = run(args.url, args.report)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
