# BasketLens | Public portfolio launch checklist

This checklist is the authoritative distinction between source quality and public hosting availability.

## Source-verified checkpoints

- GitLab M6.1 main pipeline: https://gitlab.com/fadhilrusydih/basketlens/-/pipelines/2932826067
- GitHub M6.1 main workflow: https://github.com/Fadhilstat/BasketLens/actions/runs/38024891831
- Verified project methodology and evidence: [consulting case study](portfolio-case-study.md).
- UCI Online Retail II source from 2009 to 2011; 40,280 eligible baskets; published aggregate-only 1,500-rule exhibit.
- The selected 22386 to 85099B pair and its training/holdout counts match the published aggregate evidence.
- Three-slide PNG deck generated at 1920 x 1080. Each slide passed layout overflow QA.

## Mandatory guest check before announcing the demo

1. Open https://basketlens-retail.streamlit.app/ in a new incognito window where you are not signed in to Streamlit.
2. Confirm the app loads without a login prompt or a Python traceback. It must show the M6.1 aligned header.
3. Exercise Sales overview, Association explorer, Build a basket and Data quality & methodology.
4. Search a product, change a relevant filter, add a basket item and download a CSV. Confirm that the CSV has no raw invoice or customer identifiers.
5. Check desktop and narrow mobile layouts. Confirm there are no clipped tabs, unreadable metrics or overlapping quality stages.
6. Verify Dataset, Method and GitHub navigation links lead to the expected real resources.

Until these checks pass, describe the deployment as *not independently guest-verified*, even when CI is green.

## Copy-ready GitHub About fields

Description:
Auditable retail market basket analysis with chronological holdout, a privacy-safe Streamlit dashboard and decision evidence.

Website:
https://basketlens-fadhil-9768s-projects.vercel.app/

Topics:
data-analytics, market-basket-analysis, streamlit, python, association-rules, retail-analytics, data-visualization, portfolio-project

The connected GitHub actions in this session do not support modifying repository About fields. The owner can edit the repository About section manually.

## GitHub release

After the guest check passes, publish tag v1.0.0 using [this candidate release note](release-notes-v1.0.0.md). Do not claim that v1.0.0 exists before GitHub reports a published release.

## LinkedIn

Use exactly the three M6.2 PNGs in numbered order, not the earlier nine slides. Review the [slide facts and alt text](social/three-slide-story.md) and [English caption](social/linkedin-post.md).

Association confidence and lift are not experiments. Do not claim incremental sales, profit or modern consumer demand from this historical research.


## Vercel dossier release (2026-10-10)

- Deployment: https://basketlens-fadhil-9768s-projects.vercel.app/
- Vercel project ID: `prj_BiqgK3ZnFN9vKURIftb5m1dxB8wF`
- Deployed original GitLab main: `3cf2ca5086671f3d8ee33b3d807750803c3f0488`
- Build: READY, GitLab source link active, production public configuration, preview authentication retained.
- **Guest test: PASS**. External GitLab CI Chromium anonymously returned HTTP 200 on 1440, 390, and 320 px. All train/holdout tab interactions, keyboard controls, audit information and overflow checks passed. Evidence: https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194.
- Streamlit remains an independent research app. Its separate guest smoke job is informational and cannot substitute for Vercel site checks.
- Once the guest test is green, prefer the Vercel dossier as the public LinkedIn link. Keep the full code, methodology and limitations prominent.


The Vercel portfolio front door is guest-verified independently of the Streamlit dashboard. Use https://basketlens-fadhil-9768s-projects.vercel.app/ as the primary social and GitHub About website. Publishing a separate interactive Streamlit app URL requires a passing independent Streamlit guest smoke test, so do not interpret the Vercel result as proof of that linked application's availability.


## Known hosted workbench issue

On 2026-10-10, the separate Streamlit dashboard failed its anonymous desktop/mobile browser check (the required content did not load): https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255195 . This does not invalidate the guest-tested Vercel case study, but the Streamlit app must not be promoted as a working public demo until a new smoke test passes. The Vercel front door now directs readers to the available GitHub consulting case study instead.
