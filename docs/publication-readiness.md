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
https://basketlens-retail.streamlit.app/

Topics:
data-analytics, market-basket-analysis, streamlit, python, association-rules, retail-analytics, data-visualization, portfolio-project

The connected GitHub actions in this session do not support modifying repository About fields. The owner can edit the repository About section manually.

## GitHub release

After the guest check passes, publish tag v1.0.0 using [this candidate release note](release-notes-v1.0.0.md). Do not claim that v1.0.0 exists before GitHub reports a published release.

## LinkedIn

Use exactly the three M6.2 PNGs in numbered order, not the earlier nine slides. Review the [slide facts and alt text](social/three-slide-story.md) and [English caption](social/linkedin-post.md).

Association confidence and lift are not experiments. Do not claim incremental sales, profit or modern consumer demand from this historical research.
