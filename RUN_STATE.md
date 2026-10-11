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


## M6.1 publish-ready header checkpoint (2026-10-10)
Milestone: M6.1 Header Alignment and Publication Readiness
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m61-header-polish
Base GitLab SHA: ad6d7c19e625c78ec7e211035d7d575cc060613b
Approved: APPROVE PUSH and APPROVE MERGE (2026-10-10).
Change: improve brand group/link vertical alignment, remove fake-button mode status, mobile two-row navigation; add semantic and actual Streamlit browser tests.
No changes to validated UCI source, models, aggregate public exhibit, privacy or numerical outcomes.
NEXT_ACTION: verify GitLab full UCI, public browser, GitHub CI, then merge, check source parity and public hosting.


## M6.2 final publication kit (2026-10-10)
Milestone: M6.2 portfolio promotion and release readiness
Status: PUSHED_PENDING_CI
Branch: feat/basketlens-m62-publication-kit
GitLab base main: 6b2913061412423690d0d7cf73740284c750d6fa
GitHub base main: 1d7230a5faf64bd0533f09346084f5fe6184744d
User approved APPROVE PUSH and APPROVE MERGE for the milestone.
Changes: exactly three 1920x1080 PNG consulting slides plus editable PPTX delivered separately, documented slide facts, launch caption, guest smoke checklist, GitHub About values, draft v1.0.0 release notes and documentation tests.
Data, models, source UCI files, Streamlit application and published aggregate exhibit unchanged.
Deck PptxGenJS slides_test: PASS, no overflow. Source CI and real browser QA are required.
BLOCKERS: hosted anonymous access has not been verified; GitHub About metadata empty; GitHub release not yet published. Owner action needed for About/release because connected GitHub mutation actions are unavailable.
NEXT_ACTION: green MR CI, merge GitLab/GitHub, verify parity/post-merge CI; owner incognito smoke and metadata/release publication.


## M6.3 Vercel-ready editorial dossier (2026-10-10)
Milestone: M6.3 Evidence-led portfolio frontend
State before remote verification: LOCAL_QA_PASS_REMOTE_PENDING
Approval: user explicitly provided APPROVE PUSH and APPROVE MERGE for this milestone.
Source: site/ static read-only dossier, semantic editorial presentation, interactive training/holdout comparison, evidence and limitations, accessible navigation, error-safe link actions, mobile-first layout.
No changes to validated Python analytics, Streamlit workflows, raw UCI data, or checksum-verified aggregate public bundle.
Local tests: 4/4 Node standard tests; static build; Chromium interactions across desktop/tablet/mobile including keyboard focus and no horizontal overflow. These local results do not prove the Vercel-hosted URL.
Release gates: GitLab MR unit/public UI/full UCI and bundle parity, GitHub PR checks, diff and privacy review, then verified merge and mirrors. Vercel project import and signed-out smoke check remain separate.
NEXT_ACTION: Verify M6.3 exact-head MR and PR CI, merge only on green, then connect `site/` to Vercel and verify anonymous production site before publishing the link.


## M6.4 hosted release verification (2026-10-10)
Milestone: M6.4 Vercel production guest and reproducible release gate
Status: PENDING_REMOTE_GUEST_QA
Approval: user granted APPROVE PUSH and APPROVE MERGE in current turn.
Baseline GitLab main: 3cf2ca5086671f3d8ee33b3d807750803c3f0488; GitHub main: e9c81660ecc01b70dd12a696f9e8053e8bd57b2b.
Vercel team: team_EaaiSPOJWbSimQAe1AzNVd39; project: prj_BiqgK3ZnFN9vKURIftb5m1dxB8wF; production deployment dpl_33yyNrDmzfaFU7jJfMg7m91GbbTG (READY); alias: https://basketlens-fadhil-9768s-projects.vercel.app/
The Vercel build log verified GitLab clone at 3cf2ca5, package build, completed output, and Node engine warning. Follow-up pins Node 22, documents GitLab auto deployment, and adds a remote guest browser test (plus optional Streamlit guest probe).
No modification to UCI source, analytical models, data validation or aggregate-only public bundle.
NEXT_ACTION: Run M6.4 GitLab MR real-dataset + hosted-guest Chromium checks, inspect screenshots and Streamlit access, update published evidence, sync GitHub mirror, merge only on green mandatory QA, and confirm Vercel redeploy on main.


