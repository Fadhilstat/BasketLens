# BasketLens M5.6: Methodology flow symmetry
A production screenshot of the five-step research process revealed that badges/icons were left-biased, captions centered, and connectors tied to a fixed transform in the flexible icon column. This caused visibly asymmetric cards.

## Scoped layout correction
- One five-column grid inside each desktop card reserves flexible left/right space around a fixed index (34px), fixed gap (12px) and icon (36px). Their group center equals the card center.
- A full-span caption has a consistent 37px minimum line box. All desktop cards have a common 120px minimum height.
- Decorative arrow connectors are the only absolutely positioned elements. Their width is fixed and position is computed from the 32px parent grid gap, so arrows lie between neighboring card boundaries at the row midpoint.
- At 801-1160px, a six-column grid centers the second row of two cards under the first row of three. At 481-800px, cards become a full-width vertical list. At <=480px, numbers, icons and captions form consistent rows; arrows disappear.
- The five semantic list items remain static explanatory stages, not fake buttons. Focus styles and reduced-motion preferences are inherited unchanged from BasketLens.

## Verification
Standalone Chromium Playwright geometry checks at 1440, 1280, 1024, 800, 390 and 320px passed, including box equality, badge/text centers, arrow gap centers and no horizontal overflow. This mock is supporting evidence, not the real Streamlit application. GitLab browser CI asserts computed real DOM geometry on wide and desktop and keeps full UCI/public exhibit parity gates. No model or source data changed.

See `scripts/browser_smoke.py`, `tests/test_m56_flow_alignment.py`, and the end of `app/assets/basketlens.css`.
