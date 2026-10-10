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