M6.4 verified hosted evidence (2026-10-10): GitLab guest Chromium job 17080255194 PASSED at 1440, 390 and 320 pixels, HTTP 200, live Vercel URL https://basketlens-fadhil-9768s-projects.vercel.app/, correct evidence controls and keyboard focus, zero horizontal overflow. Test artifact: https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194. Python unit and Vercel site jobs also passed at first checkpoint; full-UCI and Streamlit guest probe were still running when this documentation update was committed. Keep the Streamlit status distinct from the Vercel front door.


M6.4 risk correction: Streamlit guest probe 17080255195 FAILED on desktop and mobile because required dashboard content did not load. Cause unknown, do not assert a login redirect. To prevent a dead public CTA, the Vercel dossier now links to the available GitHub consulting case study. The Python Streamlit source remains unchanged. Hosted guest QA permits the prior published CTA on merge-request pipelines, while post-merge main CI must require the corrected CTA. NEXT_ACTION: verify updated source and real-UCI CI, sync GitHub, merge under approvals, then verify the corrected Vercel production CTA.


## M6.5 frontend match to approved reference (2026-10-10)
Milestone: M6.5 dashboard-first visual revision; scope: site UI and tests only
Owner approvals: APPROVE PUSH and APPROVE MERGE granted explicitly on 2026-10-10 in this request.
GitLab baseline: 55793c8c73c4d82ec22bfa895367f3a08a4dd554; GitHub baseline: e41a443a0e98f4eae486141c09d57fe970620812.
The first published Vercel dossier was too article-like for the approved professional retail analytics dashboard reference. The replacement includes meaningful dashboard hierarchy (left workspace rail, 4 metric tiles, source-backed comparative evidence, product-pair graphic, original methodology and decision process). Hero and chart labels show only verified UCI Online Retail II measures. No new claims, chart feeds, ML models, raw source, PII or backend services.
Local QA: `node --test site/tests/site.test.mjs` 5/5 PASS; `python site/tests/browser_smoke.py` PASS on 1440, 1024, 768, 390, and 320 px with keyboard and tab switching, verified figures, no JS errors and no horizontal overflow.
REMOTE STATUS: PENDING exact-head CI and Vercel preview/public production verification. Do not announce the M6.5 website as live until after verified merge, READY production redeploy and anonymous post-merge QA.
NEXT_ACTION: inspect GitLab MR full UCI, UI and site test gates, sync matching GitHub PR, merge with approved gates once green, inspect production preview and no-login hosted QA, then visually compare to approved retail dashboard direction.


## M6.6 published Rule Explorer continuation (2026-10-10)
Approval: user granted APPROVE PUSH & APPROVE MERGE for further BasketLens portfolio readiness in this turn.
Verified baseline: GitLab main `73e66248d180ef7f4c1b80bf18e06eb15eae8c65`; GitHub main `3d8d50a4a8694bde1628b4e57046a3c4b9496712`. Vercel project `prj_BiqgK3ZnFN9vKURIftb5m1dxB8wF` is GitLab-main production with successful M6.5 guest QA.
Scope M6.6: static Rule Explorer on the verified Vercel UI, searchable by SKU/name, min earlier lift/co-purchases and antecedent size, later observation labelled separately. No changes to UCI ETL, FP-Growth, holdout methodology or Python app. Build mirrors canonical `data/public_demo/basketlens_public_v1.b64` as a hash-checked site asset, exports a safe JSON subset from exactly 1,500 curated rules. No customer IDs, invoice IDs, or new success claims.
Local QA before push: Node markup tests 6/6 PASS; existing Chromium dashboard smoke PASS on 1440/1024/768/390/320; offline synthetic Rule Explorer browser fixture PASS at the same widths (search, filters, empty, reset, progressive display, no overflow). Genuine real-exhibit build and hosted guest tests are PENDING CI at creation of this checkpoint; distinguish the fixture checks from real provenance validation.
NEXT_ACTION: Review exact-source M6.6 GitLab and GitHub CI, fix build/schema regression if any, merge only on green, verify Vercel production READY at the approved SHA and anonymous guest explorer interactions, then evaluate whether an additional basket builder provides portfolio value.


