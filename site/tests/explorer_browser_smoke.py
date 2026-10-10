"""Offline browser fixture for Rule Explorer UI states, not analytical validity."""
from __future__ import annotations

from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def fixture() -> dict:
    rules = [{
        "a": [{"sku": "22386", "name": "Jumbo Bag Pink Polkadot"}],
        "c": {"sku": "85099B", "name": "Jumbo Bag Red Retrospot"},
        "joint": 1166, "confidence": .631294, "lift": 6.24,
        "fires": 416, "hits": 279, "holdoutConfidence": 279 / 416, "holdoutLift": 6.77,
    }]
    # Intentionally synthetic names/counts to test rendering, never shipped as analysis.
    for number in range(1, 1500):
        rules.append({
            "a": [{"sku": f"TEST{number}", "name": f"Synthetic Basket Item {number}"}],
            "c": {"sku": f"S{number}", "name": f"Synthetic Related Item {number}"},
            "joint": max(1, 600 - number // 3), "confidence": .4,
            "lift": 1.5, "fires": 0, "hits": 0, "holdoutConfidence": None, "holdoutLift": None,
        })
    return {"schema": "basketlens.rule-explorer.v1", "exhibitSha256": "a" * 64,
            "ruleCount": len(rules), "rules": rules}


def run() -> None:
    html = (ROOT / 'index.html').read_text(encoding='utf8')
    script = (ROOT / 'explorer.js').read_text(encoding='utf8')
    data = fixture()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=shutil.which('chromium') or None,
                                             args=['--no-sandbox'])
        try:
            for width, height in [(1440, 900), (1024, 768), (768, 900), (390, 844), (320, 700)]:
                page = browser.new_page(viewport={'width': width, 'height': height})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                # Network access may be disabled in CI. Mock only the transport,
                # never claim this synthetic fixture validates UCI numerical parity.
                page.set_content(html, wait_until='load')
                page.evaluate('data => { window.fetch = async () => ({ok: true, json: async () => data}); }', data)
                page.add_script_tag(content=script)
                page.locator('.rule-row').first.wait_for(timeout=15000)
                assert page.locator('.rule-row').count() == 8
                assert '1,500 of 1,500' in page.locator('#rule-summary').inner_text()
                page.get_by_role('button', name='Show 8 more rules').click()
                assert page.locator('.rule-row').count() == 16
                page.get_by_role('searchbox', name='Product name or SKU').fill('22386')
                assert page.locator('.rule-row').count() == 1
                assert '1 of 1' in page.locator('#rule-summary').inner_text()
                assert page.locator('.rule-row').first.get_by_text('279 / 416').is_visible()
                page.locator('#rule-lift').select_option('10')
                assert page.get_by_text('No rules match these filters.').is_visible()
                page.get_by_role('button', name='Reset filters').click()
                page.locator('.rule-row').first.wait_for()
                assert page.locator('.rule-row').count() == 8
                assert page.locator('#rule-error').is_hidden()
                assert not page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1'), width
                assert page.get_by_role('navigation', name='Research sections').get_by_role('link', name='Rule explorer').count() == 1
                assert not errors, errors
                print(f'PASS fixture explorer {width}px: search, filters, empty, reset, pagination, no overflow')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':
    run()