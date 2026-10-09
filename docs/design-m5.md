# M5 visual system: BasketLens research console

## Reference direction

The user supplied two editorial, green-accented analytics-dashboard references. M5 adapts their visual language to BasketLens while preserving the historical retail-research subject and the app's actual functionality. This is not a recreation of the references' finance products, logos, navigation labels, balances or user profile.

## Component vocabulary

- **Outer frame:** a soft cool-gray browser canvas surrounding a warm, low-contrast app shell. The shell becomes edge-to-edge on small screens.
- **Top bar:** real BasketLens brand mark, fixed historical coverage and a genuine link to the source code. No fake alerts, messages or user identities.
- **Resource rail:** three working outbound links (UCI source, methodology and code). It disappears on mobile, where all essential features remain available in the tab navigation.
- **Navigation:** the four original semantic Streamlit tabs receive a pill treatment. This retains keyboard and screen-reader behavior rather than replacing Streamlit tabs with static HTML.
- **KPI row:** four source-backed measurements with honest labels and explanations. There are no invented growth deltas.
- **Charts:** separate white surfaces for monthly sales, basket composition and product ranking. The area chart uses a restrained green fill and value-aware tooltips; the data remains sourced from the existing validated aggregations.
- **Evidence cards:** accessible reading notes and rule explanations carry the business meaning of Confidence, Lift and later validation.

## Visual tokens

| Role | Color | Purpose |
| --- | --- | --- |
| Canvas | `#E2E4E1` | Separate app from browser viewport |
| App shell | `#F3F4F1` | Low-contrast workspace |
| Card | `#FFFFFF` | Analytics content and native filters |
| Forest green | `#117D58` | Navigation, active actions, data emphasis |
| Ink | `#1F2925` | Headings and numeric content |
| Muted | `#607067` | Labels and methodological context |
| Pale mint | `#E7F1EB` | Interpretation context |

Fonts use a system sans-serif stack. Motion is minimal and respects `prefers-reduced-motion`; focus outlines remain visible. Cards have soft but consistent radii without glassmorphism or ornamental gradients.

## Integrity and scope

Data ingestion, cleaning, train/holdout selection, FP-Growth, Support, Confidence, Lift, recommendation ranking, public data checksum and quality policies are unchanged in M5. All figures in the actual Streamlit application are obtained from the original verified analytics exhibit. The separate HTML design preview clearly labels its chart curves and bar shapes as illustrative. The preview's study counts (40,280 baskets, 32,224 earlier baskets, 8,056 later baskets and 1,500 displayed rules) are previously verified counts, not fabricated business outcomes.

## Tested locally

- Pure-Python dashboard header/card-copy tests, escaping, real-link integrity and responsive CSS assertions.
- Baseline data/model/validation unit tests.
- Static visual prototype in Chromium at 1440px and 390px, with clickable preview navigation, keyboard focus and zero page-level horizontal overflow.
- Python compile check.

**Not yet tested in M5:** Actual Streamlit runtime, Plotly layout in Streamlit, Playwright tests with the official full UCI and public exhibit, production deployment. Those remain part of the release gate before requesting merge approval.

## Files affected by the M5 overlay

- `app/streamlit_app.py`
- `app/assets/basketlens.css`
- `src/basketlens/dashboard_ui.py` (new)
- `.streamlit/config.toml`
- `scripts/browser_smoke.py`
- `tests/test_dashboard_ui.py` (new)
- `docs/design-m5.md` (new)

Use this as a selective patch against the latest GitHub/GitLab `main`, not as a replacement for the verified published exhibit.