## M6.7: source-backed Basket Builder (2026-10-10)
Source-of-truth recovered: GitLab `main` c91559da05d82a5b98f5f8a13c87bc11497a3d23, GitHub `main` 3ad6be7b43e12cea17276e9f6e8934af3f0faadc, Vercel project basketlens production READY. No newer GitLab MR or concurrent GitLab feature branch was observed. No local BasketLens checkout was found in the targeted folders on the available desktop/VPS devices, so local dirty-worktree status remains UNVERIFIED; do not reset unrelated local files.
Milestone branch: `feat/basketlens-m67-basket-builder`. Owner's APPROVE PUSH and APPROVE MERGE in this run apply only to scoped, tested M6.7 changes. Adds pure train-only `basket-matcher.mjs`, a responsive example basket, Rule Explorer data-ready/error sharing, real Node tests, fixture-based Chromium test and Vercel guest acceptance. No raw data, new model, new services or platform secrets.
At documentation authoring: source and browser test gates PENDING. The authoritative result is the exact-sha GitLab MR pipeline and GitHub PR workflow plus post-merge Vercel READY/guest checks. Earlier Streamlit hosted guest failure is still unresolved and non-blocking for Vercel.
NEXT_ACTION: Validate all mandatory M6.7 GitLab and GitHub tests, review branch diff/privacy, squash merge approved MR/PR if green, and verify production Basket Builder on 1440/390/320 guest browsers; then decide whether to prioritise broken Streamlit hosting or performance/CI optimisations.

## M6.8 typography and Vercel-only publication (2026-10-10)

Recovered base: GitLab main `3d5454a0d5d36390b04ea39970776b51adb3e0b9`, GitHub mirror main `16ac89a5406c75afa7e73e8277e6c05572c9574e`, Vercel deployment `dpl_5wwBgBiyEB83ZWVkHeVY4ovENzWW` READY. User granted exact M6.8 APPROVE PUSH and APPROVE MERGE in this conversation. Milestone branch: `feat/basketlens-m68-typography-vercel`.
Scope: Manrope functional UI and tabular numeric styles, Instrument Serif editorial headings, CSS/system fallbacks, source/browser/hosted typography tests, retire optional failing Streamlit Cloud guest CI probe and update public hosting documentation. No changes to UCI data, FP-Growth, Rule Explorer/Basket Builder calculations, Python source, privacy, backend or VPS.
Status when written: PENDING exact-head GitLab and GitHub CI, merge and Vercel public QA. The font pair follows the approved visual direction, not a claimed exact proprietary typeface.
NEXT_ACTION: verify scoped MR/PR CI and diff, merge only if green using owner approval, validate anonymous Vercel production typefaces and responsive research interactions.

## M6.9 interaction-motion polish (2026-10-10)

User granted explicit APPROVE PUSH & MERGE for motion polish. Verified baseline before edits: GitLab main `88ddc2f99b3e24be113b33be8ec46b669dae6e8e`, GitHub main `f4020a3cd016a3e968f90e3abe3df0b5a348faff`, Vercel production READY. No GitLab MR open during recovery. Work is isolated to `feat/basketlens-m69-motion-craft`; no local checkout was changed.
Changes: 160ms hover/selection feedback for existing controls; 360ms confidence-bar width interpolation that never delays evidence text or ARIA; one-time 320ms/10px IO/WAAPI section appearances for five analysis panels; reduced-motion guard/cancellation and regression tests. Content is never hidden pending JS or scroll. No backend, dependency, new data, model, customer/invoice fields, secrets, Streamlit hosting, or VPS workload change.
At document authoring, branch exact-head GitLab/GitHub CI, merge and deployed guest QA are PENDING. Confirm actual evidence using live connectors before marking release completed.
NEXT_ACTION: check M6.9 MR full UCI and frontend/browser tests, verify synced GitHub PR, merge with exact approvals only on green checks; confirm Vercel production READY and anonymous desktop/mobile reduced-motion smoke. After release, visually inspect motion on physical mobile to rule out distraction.


