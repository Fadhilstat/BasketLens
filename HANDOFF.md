# BasketLens Handoff

## Project
BasketLens is a Python analytics and Streamlit portfolio application using the official UCI Online Retail II dataset (Daqing Chen, 2019, DOI 10.24432/C5CG6D, CC BY 4.0). Its conclusions describe historical co-occurrence; they do not establish causal sales uplift, profitability, or modern purchasing habits.

## Repositories and release process
- GitLab source of truth: https://gitlab.com/fadhilrusydih/basketlens
- GitHub public portfolio mirror: https://github.com/Fadhilstat/BasketLens
- Milestone M1/M2 merged on both main branches on 2026-10-09, with real-data and desktop/mobile CI passing.
- M3 public Streamlit deployment: feature branch feat/basketlens-streamlit-deploy, GitLab MR !2, GitHub PR #2.
- User explicitly authorized APPROVE PUSH and APPROVE MERGE subject to release QA. No VPS.
- Streamlit Cloud hosting account has not been connected to this chat. Hosted deployment must be verified independently; no URL is live until checked.

## Verified real-data analysis
- Official workbook: 1,067,371 line items and UCI source fingerprint bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980.
- Invoice audit: 83 inconsistent-date invoices, with 5,773 eligible sales lines quarantined.
- Eligible baskets: 40,280; earlier training 32,224; later holdout 8,056.
- Pairwise: 3,622 rules; FP-Growth: 113,001 candidate rules; matched 1-to-1 metrics verified.
- Browser smoke: Streamlit tabs, keyboard focus and screenshots on desktop and mobile passed in GitLab CI.
- No raw customer identifiers or invoices are committed.

## M3 public exhibit
- Full UCI workbook is processed only in disposable CI runner.
- src/basketlens/public_demo.py generates a small, gzip-compressed base64 JSON file with checksum, containing aggregate country/month/product and basket-composition facts plus 1,500 training-selected association rules with later holdout evidence.
- data/public_demo/basketlens_public_v1.b64 and .sha256 are the only public analytic data files in the repository.
- app/streamlit_app.py first uses local full artifacts when available, otherwise the checked public exhibit; this preserves local analyst mode and makes public cloud hosting fast.
- scripts/build_public_demo.py creates the public exhibit; scripts/verify_public_parity.py recomputes and compares the entire exhibit, and scripts/check_public_demo.py tests the published byte-level artifact without network.
- Final GitLab release CI must verify actual committed bundle against a fresh UCI build; run real-data and public-mode browser smoke on desktop/mobile. GitHub Actions must verify published exhibit.

## Known limitations
Candidate SKUs capped by frequency; the public 1,500 rules are a curated training-selected subset, NOT the full 113,001 rules. Holdout evidence is descriptive. Historical sales are positive eligible invoice line amounts, not reconciled net profit/revenue. Country selector affects sales summaries but not the globally trained model. Wilson intervals do not adjust for repeat customers or multiple testing.

## Next action
After GitLab MR !2 and GitHub PR #2 CI pass, merge approved release into main and verify source/data parity. Then use authenticated https://share.streamlit.io to create an app from GitHub Fadhilstat/BasketLens, branch main, entrypoint app/streamlit_app.py. Use Python 3.11 or 3.12 and no secrets. Open the actual app URL and smoke-test charts, explorer, basket builder and exports. Do not claim deployed until URL and hosted app are verified. Record the URL in README and RUN_STATE in a separate documentation-only approved commit once verified.

## M4 Frontend reader experience (2026-10-09)
The original historic-data algorithms, privacy rules and public exhibit remain unchanged.
The new app/assets/basketlens.css and src/basketlens/presentation.py introduce a
responsive editorial layout, country-scope KPIs, plain-English insights, literal SKU
search, a training-derived example cart and explicit confidence/lift explanations.
docs/experience.md records the design and anti-slop decisions.
Unit tests cover view arithmetic, literal search, example basket and rule units.
scripts/browser_smoke.py checks reading order, search, builder interaction, tabs,
focus and viewport overflow on desktop/mobile in both full-data and public mode.
The headless runner must confirm all new flows before the M4 branch is merged.
Streamlit Cloud URL is not yet verified in this conversation.


## M5 reference-inspired UX release

User approved APPROVE PUSH and APPROVE MERGE on 2026-10-09.
Base GitLab main SHA: 0c697cb558f0b87b41daa87e128a8613695f6022.
Base GitHub main SHA: 7a890234b50a029fefb56f9218451f8965ab2137.
Source changes: app/streamlit_app.py, app/assets/basketlens.css,
src/basketlens/dashboard_ui.py, .streamlit/config.toml,
scripts/browser_smoke.py, tests/test_dashboard_ui.py, docs/design-m5.md.
The official public data exhibit, historical business rules, matching algorithms,
chronological split, data quality and privacy exclusions remain unchanged.
Local QA: 35 passed, 2 optional skipped, Python compile passes and verified
M5 patch ZIP source manifest/CRC. Static HTML desktop/mobile concept is
illustrative only. Native Streamlit real-data and public-mode browser QA
remains a required CI gate before merging.
No public Streamlit Cloud URL has been confirmed.


## M5.1 live layout repair

Observed Streamlit screenshots showed floating rail icons overlapping the hero,
negative header margins, too-dense rule tables and unreadable network labels.
M5.1 corrects those issues in the app and CSS, leaves the existing real-data
UCI analytics and public exhibit unchanged, and extends browser QA on actual
element geometry, resource navigation, rule cards, keyboard and mobile overflow.
The full filtered rules are still accessible and downloadable inside a
deliberate expander. See docs/layout-repair-m51.md.
Branch: feat/basketlens-m51-live-layout-fix
Base GitLab main: 88c469e026d470bc8b881682c0e547928492db04
Base GitHub main: 7f0e91a57b93bbb3446977c1133bea7ff5fac15d
Local: 38 passed, 2 optional skipped. CI and hosted verification pending.
User has approved push and merge; do not merge failing CI or substitute
preview/mockup tests for actual Streamlit browser regression.


## M5.2 Hosted QA gate

Added `scripts/hosted_smoke.py`, `tests/test_hosted_smoke.py`, and `docs/hosted-verification-m52.md`. An anonymous fresh-browser workflow checks the live Streamlit UI at desktop/mobile dimensions. Login redirects, failed app loads, missing KPI/pair cards, broken workflows and layout regressions fail the gate. Redacted redirect URLs exclude sign-in payloads. Base GitLab main aa6f4f3bcb171c173f9d3bf903a138a1bf4973eb, GitHub main 9d3870f7b893b62cb321234ce6453c69af83db10. Anonymous deployment access remains unverified and requires owner-side sharing verification.
