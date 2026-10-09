# BasketLens Release State

Project: BasketLens
Phase: 2
Milestone: M4 Audience-first Frontend Experience
Status: CI_IN_PROGRESS
GitLab source of truth: https://gitlab.com/fadhilrusydih/basketlens
GitHub public mirror: https://github.com/Fadhilstat/BasketLens
Branch: feat/basketlens-streamlit-deploy
Base GitLab main SHA: 42b6c41e82dabb48767c4b5ec7564198cfb72eaf
Base GitHub main SHA: 0c75d93085e77281cd243d68a634b7637a9143ed

Previous Phase 2 M1/M2 release: merged; CI passed on GitLab real-data dataset and browser QA, and on GitHub.
Verified UCI source: 1,067,371 lines, 40,280 baskets, 32,224 train, 8,056 holdout,
3,622 pairwise rules, 113,001 FP-Growth candidate rules, 83 conflicted source invoices
(5,773 eligible lines) quarantined. These are descriptive relationships, not causal uplift.
No source invoices or personal customer information is included in the repositories.

Current work: create deterministic checksum-verified aggregate-only public bundle from
full offline UCI analysis, adapt Streamlit overview to aggregate basket rollups,
declare deployment dependencies, and test published-mode dashboard in Chromium
on desktop and mobile inside GitLab CI. GitLab CI initially emits the published
bundle in logged chunks for controlled review and subsequent repository commit.

Release gate: do not merge a branch that is missing the validated real-data
published bundle. Re-run unit, data, browser and privacy validation for the
actual committed exhibit. Sync source content to GitHub after GitLab passes.
Streamlit Community Cloud deployment requires an authenticated Cloud account;
no deployed URL or hosted smoke test should be claimed without verification.

No VPS. User has explicitly approved push and merge for this deployment work.
PUBLIC_EXHIBIT_V1: generated from full UCI in GitLab CI and committed for release.
Expected encoded characters: 241100; compressed bytes: 180823; published rules: 1500.
SHA256 of compressed exhibit: 5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20
Source pipeline: GitLab #2928955184, real_dataset_audit job #17049067522.
NEXT_ACTION: Run final CI comparing the committed exhibit with freshly recomputed UCI output, then sync and merge GitLab MR !2 and GitHub PR #2 after green gates. Streamlit Cloud first-time app creation still needs authenticated account access; do not claim live URL until observed.


## M4 UX checkpoint (2026-10-09)
Branch: feat/basketlens-m4-audience-ux
Base GitLab main: 9b1d1b88a366430f28f147458b278c5f712c7b29
GitHub main before sync: ce854e4f51450f9b9715b046b0ef77878c3e2c4a
Changed: reader-first Streamlit app, responsive CSS, literal product search,
training-derived sample basket, plain-language glossary, human-readable network,
quality context, design rationale, and expanded browser QA.
Local QA: 29 passed, 2 skipped (mlxtend and Streamlit not installed locally).
Browser/mobile tests: pending GitLab real-data CI. No new hosted deployment claim.
The UCI public data bundle remains unchanged.
NEXT_ACTION M4: GitLab MR CI including real/public desktop+mobile UX checks.
Only after green QA, sync GitHub and promote main, then verify hosted Streamlit URL.


## M5 release checkpoint (2026-10-09)

Milestone: M5 reference-led responsive dashboard
Status: PUSHED_PENDING_CI
GitLab branch: feat/basketlens-m5-reference-dashboard
GitLab base SHA: 0c697cb558f0b87b41daa87e128a8613695f6022
GitHub base SHA: 7a890234b50a029fefb56f9218451f8965ab2137
User gate: APPROVE PUSH and APPROVE MERGE provided 2026-10-09.
Local tests: 35 passed, 2 optional skipped; compile and ZIP CRC pass.
M5 source: source-backed soft-green UI, compact header, accessible research links,
rounded analytic cards, existing 4 research workflows and exports, unit/browser tests.
Public UCI exhibit and checksum: preserve unchanged.
NEXT_ACTION M5: Check GitLab CI on exact M5 HEAD, browser smoke for both full-data
and public exhibit on desktop/mobile, scan secrets/diffs, then reconcile GitHub
and merge both platforms only on green verification. Verify postmerge CI.
Hosted Streamlit Community Cloud status unknown pending actual authenticated URL.


## M5.1 release checkpoint (2026-10-09)

Milestone: M5.1 screenshot-driven live layout repair
Status: PUSHED_PENDING_CI
GitLab branch: feat/basketlens-m51-live-layout-fix
GitLab base main SHA: 88c469e026d470bc8b881682c0e547928492db04
GitHub base main SHA: 7f0e91a57b93bbb3446977c1133bea7ff5fac15d
User authorized APPROVE PUSH and APPROVE MERGE in current conversation.
Local QA: 38 passed, 2 optional skipped; compile, ZIP CRC, all 10 SHA-256 paths passed.
Changes: remove overlapping absolute shortcut rail, replace negative-offset
main layout, increase card/table legibility, show four unique top product
pairings, collapse noisy network with adjacency list, improve methodology.
Source UCI and public data exhibit are unchanged.
NEXT_ACTION: Verify GitLab CI against real UCI and Streamlit desktop/mobile,
compare GitHub source parity and CI, review security/diffs, then merge both
repositories only on fully green results. Confirm the hosted Streamlit
https://basketlens-retail.streamlit.app after GitHub main updates.