## M7.0 selective full-data CI (2026-10-11)
Verified before branch: GitLab main `a1bcc3a0cb0ff7b1d9c56f6bd0c712540d74a242`, GitHub main `e2fa418a63001270587f15febac802eb31713cd1`, GitLab main pipeline `2933874888` SUCCESS and Vercel `dpl_5nbMtnBEvEML6G9HARtYG6ys7AYw` READY. No open GitLab MRs or new project branches were found. No BasketLens checkout found in common connected desktop or VPS paths; local dirty files remain UNKNOWN, untouched. User authorized APPROVE PUSH and APPROVE MERGE for the current scoped milestone.
Evidence: previously `real_dataset_audit` ran on every MR, downloading 1,067,371 UCI records and verifying FP-Growth 113,001 rules even when only HTML/CSS changed. M7.0 runs full UCI/FP-Growth on MRs that alter analytic code/tests/scripts/data, the historical Python app or CI config; UI/doc-only MRs keep a manual, non-blocking full audit option. Python unit tests, public browser regression, checksum-protected real 1,500-rule Vercel export and guest smoke remain independent gates for their applicable pipelines. This milestone changes CI policy and handoff only, no app, dataset, runtime or model code.
Status at writing: branch `chore/basketlens-m70-ci-scope` is pending exact-head pipeline, mirror review, approved merge and main guest smoke. Note that this CI-file change intentionally triggers one final full audit on its own MR. Do not assume the new selective behavior passed solely because the same MR ran the full audit; check a later UI-only MR, or validate GitLab rule semantics before citing demonstrated savings.
NEXT_ACTION: Verify exact-head GitLab pipeline and GitHub CI, merge only on green plus safe diff, check no loss of public guest checks. On the next UI-only PR confirm real_dataset_audit is manual, while an analytics-code PR schedules it automatically.

## M7.0 release evidence and selective-CI acceptance (2026-10-11)

M7.0 merged from GitLab MR !21 as canonical main commit `d6daab8b294d4ce335fee50e4936db56dbc88dd7`, mirrored in GitHub PR #21 as `f459fbf0926edcc27f88ffbd3dd806cce39d8654`. Exact-head GitLab MR CI `2934202409` SUCCESS: Python unit tests, source UCI/FP-Growth rebuild, public exhibit parity, frontend/Chromium smoke and anonymous Vercel guest check. GitHub Actions on mirror head also SUCCESS. Full audit confirmed the published 1,500 curated rules continue to match original historical data. Vercel production deployment `dpl_CDhHxEtd8x5qhn2qGGxG3wgUmCoA` READY; M7.0 only changes CI and docs, not visitor-facing code.

Purpose of this documentation-only verification branch `docs/basketlens-m70-release-evidence`: verify that GitLab MR `rules:changes` no longer auto-starts the expensive full dataset audit when only RUN_STATE/HANDOFF change. The intended acceptance is `real_dataset_audit` manual/optional while `unit_tests`, `portfolio_site_tests`, `public_ui_smoke` and `hosted_portfolio_smoke` remain required. Do not mark the selective behavior VERIFIED until this MR's actual jobs are inspected. All remote branches and local checkout directories must be read-only until identified. No new backend, VPS service, database, queue, model or runtime dependency.

NEXT_ACTION: Inspect the actual job schedule on the documentation-only MR and ensure `real_dataset_audit` is manual/optional; if successful, merge after green required CI and mirror verification. Preserve full UCI automatic audit for future analytic-code/data/CI changes and record production guest evidence after merging.

## M7.1 canonical exhibit parity repair (2026-10-11)

Recovered source GitLab main `56f243cab1c9a619236301c2eb8fd99ef501629a`; GitLab main pipeline `2934325239` SUCCESS. GitLab MR !22 was merged; its docs-only audit `real_dataset_audit` was manual and optional, and required unit/browser/hosted jobs succeeded. GitHub public mirror latest observed commit `61d2433ed7752cc89f689d197e5b9868c9ff8492`. Vercel production deployment `dpl_9BUxgoYoE5r3G7YeJx9JYKmdx2yj` READY. No local existing worktree was modified: a new clean temporary checkout was used on branch `fix/basketlens-m71-canonical-parity`.

