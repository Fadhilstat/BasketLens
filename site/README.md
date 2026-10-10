# BasketLens Vercel companion

This is a public, dependency-free research dossier for BasketLens, not a replacement for the interactive Streamlit research dashboard. All numbers are taken from the verified case study. There is no backend, dataset processing or user tracking in this site.

## Local checks

```bash
cd site
npm test
npm run build
python tests/browser_smoke.py
```

The Chromium smoke uses Playwright and expects an installed Chromium browser (or the Playwright-managed Chromium). The static production output is `site/dist/index.html`.

## Vercel deployment

1. Vercel project `basketlens` is linked to GitLab `fadhilrusydih/basketlens` as the source of truth. GitHub `Fadhilstat/BasketLens` stays the public mirror.
2. Production alias: https://basketlens-fadhil-9768s-projects.vercel.app/
3. Root Directory: `site`. Framework: Other. Build: `npm run build`. Output: `dist`. Runtime: Node.js 22.
4. No secrets, API, database or Vercel server functions are required. Production is publicly configured; previews stay authentication-protected.
5. The release gate `python site/tests/hosted_smoke.py` passed anonymously on 2026-10-10 at desktop and mobile. CI evidence: https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194. Re-run for future frontend changes and review screenshots.

All historical UCI analytics still run in Python/Streamlit. The Vercel companion only presents a selected verified finding and links to source methodology. The linked Streamlit app's anonymous access is not independently verified and is explicitly labeled that way.

## Product choice

Vercel is a hosting/deployment platform, not a design framework. This dependency-free presentation was chosen for fast loading, portable hosting and minimal moving parts. If later we need the full association explorer, dynamic routes or richer state in a unified web app, move the presentation to Next.js and design an explicit, tested data contract. Do not port the CPU-heavy UCI mining pipeline into a Vercel request handler without profiling.


The separate Streamlit hosted workbench failed anonymous guest QA on 2026-10-10. Until access is independently restored, the Vercel site links to the reproducible GitHub case study rather than an unreliable hosted dashboard. Reverify this link after each production deployment. The original Streamlit program and local analyst mode remain unchanged.


## M6.5 retail intelligence dashboard

This source remains a self-contained static site, but the visitor experience is an actual portfolio dashboard rather than a long editorial page. Desktop: forest-green workspace navigation, audit-period banner, verified cohort KPI tiles, interactive training/holdout evidence, diagram of the selected two-product association, inline QA protocol and decision brief. On mobile/tablet the sidebar becomes touch-scrollable horizontal navigation and two-column analysis panels stack vertically. Everything is non-sensitive aggregated history, not a live feed.

Validation before publication: `npm --prefix site test`, `npm --prefix site run build`, `python site/tests/browser_smoke.py`. The browser smoke inspects five widths, keyboard tab interaction, data and method details, alignment and overflow. Guest-verified Vercel deployment is a separate gate after merge to `main`.


## M6.6 real published Rule Explorer

- `index.html` retains the desktop/mobile retail research shell and fixed featured evidence. `explorer.js` renders actual additional rules and search/filter/load-more states using only DOM text nodes, with no server backend or external dependencies.
- `data/basketlens_public_v1.b64` and its SHA256 companion are exact copies of the existing canonical **aggregate-only** publication in `../data/public_demo/`. The site copy is necessary for Vercel Root Directory=`site` build isolation, not a new source of truth.
- `scripts/build.mjs` verifies SHA256, dataset structure, cohort totals, 1,500 rule/evaluation keys, and safe public fields. When the root canonical bundle is available in CI, bytes must match. It emits a compact `dist/explorer.v1.json` with a 2MB maximum test budget and no invoice/customer fields.
- `tests/explorer-data.test.mjs` validates the resulting real artifact, its canonical portfolio pair, and train-only ordering. `tests/explorer_browser_smoke.py` uses clearly synthetic fixture data for **interaction testing only** across five viewports. GitLab hosted smoke is a distinct guest check of the actual live artifact.

Commands: `npm test --prefix site` (build and test); `python site/tests/explorer_browser_smoke.py` (UI fixture); `python site/tests/browser_smoke.py` (existing dashboard regression). After every data refresh: regenerate and review the canonical exhibit first, mirror its bytes and SHA256 into `site/data/`, run full UCI parity checks, then publish. Do not copy raw workbook or customer identifiers into `site`.
