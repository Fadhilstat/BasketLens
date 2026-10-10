"""Chromium accessibility and visual regression smoke for the M6.5 BasketLens dashboard."""
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
                errors = []
                page.on('pageerror', lambda err: errors.append(str(err)))
                page.set_content(html, wait_until='load')
                assert page.get_by_role('heading', name='A pattern in the basket. Not a sales forecast.').is_visible()
                assert page.get_by_role('heading', name='Confidence by period').is_visible()
                assert page.get_by_role('navigation', name='Research sections').get_by_role('link', name='Association evidence').count() == 1
                assert page.locator('.kpi-row .kpi').count() == 4
                assert page.get_by_role('link', name='Read full case study').get_attribute('href') == 'https://github.com/Fadhilstat/BasketLens/blob/main/docs/portfolio-case-study.md'
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
                assert not page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1'), f'Horizontal overflow at {width}px'
                assert not errors, f'JS errors at {width}px: {errors}'
                assert page.locator('.hero-banner').bounding_box()['width'] > 250
                # Test layout without including scroll-induced sticky-position artifacts.
                page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
                page.wait_for_timeout(100)
                if width in (1440, 390):
                    page.screenshot(path=str(ROOT / f'preview-{width}.png'), full_page=True, animations='disabled')
                    page.screenshot(path=str(ROOT / f'first-screen-{width}.png'), full_page=False, animations='disabled')
                if width == 1440:
                    sidebar = page.locator('.sidebar').bounding_box()
                    content = page.locator('.main-area').bounding_box()
                    assert sidebar['width'] >= 200 and content['x'] >= sidebar['width'] - 1
                    assert page.locator('.finding-grid').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length') >= 2
                if width <= 390:
                    assert page.locator('.hero-banner').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length') == 1
                print(f'PASS {width}x{height}: dashboard, responsive layout, tabs, keyboard, audit, JS')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':
    run()