Evidence: `site/scripts/build.mjs` looked for its canonical public exhibit at `../../data/public_demo` relative to `site/`, outside the repository. The optional `existsSync` check silently skipped parity with repository canonical data. The one-line fix points to `../data/public_demo` and a regression test asserts both build source path and exact mirror equality. Local Windows `npm.cmd --prefix site test`: 17/17 PASS. Intentional canonical data corruption caused build rejection (exit 1, SHA256 mismatch), after restoring the canonical data the 17 tests passed again. No UCI/analytic code, manifest values, runtime, hosted services or frontend design changed.

Risks: Vercel Root Directory `site` intentionally isolates the canonical root artifact, so this check runs when a root checkout is present (GitLab/GitHub CI); the pinned published checksum continues to protect isolated Vercel builds. Branch merge and post-merge CI/deployment evidence must be verified before marking published. No additional VPS resources.

NEXT_ACTION: Verify M7.1 exact-head GitLab and GitHub CI and diff, merge only if mandatory checks pass under current scoped approval, check Vercel production READY and anonymous guest smoke, and make sure exhibit parity fails on any future divergent mirror in CI.

## M7.2 release provenance and deployment source attestation (2026-10-11)

Recovered actual baseline: GitLab main `58d3c173fa490dcb682072f4c841b45bc54336ed`; GitHub mirror main `b32b19b0eed237709a2c5152ef4d81fc9cff0f7f`; both post-merge CI SUCCESS. No open GitLab MR or GitHub PR. Vercel production deployment `dpl_5SquqD1djQ1mLQhGJrCXgyqQYJDD` READY; its Vercel build log explicitly confirms cloning `gitlab.com/fadhilrusydih/basketlens`, branch `main`, commit `58d3c17`. Earlier M7.1 parity correction has already shipped. Fresh, clean temporary Windows checkout created for this run; no existing worktree or VPS workload modified.

Problem and evidence: CI guest smoke checked page content, interactions and audited public data but did not prove the public production alias was built from the exact commit tested on GitLab main. A stale production release could pass prior UI smoke. M7.2 fixes this without new server/API, database, dependency or worker: `site/scripts/build.mjs` now emits a minimal public `dist/release.json` with a 40-character source SHA from Vercel's documented `VERCEL_GIT_COMMIT_SHA` (or `CI_COMMIT_SHA` in GitLab builds), the verified UCI aggregate checksum and 1,500-rule count. On Vercel it fails closed if the source SHA is absent or malformed. Local runs explicitly report null/unverified SHA. No arbitrary environment fields, user IDs or credentials are serialized.

`site/tests/hosted_smoke.py` accepts `--expected-sha` to compare Vercel's guest-accessible release stamp with GitLab main, using bounded retries because GitLab CI and Vercel builds run independently. GitLab MR guest smoke continues checking currently published production without requiring unmerged code to be live; GitLab main smoke requires exact release SHA. A fast Python unittest suite validates provenance success/failure without network. Node tests validate the generated manifest and fail-closed source behavior. Since `.gitlab-ci.yml` changed, the M7.2 MR intentionally requires the full existing UCI audit once. Post-release build identity is a public provenance claim, not an integrity guarantee against a compromised deployment platform.

Local development tests before remote push: 23/23 Node PASS and 7/7 Python PASS; Python compile PASS. Exact-head MR CI, Vercel preview build and post-merge production attestation were PENDING at document authoring; do not mark them PASS prematurely. No VPS hosting, service, scheduler or data processing introduced.

First remote gate observation: Vercel M7.2 preview `dpl_AEvJ9UEgmVLu7aHrCK1yh7pCebsb` returned HTTP 200 with exact GitLab branch SHA `e278fae0dfb76f26855c69905df07fc97a880d4f` and the expected public exhibit checksum. GitLab MR !24 first pipeline `2935409423` reported a hosted smoke FAIL because the CI multiline command included doubled literal backslashes and argparse rejected an extra `\\` argument. This is a shell formatting failure, not a portfolio runtime or data failure. The correction uses explicit single-line Python commands in the same job; verify a new exact-head MR pipeline before merging. The real-UCI audit and all mandatory gates remain required.

