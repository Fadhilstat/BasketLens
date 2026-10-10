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


## M5.3 fluid interface refinement
User provided current Streamlit screenshot, accepted a lighter soft-green reference render and authorized APPROVE PUSH and APPROVE MERGE for implementation. The M5.3 overlay in `app/assets/refinement-m53.css` is loaded after the existing M5.1 base CSS. Native Streamlit semantics are retained; scoped keys style overview metrics and 3 sales chart containers. CSS uses restrained forest gradients, consistent surface radii, responsive spacing and native focus/selected states. Mobile avoids content overflow and reduced-motion users do not receive active transitions. `pyproject.toml` requires Streamlit >=1.41 for styleable container keys. `scripts/browser_smoke.py` asserts computed radii, keyed UI hooks and a real desktop icon in the full-UCI/public-data CI. No analytical source or published data mutation. After both green merge gates, verify the latest app view and interactions at https://basketlens-retail.streamlit.app/.


## M5.4 live UI QA / typography fix

User reported the M5.3 public Streamlit screenshot still looked too small and unstructured in Data quality & methodology and approved both release gates. M5.4 merges two prior injected stylesheets into canonical app/assets/basketlens.css, adjusts meaningful visual hierarchy without changing application calculations or published UCI data, adds a scoped quality_kpis container and semantic quality_pipeline() ordered list, improves the actual Streamlit role tablist, typography, chart ticks and table. Actual Chromium browser smoke now verifies 1920/1440/390 screenshots including the methodology tab, four quality metrics and list semantics. A new fast public UI GitLab job catches visual regressions ahead of full-data processing; full UCI + published parity CI stays mandatory. No VPS deployment.


## M5.5 screenshot-approved frontend
The user approved the refined Data quality & methodology reference and explicitly authorized push and merge. Implemented in canonical CSS without replacing any source-backed Streamlit widgets. Four quality cards get meaningful inline-svg pictograms while keeping original labels and numbers. Five semantic ordered process steps gain matching icons and desktop sequence arrows but do not become fake links or buttons. The source-line evidence table gets numerical alignment and scan-friendly striping. Four native tabs use a visible 2-by-2 grid on narrow mobile and retain keyboard/focus behavior. A browser regression test is included. Preserve all analytics and publicly audited UCI data unchanged. Full-data and published browser QA must pass before release.


## M5.6 methodology symmetry fix
The user showed non-centered number/icon groups and connectors in the M5.5 five-step method sequence and authorized push/merge. CSS now uses 5-column index/icon layout within each card so their combined group is centered. Equal-sized desktop cards have a centered label spanning the whole inner card, and absolute-positioned decorative arrows sit at the exact midpoint of each 32px gap. No other application element is absolutely positioned. Tablet rows become balanced 3+2 with the last two cards centered. Mobile is a full-width ordered list. Browser smoke explicitly compares real Streamlit card dimensions, captions, icon badges and connector positions in the desktop and wide viewports. Original UI semantics, UCI pipeline, model output and public exhibit remain untouched.


## M6 portfolio launch and consultant decision brief
On 9 Oct 2026, user requested a consulting-style PNG deck inspired by uploaded navy/green corporate references and approved project code push/merge. The deck uses audited public UCI and verified real selected rule 22386 (Jumbo Bag Pink Polkadot) -> 85099B (Jumbo Bag Red Retrospot). It does not invent sales impact.
New src/basketlens/portfolio_case.py selects a 1:1 pair using only training joint frequency, confidence and lift, then joins later evidence after selection; all shown names are HTML escaped. Four deterministic unit tests protect no-peeking, missing-data, zero-firings and escaping.
Appends a compact business decision brief to Sales overview after product charts. All existing four tabs, models, data, and exports remain unchanged. Existing Streamlit real-data and public browser smoke now checks the brief's presence, four evidence cells and explicit non-causal caveat.
The README is rewritten to remove stale claims that CI/deployment did not exist, and docs/portfolio-case-study.md with an SVG visual summary makes the project understandable to recruiters. Deck PNGs are user-delivered separate artifacts. Public Cloud access must be checked from a fresh anonymous browser before social promotion.


## M6.1 header alignment
User approved launch-oriented refinements and both push/merge gates. M6.1 applies scoped canonical CSS for an 80px content-centered header on desktop, balanced brand and real research links, non-button public status, and a two-row mobile header. Adds CSS/link unit tests and browser DOM alignment assertions on real Streamlit. Source analytics, public exhibit, licensing and original consulting deck are unchanged. A local Chromium prototype passed desktop and mobile viewport checks, but full GitLab CI and hosted verification are required before claiming release success.


