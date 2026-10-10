"""Anonymous release smoke test for the deployed BasketLens Vercel portfolio."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_URL = "https://basketlens-fadhil-9768s-projects.vercel.app/"
ALLOWED_HOSTS = {
    "basketlens-fadhil-9768s-projects.vercel.app",
    "basketlens-topaz.vercel.app",
}
VIEWPORTS = (("desktop", 1440, 900), ("mobile", 390, 844), ("small-mobile", 320, 700))


def clean_url(raw: str) -> str:
    parsed = urlsplit(raw.strip())
    if (parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS
            or parsed.username or parsed.password or parsed.port
            or parsed.query or parsed.fragment or parsed.path not in ("", "/")):
        raise ValueError("Use the clean HTTPS BasketLens production Vercel URL")
    return "https://" + parsed.hostname + "/"


def check_page(page, url: str) -> dict:
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
    if response is None or response.status < 200 or response.status >= 300:
        raise AssertionError("Public entrypoint did not respond with HTTP 2xx")
    if urlsplit(page.url).hostname not in ALLOWED_HOSTS:
        raise AssertionError("Public guest redirected away from BasketLens")
    page.locator("#hero-title").wait_for(timeout=30000)
    title = page.locator("#hero-title").inner_text()
    if "A pattern in the basket." not in title or "Not a sales forecast." not in title:
        raise AssertionError("Wrong page content or authentication gate")
    if page.get_by_role("heading", level=1).count() != 1:
        raise AssertionError("Missing unique page heading")
    for anchor in ("finding", "method", "decision"):
        if page.locator(f"#{anchor}").count() != 1:
            raise AssertionError(f"Missing published {anchor} section")
    dashboard = page.locator(".kpi-row").count() == 1
    if dashboard:
        if page.locator(".kpi-row .kpi").count() != 4 or "40,280" not in page.locator(".kpi-row").inner_text():
            raise AssertionError("Source-backed dashboard KPIs missing")
        if page.get_by_role("navigation", name="Research sections").count() != 1:
            raise AssertionError("Research sidebar is missing")
        if page.locator(".hero-banner").count() != 1 or page.locator(".finding-grid").count() != 1:
            raise AssertionError("Retail intelligence dashboard layout is missing")
    elif os.getenv("CI_PIPELINE_SOURCE") == "merge_request_event":
        # Source MR is tested while the previous production site is still live.
        if "40,280" not in page.locator(".hero-ledger").inner_text():
            raise AssertionError("Neither existing nor redesigned public cohort is available")
    else:
        raise AssertionError("Production has not deployed the approved dashboard redesign")

    earlier = page.get_by_role("tab", name="Earlier training")
    later = page.get_by_role("tab", name="Later holdout")
    if earlier.get_attribute("aria-selected") != "true":
        raise AssertionError("Earlier training not selected initially")
    later.click()
    if (page.locator("#chart-value").inner_text() != "67.1%"
            or page.locator("#count-value").inner_text() != "279 of 416 baskets"
            or page.get_by_role("progressbar").get_attribute("aria-valuenow") != "67.1"):
        raise AssertionError("Later holdout interaction returned wrong values")
    later.press("ArrowLeft")
    if (earlier.get_attribute("aria-selected") != "true"
            or page.locator("#chart-value").inner_text() != "63.1%"):
        raise AssertionError("Keyboard period selection did not work")

    page.locator(".method-details summary").click()
    if not page.get_by_text("30,317 routine line exclusions").is_visible():
        raise AssertionError("Quality exclusion details missing")
    research = page.get_by_role("link", name="Read full case study")
    if research.count() == 1:
        if research.get_attribute("href") != "https://github.com/Fadhilstat/BasketLens/blob/main/docs/portfolio-case-study.md":
            raise AssertionError("Public case study URL is invalid")
        cta = "verified_source_link"
    elif os.getenv("CI_PIPELINE_SOURCE") == "merge_request_event":
        previous = page.get_by_role("link", name="Open research dashboard")
        if previous.count() != 1:
            raise AssertionError("Neither prior nor new published reference exists")
        cta = "previous_production_release"
    else:
        raise AssertionError("Production still exposes an unverified Streamlit CTA")
    # Rule Explorer is tested after it has deployed to production.
    # An MR runs against the preceding guest-facing production release.
    explorer_present = page.locator("#explorer").count() == 1
    if not explorer_present and os.getenv("CI_PIPELINE_SOURCE") != "merge_request_event":
        raise AssertionError("Production is missing the Rule Explorer release")
    if explorer_present:
        page.wait_for_function(
            "document.querySelector('#rule-summary')?.textContent?.includes('1,500 of 1,500')",
            timeout=30000)
        if page.locator(".rule-row").count() != 8 or not page.locator("#rule-error").is_hidden():
            raise AssertionError("Published rule data did not load correctly")
        if not page.locator("#rule-fingerprint").inner_text().startswith("Exhibit SHA256 5303df81bb5d"):
            raise AssertionError("Unexpected public exhibit fingerprint")
        page.locator("#rule-query").fill("22386")
        if page.locator(".rule-row").count() < 1:
            raise AssertionError("Published product code search yielded no result")
        if not page.locator(".rule-row").first.inner_text().find("22386") >= 0:
            raise AssertionError("SKU search returned unrelated rules")
        page.locator("#rule-query").fill("NOT_A_REAL_SKU_TEST_2026")
        if not page.get_by_text("No rules match these filters.").is_visible():
            raise AssertionError("Empty rule search state failed")
        page.get_by_role("button", name="Reset filters").click()
        page.wait_for_function(
            "document.querySelector('#rule-summary')?.textContent?.includes('1,500 of 1,500')",
            timeout=10000)
        if page.locator(".rule-row").count() != 8:
            raise AssertionError("Explorer filter reset failed")
        page.get_by_role("button", name="Show 8 more rules").click()
        if page.locator(".rule-row").count() != 16:
            raise AssertionError("Explorer pagination failed")


    # The M6.7 Basket Builder must exist after production deploy.
    basket_present = page.locator("#basket").count() == 1
    if not basket_present and os.getenv("CI_PIPELINE_SOURCE") != "merge_request_event":
        raise AssertionError("Production is missing the example Basket Builder")
    if basket_present:
        page.get_by_role("button", name="Load published example").click()
        page.locator("#basket-candidates li").first.wait_for(timeout=12000)
        if page.locator("#basket-chosen li").count() != 1:
            raise AssertionError("Verified example basket did not select exactly one product")
        if not page.locator("#basket-candidates").inner_text():
            raise AssertionError("Basket did not render published matching rules")
        page.get_by_role("button", name="Clear basket").click()
        if "No products selected" not in page.locator("#basket-status").inner_text():
            raise AssertionError("Basket clear action did not update state")
        page.get_by_label("Search catalogued product").fill("22386")
        page.locator("#basket-options button").first.click()
        if page.locator("#basket-chosen li").count() != 1 or not page.locator("#basket-error").is_hidden():
            raise AssertionError("Live basket SKU selection failed")


    # Typography is required only after merge; an MR tests the prior published release.
    has_m68_type = page.locator('link[href^="https://fonts.googleapis.com/css2"]').count() == 1
    if os.getenv("CI_PIPELINE_SOURCE") != "merge_request_event" and not has_m68_type:
        raise AssertionError("Published M6.8 font stylesheet is missing")
    if has_m68_type:
        if "Manrope" not in page.evaluate("getComputedStyle(document.body).fontFamily"):
            raise AssertionError("Functional UI does not use Manrope")
        if "Instrument Serif" not in page.locator("#hero-title").evaluate("(el) => getComputedStyle(el).fontFamily"):
            raise AssertionError("Editorial heading does not use Instrument Serif")

    if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"):
        raise AssertionError("Page overflows horizontally")
    if errors:
        raise AssertionError("Uncaught JavaScript error: " + errors[0][:150])
    return {"status": "PASS", "http_status": response.status,
            "final_host": urlsplit(page.url).hostname, "cta": cta,
            "dashboard": "redesigned" if dashboard else "previous_production"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--report", type=Path, default=Path("reports/vercel-guest"))
    args = parser.parse_args()
    url = clean_url(args.url)
    args.report.mkdir(parents=True, exist_ok=True)
    report = {"url": url, "at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "FAIL", "viewports": []}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for name, width, height in VIEWPORTS:
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            device_scale_factor=1)
                    try:
                        result = check_page(page, url)
                        report["viewports"].append({"viewport": name, **result})
                        page.screenshot(path=str(args.report / f"{name}.png"),
                                        full_page=True, animations="disabled")
                        print(f"PASS {name}: HTTP {result['http_status']}, tabs, keyboard, no overflow")
                    except Exception as exc:
                        report["viewports"].append({"viewport": name, "status": "FAIL",
                                                     "reason": str(exc)[:350]})
                        try:
                            page.screenshot(path=str(args.report / f"{name}-failed.png"))
                        except Exception:
                            pass
                    finally:
                        page.close()
            finally:
                browser.close()
    except Exception as exc:
        report["viewports"].append({"viewport": "setup", "status": "FAIL",
                                     "reason": type(exc).__name__})
    report["status"] = ("PASS" if len(report["viewports"]) == len(VIEWPORTS)
                        and all(v["status"] == "PASS" for v in report["viewports"])
                        else "FAIL")
    (args.report / "summary.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
