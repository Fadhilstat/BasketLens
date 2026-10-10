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

1. Import GitHub `Fadhilstat/BasketLens` into a personal Vercel account.
2. Set **Root Directory** to `site` and **Framework Preset** to `Other`.
3. Use the committed `vercel.json`: build command `npm run build`, output directory `dist`.
4. Do not configure secrets, a database or an API. There are no runtime secrets.
5. Verify the public URL as a logged-out guest on desktop and mobile and run the same evidence toggle and source-link checks before posting the URL.

All historical UCI analytics still run in Python/Streamlit. The Vercel companion only presents a selected verified finding and links to source methodology. The linked Streamlit app's anonymous access is not independently verified and is explicitly labeled that way.

## Product choice

Vercel is a hosting/deployment platform, not a design framework. This dependency-free presentation was chosen for fast loading, portable hosting and minimal moving parts. If later we need the full association explorer, dynamic routes or richer state in a unified web app, move the presentation to Next.js and design an explicit, tested data contract. Do not port the CPU-heavy UCI mining pipeline into a Vercel request handler without profiling.
