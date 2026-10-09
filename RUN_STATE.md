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
