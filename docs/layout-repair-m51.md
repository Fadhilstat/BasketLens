# BasketLens M5.1: live-layout repair

Status: local patch ready for controlled GitLab CI and reviewer approval. Not yet deployed.

## Screenshot audit

The production screenshots from `basketlens-retail.streamlit.app` revealed:

1. A resource icon rail overlaid the hero title and body copy.
2. The header was widened using negative margins while the page reserved 109px of unused left padding.
3. A broad CSS selector styled every `stVerticalBlockBorderWrapper`, including internal layout wrappers that were not intended to be panels.
4. The first association results displayed 80 grid rows, including the same pair in opposite directions, with long all-caps labels.
5. The affinity map was expanded by default and placed overlapping labels on dense clusters of nodes.
6. Several captions, panel labels and data explanations were too small to read comfortably in a full-size browser.
7. The methodology section expanded into a long wall of text instead of offering an optional deep dive.

## Corrections

- Remove absolute positioning of the resource rail completely. Official data, methodology and GitHub links are now text-labelled, keyboard-accessible links inside the normal-flow header.
- Replace negative margins, custom 109px left inset and forced page height with one centered grid and uniform padding.
- Scope CSS to deliberate components and avoid styling every Streamlit vertical block wrapper.
- Show the four most frequent **unique** one-to-one training pairings in readable two-column cards (one card per undirected pair). Each card explains direction-specific confidence clearly.
- Preserve the complete filtered rule table and CSV download inside an opt-in expander. The full set is not discarded or recalculated.
- Collapse the network by default, reduce nodes and edges, omit colliding on-plot labels, and add a readable list of the same connections. Hover/tap still exposes the underlying product name.
- Increase body, caption, input-label and chart readability without altering statistics or colors chosen for the project.
- Format the eight data-quality reasons as a simple static table; keep the full methodology available in a collapsed section.
- Keep data and analysis unchanged: official UCI source, chronology, source audit, baskets, rule metrics, holdout, published 1,500-rule exhibit and SHA-256 remain untouched.

## Tests

Local tests: 38 passed, 2 optional skipped (Streamlit and mlxtend unavailable in local environment). Python compilation passed. The CSS parser reported zero errors. Escaped HTML links and unique pairing selection were independently inspected. Green-on-white foreground contrast measured 5.31:1, muted-on-shell 4.96:1, and main copy-on-shell 7.41:1.

Updated CI browser smoke checks: visible brand and navigation, 3 working research links, no floating rail, no overlap between header and hero, aligned left edges, 4 real KPI cards, unique pairing cards, searchable rules, basket example, methodology tab, keyboard focus, and no horizontal page overflow. Both full-data and public-mode desktop/mobile must pass in GitLab CI **before merge**.

## Release checklist

1. Create `feat/basketlens-m51-live-layout-fix` from verified GitLab main SHA `88c469e026d470bc8b881682c0e547928492db04`.
2. Overlay only the changed code, test and documentation files in the patch onto current GitLab main. Do not upload raw UCI files or the old local README, RUN_STATE or HANDOFF into the repository.
3. Commit once, open a single MR to `main`, wait for real-data GitLab CI and actual browser screenshot tests.
4. If green, mirror the exact text files to a GitHub feature branch based on GitHub main `7f0e91a57b93bbb3446977c1133bea7ff5fac15d`.
5. Check GitHub Actions, diff security, and parity. Merge only after authorization and green checks.
6. Confirm Streamlit Community Cloud updated from GitHub main, visually compare dashboard with the supplied screenshots, and test the live URL on desktop/mobile.

The Streamlit Cloud owner-only `Manage app` button and the platform toolbar are host controls, not elements drawn by BasketLens. Those controls may still be visible to a signed-in owner.