## M6.2 handoff
The user asked to finish the BasketLens portfolio launch with push and merge approvals. Three LinkedIn-ready PNG slides were created via PptxGenJS at 1920x1080, plus an editable PPTX. The design follows the authentic forest-green consulting aesthetic and uses only measured UCI basket figures. A publication package ZIP contains exactly three numbered PNGs, the PPTX, the LinkedIn caption and the checklist, delivered as conversation artifacts rather than source Git binaries. The repository contains a source-backed three-slide story, alt text, LinkedIn copy, GitHub About metadata guidance, guest demo test and draft v1.0.0 release notes, plus static QA. Analytics, models, public aggregate exhibit and hosted code have not changed. Github About/release updates require owner UI actions. Guest Cloud access remains unverified; green source CI does not prove public hosting access.


## M6.3 Vercel portfolio companion
User approved push and merge for improving BasketLens to publication-ready quality. M6.3 adds a dependency-free site/ static portfolio dossier with responsive, accessible, product-specific editorial direction, training and later holdout comparison, clear no-uplift boundary, and working links to the canonical Python Streamlit research app and methodology. This is **not** a rewrite of the statistical computation and does not fetch personal or raw source records. It can deploy through Vercel Root Directory=site with output dist and no secrets. CI adds Node static tests and native Chromium smoke, including keyboard/touch and mobile widths. Existing official UCI audit, public data parity, Streamlit regression, and repo sources remain protected. Vercel authenticated project setup and anonymous production smoke require a separate verification gate before claiming a live URL. See docs/vercel-frontend.md.


## M6.4 Vercel hosted verification
Live Vercel project `basketlens` was created under team `team_EaaiSPOJWbSimQAe1AzNVd39` from GitLab `fadhilrusydih/basketlens` and deployment `dpl_33yyNrDmzfaFU7jJfMg7m91GbbTG` is READY after building GitLab M6.3 main `3cf2ca5`. Production guest authentication is disabled, previews retain protection. Public alias https://basketlens-fadhil-9768s-projects.vercel.app/. The source has a static dossier and links to the separate, privacy-safe Streamlit workbench. A remote Chromium guest test is required to independently verify actual access; optional Streamlit probe records the linked application's status. Do not confuse successful build with public guest access. M6.4 pins Node 22 to avoid future major drift and updates deployment instructions; no analytical results are changed.


M6.4 external proof: Vercel anonymous guest browser job https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194 PASSED with HTTP 200, visible case-study content, working earlier/later toggles, keyboard response, readable desktop/mobile and no overflow. README, publication checklist, LinkedIn caption and draft release notes now point to the guest-verified Vercel front door. The Streamlit research application remains a separately checked, optional deep dive; do not claim its guest access unless its optional smoke test passes.


Guest-tested workbench exception (2026-10-10): external Streamlit cloud URL failed anonymous checks on desktop/mobile with content not loading, cause not established. The third M6.4 commit removes the unreliable Streamlit hero link from the portfolio, replaces it with the verified GitHub consulting case study, updates static/hosted smoke tests and documents the independent workbench issue. MR CI accepts the previously published CTA during transition; main post-merge CI requires the corrected CTA. Keep the original Python analysis and Streamlit code intact.


## M6.5 dashboard-first UI release handoff
User requested a stronger match to the approved forest-green retail intelligence dashboard reference and gave exact push and merge approvals. M6.5 replaces the self-contained static Vercel dossier UI with a compact analytics dashboard while preserving factual contract and training/holdout interaction. Desktop is an app shell with left navigation, contrast-rich hero, source-backed KPI tiles, true confidence bars, product pair and compact methodology/decision views. Phone and tablet use responsive horizontal navigation, independent scroll and stacked panels. Node site tests (5 cases) and Chromium smoke (1440, 1024, 768, 390, 320) passed locally. GitLab and GitHub CI plus post-merge anonymous production smoke are still required. Changes do not affect Python ETL/FP-Growth models, quarantine policy, full-UCI validation, aggregate public bundle or source licenses. Do not relink the unreliable hosted Streamlit URL; use the working GitHub case study for deeper research.


## M6.6 source-backed Vercel explorer
User approved further portfolio implementation with PUSH and MERGE. Repo source of truth is GitLab main at 73e66248d180ef7f4c1b80bf18e06eb15eae8c65 before this milestone. Build-internal compressed public exhibit mirror matches canonical `data/public_demo/` SHA256 5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20. Node builds a whitelisted browser JSON artifact for 1500 training-selected rules + matched holdout; all selection and sorting remain training-only. Frontend adds responsive Rule Explorer with actual filtering, pagination and error/retry states; user data is never requested or published. Existing featured hero and historical caveats are preserved. Local Chromium fixtures test interactions, but actual data provenance requires CI and guest production. The separate Streamlit hosted site was previously unable to load anonymously and is not used in CTA. GitLab MR + GitHub PR and exact-head gates must be verified before merging; follow up with auto Vercel guest smoke after deployment.


