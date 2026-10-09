# BasketLens M5.4: legible, coherent Streamlit interface

## Why this milestone exists

The user shared a 1920px screenshot of the live methodology page after M5.3. The background was acceptable, but typography, KPI values, tabs, tables, and research-flow chips remained visually weak or inconsistent. Some rules were cascading from two independent injected stylesheets.

## Implementation

- Consolidate the original and M5.3 CSS into one injected file, with deliberate final typographic rules. The old refinement file is deleted, but the M5.3 visual vocabulary remains.
- Raise body context and accessible navigation labels to 14-16px where useful. Metric labels are 14px and data quality values are 24-30px with tabular figures. The chart typeface and axis labels are also larger.
- Give the actual Streamlit role-based tablist a quiet track and one visibly selected tab. Other tabs only receive subtle hover color, never a second highlighted active state.
- Keep native Streamlit metrics, country filter, charts, tabs, basket builder, search, exports and labels. Add a scoped quality KPI container so quality figures receive consistent styling without applying icon overlays intended for the sales KPIs.
- Replace unstructured pseudo-chips with an ordered 5-step methodological list. Its labels describe the real data flow, not fake navigation. Render it 5 columns on wide screens, 3 on tablet, 2 on small tablet, and a readable vertical sequence on mobile.
- Improve native Streamlit table contrast, cell padding and readable headings. Move deprecated width arguments to current Streamlit width="stretch" API.
- Respect reduced-motion and keyboard focus. No synthetic statistics, user identities, investor language or ornamental icons are introduced.

## QA strategy

Pure-browser layout prototype: 1920, 1440, 1024 and 390px; no document-level horizontal overflow, navigation track filled, metrics 25-30px on quality cards. It is a *layout mock*, not proof of deployed Streamlit.

Actual release gate: GitLab unit tests, fast published-data Chromium UI QA, full official UCI source audit with pairwise/FP-Growth verification, full-data desktop/wide/mobile browser QA and published exhibit parity. GitHub Actions checks mirrored source. The browser test now records methodology screenshots and verifies the semantic ordered data flow and computed KPI text sizes.

## Integrity

The input workbook, source validation thresholds, date quarantine policy, chronological train/holdout logic, association models, evaluation metrics, published checksum-verified aggregate exhibit, and privacy exclusions are unchanged. No deployment to a VPS is required.