NEXT_ACTION: Validate the M7.2 GitLab MR exact-head unit/site/real-UCI/browser/guest jobs and check its Vercel preview release.json against the MR commit. Reconcile GitHub mirror, merge only after green CI under scoped approval, then require the GitLab main hosted smoke to verify the exact deployed main commit and confirm GitHub Actions parity.

## M7.3 browser exhibit contract and recovery (2026-10-11)

Recovered current state before edits: GitLab canonical main `94250b00f90fa5457c385cf7f1c7e0b370df9d8f`, pipeline `2935458018` SUCCESS; GitHub public mirror main `dbeb2c4a23028f3f4335dc054383fbb14851e4c8`, Actions `38125272163` SUCCESS. No open GitLab MRs or GitHub PRs. Vercel production `dpl_FTFKTGhgRf1CnFxHkD2bp7WhPW8b` READY and its public /release.json returns that exact GitLab commit, verified exhibit SHA256 `5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20` and 1,500 rules. Prior M7.1/M7.2 temporary Windows checkouts are clean, left untouched. A new clean checkout was made for M7.3, with one branch `fix/basketlens-m73-browser-data-contract`. No VPS, services, database or workers used.

Evidence-based problem: `site/explorer.js` accepted any 64-character lowercase hexadecimal `payload.exhibitSha256` and any cohort after a minimal schema/count check. A syntactically plausible but inconsistent payload could be presented as audited research. No such live corruption was observed. Scope is browser-side integrity and recoverability, not a new mining/model implementation.

Minimal change: pin the browser payload to the already published SHA256 and audited chronological cohort (40,280 total, 32,224 earlier, 8,056 later). A mismatched fingerprint or cohort follows the existing error state and does not reach Basket Builder. Extend the clearly synthetic browser fixture to use approved metadata, and test adversarial metadata followed by a successful Retry for both Explorer and Basket Builder. A Node test compares the browser pin with the built real exhibit to prevent accidental version drift. This is a version compatibility check, not independent cryptographic verification of the JSON bytes; build-time source parity, public SHA256 and post-deployment source attestation remain separate controls.

Baseline published explorer JSON size locally measured 431,749 bytes, below the existing 2 MB budget. No performance refactor warranted. Local checks before push: Node `npm --prefix site test` 24/24 PASS, Python browser fixture files syntax compile PASS, `git diff --check` PASS. Live browser regression and GitLab/GitHub exact-head CI are not yet marked PASS at document authoring; check real statuses before merge. No UI redesign, external tracker, dependency, secret, backend or VPS workload.

NEXT_ACTION: Verify GitLab MR head browser fixtures (including wrong checksum/cohort rejection and Retry), Node tests and guest smoke; verify GitHub mirror CI and Vercel preview. Merge only if exact-head mandatory gates pass and no concurrent file drift. After merge verify canonical main guest browser and /release.json SHA, then record results and choose next demonstrated portfolio value gap.

## M7.4 public publication and documentation clarity (2026-10-11)

Recovered baseline before change: GitLab canonical main `54dd759c40d364214223de2f25b2f81a03b63adb`, pipeline `2935480963` SUCCESS; GitHub mirror main `d2f374a23f41298e657f2421771c73e5dcb9f71f`, Actions `38126462439` SUCCESS. Zero open GitLab MRs/GitHub PRs. Vercel production `dpl_3yoPq1manXE6926wXximwnYzzw1j` READY; public release.json HTTP 200 matched GitLab main, approved exhibit fingerprint and 1,500 rules. Existing M7.1-M7.3 temporary remote worktrees were read-only inspected and clean, not modified. Repo has no standalone CHANGELOG/NEXT_ACTION; continuity uses RUN_STATE and HANDOFF.

Problem evidence: README and publication checklist still directed readers to Streamlit Cloud or described it as the public demo, despite the later M6.8 Vercel-only policy. README was pinned to obsolete M6.3 deployment and advertised workbench interactions not available on static Vercel. Verification docs implied automatic full-UCI audit in all MRs, contradicting selective .gitlab-ci.yml. Candidate release notes linked the retired Streamlit Cloud URL. This is misleading to hiring reviewers and future coding agents, not a defect in production data.