## M6.7 basket matching vertical slice
Current source prior to run: GitLab main c91559da and GitHub main 3ad6be7b, M6.6 verified Vercel live. The highest-value incomplete visitor flow was composing a basket to trigger rules directly within the publicly accessible Vercel dossier. M6.7 implements a train-only subset matcher using the existing 1,500 audited aggregate rules, maximum 3 SKUs, deduped consequent products and deterministic ranking by antecedent specificity and earlier co-purchases/confidence/lift. Selected items are not real purchases and no cart state is saved. Holdout hits/fires are rendered as observational context only. Existing `explorer.js` shares data/error state with the builder, avoiding duplicate static JSON fetches. Browser UI has no backend/auth/database or external service. Previous Vercel and Streamlit artifacts remain intact.
Testing: actual CI results must be checked at the M6.7 branch head; Node unit tests and fixture browser tests were added. GitLab full-UCI and parity check remains the merge gate even though the research engine is unchanged. After merge, inspect Vercel auto deployment and signed-out hosted smoke on the new Basket Builder. No blind reset of local worktrees, because their status was not fully observable through the connectors. NEXT_ACTION: exact-head CI -> approved merge -> production guest smoke -> continue from newly verified baseline.

## M6.8 approved type refresh and Vercel-only operation

Current verified base is GitLab main `3d5454a0`, GitHub main `16ac89a5`, Vercel public production READY. M6.8 approval is explicit and limited to typography and retiring Streamlit Cloud deployment checks. Functional text and figures use Manrope, editorial headings Instrument Serif with Georgia/system fallbacks; no font binaries bundled. Only optional hosted Streamlit CI probe is retired, while Python research implementation and mandatory numerical audit/guest Vercel CI remain. No new secrets, services or data claims. Check MR/PR and exact-head CI before merge. Rollback: redeploy pre-M6.8 Vercel commit without migration.

## M6.9 motion polish, continuation-safe

Owner explicitly approved a scoped motion/transitions update. GitLab main source of truth was `88ddc2f` and GitHub mirror `f4020a3` before the branch `feat/basketlens-m69-motion-craft`. Pure CSS transitions now unify existing navigational states, tabs, links, filters and Basket Builder. An evidence-bar transition and short value cue follow actual training/holdout changes, with numeric and accessibility updates remaining instant. IntersectionObserver triggers single-use 10px/320ms Web Animations API entrance cues on five research sections, without hiding content. Reduced-motion preference disables CSS motion and skips/cancels JS effects. No additional dependency, JS bundle, data/model transformation, network service, user analytics, backend, VPS or secret scope is introduced. Source, regression and hosted tests were updated; verify live MR and production evidence before claiming release success. Roll back by selecting prior READY Vercel deployment; no database migration exists.


## M7.0 selective analytic CI policy
M6.9 already live at GitLab main `a1bcc3a`, GitHub main `e2fa418`, Vercel READY. The largest observed operational inefficiency is unnecessary full source download and FP-Growth rebuild for each cosmetic/UI-only MR. The current milestone `chore/basketlens-m70-ci-scope` scopes `real_dataset_audit` to merge requests changing `.gitlab-ci.yml`, Python/data/research files and source dependencies, with an explicit optional manual route for otherwise presentation-only MRs. Browser/UI, Node public exhibit checksum, Python unit and anonymous Vercel smoke still run under their existing rules. No runtime services, code, libraries, schema, source datasets or secrets changed. This branch itself changes `.gitlab-ci.yml`, so it must pass full source audit once before merge. Unknown local worktree state remains untouched. NEXT_ACTION: Confirm actual jobs/pipeline exact SHA; mirror GitHub; approve-only merge and production CI verification; later verify that an UI-only MR offers a manual audit without forcing the expensive job.

## M7.0 release checkpoint and focused acceptance test

The prior milestone is no longer pending: GitLab MR !21 and GitHub PR #21 were squash-merged with verified exact-head green CI. GitLab canonical main `d6daab8`, GitHub public mirror main `f459fbf`. M7.0 narrows the expensive `real_dataset_audit` job to analytically relevant MR paths, while UI/docs-only changes retain an explicit manual audit route. Research tests, published exhibit checksum checks, functional browser checks and Vercel signed-out smoke are preserved. Vercel production `dpl_CDhHxEtd8x5qhn2qGGxG3wgUmCoA` READY with no app/data delta.

To demonstrate that the new rules work in practice, this branch deliberately changes only these continuity documents. It must show a manual nonblocking full-audit job in GitLab MR CI. Inspect actual job statuses and required smoke, then verify GitLab and GitHub file parity before using the owner's scoped approve-merge permission. There is no claim of measured runner savings until real elapsed time and resource metrics are compared. No local worktrees, external services or data were modified by this checkpoint.

NEXT_ACTION: Confirm docs-only manual CI gate on the current MR, finish required checks, merge and verify public Vercel readiness; subsequent analytics-code changes must still force `real_dataset_audit` to run automatically.
