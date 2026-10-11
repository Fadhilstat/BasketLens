# BasketLens | Public portfolio launch checklist

This checklist is the authoritative distinction between source quality and public hosting availability.

## Source-verified checkpoints

- Core evidence: the [consulting case study](portfolio-case-study.md) and [methodology](methodology.md) document UCI Online Retail II (2009 to 2011), 40,280 eligible baskets and 1,500 training-selected public rules.
- Dated M7.3 checkpoint: [GitLab post-merge pipeline 2935480963](https://gitlab.com/fadhilrusydih/basketlens/-/pipelines/2935480963) and [GitHub Actions 38126462439](https://github.com/Fadhilstat/BasketLens/actions/runs/38126462439) both succeeded. These are historical results, not a permanent claim about the latest SHA.
- Three separate M6.2 consulting PNG slides are documented in the [three-slide narrative](social/three-slide-story.md), not committed as binary assets.

## Mandatory Vercel guest check for each new public release

1. Open **https://basketlens-fadhil-9768s-projects.vercel.app/** in a signed-out incognito browser. Confirm HTTP 200, the correct dashboard and no login prompt or Vercel authentication gate.
2. Exercise Earlier training / Later holdout tabs with pointer and keyboard. Confirm numbers match the [case study](portfolio-case-study.md).
3. Search and filter Rule Explorer, then use Basket Builder to load SKU 22386 and inspect the 85099B candidate. Later co-occurrence must never be described as incremental uplift.
4. Check desktop, mobile and narrow-mobile layouts, navigation, methodology links and absence of horizontal overflow.
5. Compare [production /release.json](https://basketlens-fadhil-9768s-projects.vercel.app/release.json) `gitSha` with current [GitLab `main`](https://gitlab.com/fadhilrusydih/basketlens/-/commits/main), and check `source: "vercel-git"`, 1,500 rules and the audited public checksum.
6. Inspect required GitLab/GitHub exact-head CI, reviewed source parity and absence of raw invoices, customer identifiers or credentials in public assets. CSV export belongs to the **local** Streamlit research workbench, not the static Vercel site.

A Vercel READY status alone is insufficient. If any guest, integrity or source-provenance check fails, do not advertise that release as verified.

## Copy-ready GitHub About fields

Description:
Auditable market basket analysis with chronological holdout, a privacy-safe Vercel Rule Explorer, Basket Builder and research evidence.

Website:
https://basketlens-fadhil-9768s-projects.vercel.app/

Topics:
data-analytics, market-basket-analysis, streamlit, python, association-rules, retail-analytics, data-visualization, portfolio-project

Review these suggested About fields against the live Vercel site before applying them; this checklist does not itself change repository settings.

## GitHub release

After the guest check passes, publish tag v1.0.0 using [this candidate release note](release-notes-v1.0.0.md). Do not claim that v1.0.0 exists before GitHub reports a published release.

## LinkedIn

Use exactly the three M6.2 PNGs in numbered order, not the earlier nine slides. Review the [slide facts and alt text](social/three-slide-story.md) and [English caption](social/linkedin-post.md).

Association confidence and lift are not experiments. Do not claim incremental sales, profit or modern consumer demand from this historical research.


## Vercel dossier release (2026-10-10)

The only supported public application is the [Vercel dashboard](https://basketlens-fadhil-9768s-projects.vercel.app/), served from canonical GitLab `main` (project `prj_BiqgK3ZnFN9vKURIftb5m1dxB8wF`, Root Directory `site`). The site contains the Rule Explorer and hypothetical Basket Builder. Preview authorization can differ from the production guest configuration.

**Historical M7.3 release checkpoint (2026-10-11):** Vercel deployment `dpl_3yoPq1manXE6926wXximwnYzzw1j` was READY, and anonymous CI verified the production SHA `54dd759c40d364214223de2f25b2f81a03b63adb` against GitLab main. Subsequent releases supersede that checkpoint; always verify the live `/release.json`, not this static SHA.

No hosted Streamlit runtime, VPS, external prediction service or sensitive-data backend is required for public browsing.

## Known hosted workbench issue

On 2026-10-10, the retired Streamlit hosted dashboard failed anonymous desktop/mobile browser QA ([GitLab job 17080255195](https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255195)). It is no longer an active public deployment; its Python/Streamlit implementation remains available for local analysis. Vercel is the only maintained public experience.

## M6.8 publication policy supersedes Streamlit deployment plans

Vercel remains the sole public frontend. Streamlit Cloud plans are historical; Python research and the local Streamlit UI remain reproducible. Each new Vercel release requires green CI, signed-out production guest checks and verified source commit identity.