## M5.2 release checkpoint (2026-10-09)
Milestone: M5.2 Anonymous Hosted Release Gate
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m52-hosted-release-gate
Base GitLab main SHA: aa6f4f3bcb171c173f9d3bf903a138a1bf4973eb
Base GitHub main SHA: 9d3870f7b893b62cb321234ce6453c69af83db10
Approved: APPROVE PUSH and APPROVE MERGE on 2026-10-09.
Scope: credential-free Chromium hosted smoke, deterministic unit tests, runbook, continuity update. No UCI/model/public exhibit changes.
Production: ACCESS_NOT_VERIFIED because anonymous Streamlit URL redirects to login.
NEXT_ACTION M5.2: verify real-UCI GitLab CI and GitHub Actions on committed source; merge only on green results; owner to make Streamlit public and rerun hosted smoke before declaring production verified.


## M5.3 design refinement checkpoint (2026-10-09)
Milestone: M5.3 Streamlit fluid surface refinement
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m53-fluid-surface
GitLab main baseline: 5c7441e91a692aac4959a61758da60825c3254af
GitHub main baseline: 9d6939a5e3600bd89051417e89631cd03609c709
User approved APPROVE PUSH and APPROVE MERGE for M5.3 on 2026-10-09.
Changes: scoped responsive visual system, iconographic overview native metrics, targeted chart containers, UI regression tests, Streamlit min 1.41.
Data source, validated UCI rules, model results, aggregate public exhibit and checksum unchanged.
Offline design prototype: desktop/tablet/mobile no horizontal overflow, CSS parser found zero syntax errors. Exact-source GitLab CI and GitHub workflow must pass before merge.
NEXT_ACTION M5.3: verify MR full UCI audit and both desktop/mobile screenshot tests, check Github mirror, merge only after both CIs green, verify hosted UI under fresh app session.


## M5.4 live methodology layout checkpoint (2026-10-09)
Milestone: M5.4 Readable Streamlit Research Interface
Status: PUSHED_PENDING_CI
GitLab branch: feat/basketlens-m54-readable-ui
GitLab base main: 8369dd5c0342a826ec176b3d4c787c20cb4ffbed
GitHub base main: 355a5ccfe9bd9f25804a7aeb8fb69fd8f1685b7c
User granted APPROVE PUSH and APPROVE MERGE for M5.4.
Scope: consolidate CSS, enlarge data-quality values and captions, improve real tabs, stepper, table, chart tick readability, browser smoke screenshots at wide/desktop/mobile, add fast public UI CI.
Local layout prototype: 1920/1440/1024/390px tested; no horizontal document overflow. Real Streamlit CI still required.
The UCI source, algorithms, verified public exhibit and checksum are unchanged.
NEXT_ACTION M5.4: confirm fast public UI and full UCI GitLab MR CI plus GitHub Actions. Merge only with green QA. After release, check deployed UI and capture actual Streamlit screenshot.


## M5.5 screenshot-approved methodology UI release (2026-10-09)
Milestone: M5.5 evidence-first UI, methodology reference edition
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m55-reference-ui
Base GitLab main: f893f8546c7039f212c83e21f646d6efbac03e20
Base GitHub main: d507742501c23c813c76fe2d66bd698cb111e286
User explicitly granted APPROVE PUSH and APPROVE MERGE for this milestone.
Changes: accessible native KPI icons, five-stage evidence flow, right-aligned quality counts, clearer desktop/mobile navigation and new Streamlit browser regression checks.
Unchanged: official UCI dataset, chronological holdout, cleaning, association mining, public exhibit hash, privacy safeguards.
Local approved-reference preview: 9 style checks passed and Chromium responsive checks at 1440, 1024, 390 and 320 pixels; real runtime CI remains mandatory.
NEXT_ACTION: verify GitLab MR unit, public QA, full UCI/browser and public parity; GitHub Actions. Merge only on green, verify main parity and Streamlit Cloud after rollout.


## M5.6 flow alignment checkpoint (2026-10-09)
Milestone: M5.6 Methodology Symmetry Fix
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m56-symmetric-methodology
Base GitLab main: fa9bda429ce912d67b364de809b5668df5a714bb
Base GitHub main: 6365e8a7916632ef7b036b7bee0f789fb28572cc
User granted APPROVE PUSH and APPROVE MERGE for this milestone.
Scope: equal five card geometry and true arrow gap midpoint alignment, centered 3+2 tablet flow, single-column mobile, browser geometry regression tests. No analytic data or source code changes.
Local: Chromium mock at 1440/1280/1024/800/390/320 px passed with zero horizontal overflow. CSS parser passed.
NEXT_ACTION: verify GitLab MR unit, public and UCI real-data/browser CI; GitHub Actions; merge if green and verify main source parity and published deployment.


## M6 portfolio launch checkpoint (2026-10-09)
Milestone: M6 Portfolio Launch and Evidence Brief
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m6-portfolio-launch
GitLab main baseline: 69d95f811577b8704169eec3ac420d027994b883
GitHub main baseline: c9225270962900f7f8390b8de4c9162e015c1ca5
User approved APPROVE PUSH and APPROVE MERGE for consulting-deck and suitable code upgrades.
Change: dynamic training-selected decision brief in Sales overview, four non-leaky unit tests, real full-data/public browser check, rewritten recruiter-focused README, new case study and SVG repository banner.
Verified portfolio case from aggregate public exhibit: 22386 -> 85099B; 1,166 train joint baskets; train confidence .63129399; train lift 6.240128; 416 later fires, 279 hits; later confidence .670673; later lift 6.770604.
No change to official UCI data, cleaning, rule mining, chronological holdout, public exhibit hash, privacy protections, or hosting.
A separate nine-slide 1920x1080 PNG consulting deck was generated locally and verified for slide overflow; it is delivered in this conversation, not checked in to the code repository.
NEXT_ACTION: verify M6 MR GitLab unit/full source/public browser CI, GitHub Actions, then merge both under user's explicit approvals if green. Confirm exact main parity and public hosted status separately.
