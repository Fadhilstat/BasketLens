"""Chromium desktop/mobile smoke for the self-contained Vercel portfolio dossier."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=shutil.which('chromium') or None, args=['--no-sandbox'])
        try:
            for width, height in [(1440, 900), (1024, 768), (768, 900), (390, 844), (320, 700)]:
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
                errors: list[str] = []
                page.on('pageerror', lambda err: errors.append(str(err)))
                page.set_content(html, wait_until='load')
                assert page.get_by_role('heading', name='A pattern in the basket. Not a sales forecast.').is_visible()
                assert page.get_by_role('tab', name='Earlier training').get_attribute('aria-selected') == 'true'
                page.get_by_role('tab', name='Later holdout').click()
                assert page.locator('#chart-value').inner_text() == '67.1%'
                assert page.locator('#count-value').inner_text() == '279 of 416 baskets'
                assert page.get_by_role('progressbar').get_attribute('aria-valuenow') == '67.1'
                page.get_by_role('tab', name='Later holdout').press('ArrowLeft')
                assert page.get_by_role('tab', name='Earlier training').get_attribute('aria-selected') == 'true'
                assert page.locator('#chart-value').inner_text() == '63.1%'
                page.locator('.method-details summary').click()
                assert page.get_by_text('30,317 routine line exclusions').is_visible()
                overflow = page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1')
                assert not overflow, f'Horizontal overflow at {width}px'
                assert not errors, f'JavaScript errors at {width}px: {errors}'
                if width in (1440, 390):
                    page.screenshot(path=str(ROOT / f'preview-{width}.png'), full_page=True)
                print(f'PASS {width}x{height}: evidence, keyboard, audit, overflow, JS')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':
    run()