M7.4 repairs seven documentation/copy files and adds three fast Node publication contract tests under site/tests. Public Vercel Explorer and Basket Builder are explicitly separate from locally reproducible Python/Streamlit research. Release guidance now uses current public /release.json versus GitLab main, not stale deployment ID. Historical M7.3 SHA is labelled as a dated checkpoint, and the v1.0.0 candidate remains DRAFT, not a published release. Relative Markdown links and Vercel-only public claims are guarded by Node tests. Selective CI is accurately documented: full UCI auto audit for research/CI changes; manual nonblocking for docs-only updates.

No changes to site runtime/frontend JS, historical dataset, model, research source, CI config, secrets, infrastructure, API or VPS. Source was updated via a new independent GitLab branch `docs/basketlens-m74-publication-contract`; earlier remote worktrees were preserved. The first scoped docs commit is `d28bc2294bef68dc7e231dc4f8f45b85b14fe14d`. Full exact-head MR test status, GitHub mirror merge, production guest verification and resource outcome are pending at this pre-release checkpoint. Do not mark PASS prematurely.

NEXT_ACTION: Verify M7.4 GitLab MR docs-only selective job and all required unit/site/browser/Vercel guest tests at exact commit, review diff and secrets, mirror GitHub with file-by-file parity; merge only after green gates. On GitLab main post-merge, prove Vercel /release.json SHA equals new GitLab main and guest smoke passes, then verify GitHub Actions. Afterwards prioritize evidence-based improvement of analyst decision-clarity, not speculative profitability claims.

M7.4 first MR pipeline `2935549547` failed before release. Existing Python publication test `tests/test_publication_m62.py` requires literal checklist text `incognito` and `login prompt`, plus release candidate text `Status: DRAFT` and `does not publish a tag`. The new Node docs test also overfit to the literal phrase `current GitLab` instead of verifying the URL. The scoped repair restored those truthful legacy phrases and changed the Node check to inspect GitLab's `/commits/main` path. Original browser/runtime and research code remain unchanged. A new exact-head CI pipeline must pass before merge; do not rely on failed `2935549547`.

## M7.4 CI-quota incident and independent Chromium fallback (2026-10-11)

Following the documentation-only MR !26 branch commit `0cbb82d4c916b95edf3a4d653116d1d41e318906`, GitLab `public_ui_smoke` job `17091925495` **never started**, failing `stuck_pending_no_matching_runners` after 4407.86 queued seconds. Retrying the exact job created `17092856820`, which GitLab immediately failed with `ci_quota_exceeded` and no runner/test execution. This is not evidence of a code/browser test failure. GitLab MR other mandatory `unit_tests`, `portfolio_site_tests` and `hosted_portfolio_smoke` had PASS; `real_dataset_audit` was manual/nonblocking as configured for docs changes. GitHub prior `test` and `portfolio-site` jobs passed. A local clean Windows checkout at the exact branch SHA passed 27/27 Node tests and 4/4 Python publication tests with clean diff, and prior M7.3 UI/data code was unchanged.

Minimal operational workaround for depleted GitLab quota: extend existing GitHub Actions `.github/workflows/ci.yml` Python `test` job for pull requests only, to install Playwright Chromium then run the same public provenance unittest, local research Streamlit browser smoke, static dashboard, Explorer and Basket Builder browser scripts used by GitLab `public_ui_smoke`. Reuse the existing Python dev-dependency environment, cap job at 25 minutes, avoid persistent services, new workers or a heavy dataset re-download. No GitLab CI gate was deleted, marked green or skipped; historical GitLab quota failures remain recorded. The fallback is acceptable only if exact-head GitHub Actions Chromium steps actually complete PASS and source parity, Vercel guest access, branch conflict checks and test scope also pass. A failed GitHub browser test remains a release blocker. No VPS work.

NEXT_ACTION: Verify the GitHub PR exact-head 25-minute test job including all five Chromium/Streamlit script commands, its portfolio-site job, and GitLab/GitHub file parity. If tests pass, confirm scoped owner approval and safe MR/PR merges despite the explicitly disclosed GitLab quota-only failure; verify newly deployed Vercel SHA and signed-out guest behavior, and write an accurate release checkpoint. If fallback fails, preserve both branches and fix reported test defects before merging.
