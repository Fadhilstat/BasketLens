# BasketLens Release State

Project: BasketLens
Phase: 2
Milestone: M3 Public Streamlit Deployment
Status: PUBLIC_EXHIBIT_REVIEW
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
