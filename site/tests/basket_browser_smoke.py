"""M6.7 browser fixture: example basket, search, candidate matching and fallback."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from explorer_browser_smoke import fixture

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "/": (ROOT / "index.html").read_text(encoding="utf8"),
    "/explorer.js": (ROOT / "explorer.js").read_text(encoding="utf8"),
    "/basket-matcher.mjs": (ROOT / "basket-matcher.mjs").read_text(encoding="utf8"),
    "/basket-builder.mjs": (ROOT / "basket-builder.mjs").read_text(encoding="utf8"),
}
DATA = json.dumps(fixture())


def route_asset(route, fail_data: bool = False) -> None:
    path = urlsplit(route.request.url).path
    if path == "/explorer.v1.json":
        route.fulfill(status=503 if fail_data else 200, body="error" if fail_data else DATA,
                      content_type="application/json")
    elif path in FILES:
        content_type = "text/html" if path == "/" else "text/javascript"
        route.fulfill(status=200, body=FILES[path], content_type=content_type)
    else:
        route.abort()


def run(report: Path) -> None:
    report.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for width, height in [(1440, 900), (1024, 768), (768, 900), (390, 844), (320, 700)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors: list[str] = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.route("**/*", lambda route: route_asset(route))
                page.goto("https://basketlens.local/", wait_until="load")
                page.wait_for_function("window.BasketLensPublicDatasetStatus === 'ready'", timeout=18000)
                page.get_by_role("button", name="Load published example").click()
                assert page.locator("#basket-chosen li").count() == 1
                assert page.locator("#basket-candidates li").count() >= 1
                assert "85099B" in page.locator("#basket-candidates").inner_text()
                assert "279 / 416" in page.locator("#basket-candidates").inner_text()
                page.get_by_role("button", name="Clear basket").click()
                assert "No products selected" in page.locator("#basket-status").inner_text()
                page.get_by_label("Search catalogued product").fill("TEST1")
                page.get_by_role("button", name="Add Synthetic Basket Item 1 (TEST1)", exact=True).click()
                assert page.locator("#basket-chosen li").count() == 1
                assert "S1" in page.locator("#basket-candidates").inner_text()
                page.get_by_label("Search catalogued product").fill("NOT_A_PRODUCT_2026")
                assert "No matching published antecedent" in page.locator("#basket-search-hint").inner_text()
                page.get_by_role("button", name="Remove Synthetic Basket Item 1").click()
                assert page.locator("#basket-chosen li").count() == 0
                assert not page.locator("#basket-error").is_visible()
                assert not page.evaluate(
                    "document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
                ), f"Horizontal overflow at {width}px"
                assert not errors, f"JavaScript exceptions at {width}px: {errors}"
                page.screenshot(path=str(report / f"basket-{width}.png"), full_page=True, animations="disabled")
                page.close()
                print(f"BASKET_UI_PASS {width}px example, search, remove, empty and layout", flush=True)
            failed = browser.new_page()
            failed.route("**/*", lambda route: route_asset(route, fail_data=True))
            failed.goto("https://basketlens.local/", wait_until="load")
            failed.locator("#basket-error").wait_for(state="visible", timeout=12000)
            assert failed.locator("#basket-search").is_disabled()
            assert failed.get_by_role("link", name="Rule Explorer").count() >= 1
            failed.close()
            print("BASKET_ERROR_PASS explicit failed-data state", flush=True)
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("reports/basket-fixture"))
    args = parser.parse_args()
    run(args.report)
