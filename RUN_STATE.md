# RUN_STATE.md

> Continuity checkpoint for the current local development branch. No fabricated real-data results.

## Project
- Name: BasketLens
- Scope: UCI Online Retail II market basket research and cross-selling decision support
- Phase: 2 (technical implementation, approved)
- Updated: 2026-10-08 23:25 Asia/Jakarta

## Git
- Branch: feat/basketlens-m1-m2
- HEAD: 41afe37b626047d613d22eaeb5bea0519ca44217 (first local commit; see current git HEAD after checkpoint commit)
- Target: main, not yet verified on remotes
- Base SHA: NONE
- Working tree: committed locally; no push
- Commits ahead of base: 1 initial root commit

## Current milestone
- Name: M1 data foundation plus M2 analyst dashboard source
- Status: IN_PROGRESS
- Verified locally: source logic, 22 unit and CLI tests, Plotly affinity network generation, synthetic pipeline scaling, independent artifact math verification
- Pending: official UCI data validation, genuine mlxtend run, actual Streamlit runtime/browser, CI, deployment

## Continuation
- Last completed action: built release-source ZIP and verified source integrity after expanded tests, validation and documentation
- Current unfinished work: obtain verified repo destinations and download official UCI workbook, install full dependencies, run full data pairwise/FP-Growth, evaluate model output, actual Streamlit and browser QA
- NEXT_ACTION: In a working-network Python 3.11 environment, install dependencies (`python -m pip install -e '.[dev]'`), execute `python -m basketlens.cli doctor`, download original UCI workbook, run full dataset pairwise then FP-Growth, and execute `python -m basketlens.cli verify` after each run
- THEN:
  1. Review source exclusions, potential duplicates, invoice conflicts, counts, candidate coverage and temporal rule stability
  2. Run actual `streamlit run app/streamlit_app.py` and verify desktop/mobile, keyboard, empty-data, data-loading, chart, export and basket-selection behaviour
  3. Run complete release gate, secret scan and CI after separate authorized push
  4. Make 1 to 3 meaningful local commits using user-configured author only after confirmed release readiness; reconcile with remote state
  5. Create verified Google Drive Latest checkpoint and request exact APPROVE PUSH before any remote push; later request APPROVE MERGE separately

## P0
- Multi-sheet UCI ingestion and schema adaptation: CODE READY, fixture tested
- Missing/cancelled/nonmerchandise/non-finite-line cleaning: CODE READY, fixture tested
- Explicit conflicting-invoice fail/quarantine policy: CODE READY, fixture tested
- Basket creation and chronological train/holdout split: CODE READY, fixture tested
- Sparse pairwise rule baseline: CODE READY, fixture tested, synthetic scale run
- mlxtend FP-Growth: CODE READY, actual runtime NOT RUN (dependency unavailable)
- Independent output verification and atomic build activation: CODE READY, fixture and tampering tests passed
- Raw official UCI source evaluation: BLOCKED by runtime DNS
- Streamlit actual UI: SOURCE READY, runtime and visual verification BLOCKED (dependency unavailable)
- CI workflows: DEFINED, not run remotely

## P1
- Deterministic candidate SKU selection and coverage diagnostics: IMPLEMENTED, tested
- Bounded Plotly/NetworkX product-affinity map: IMPLEMENTED, unit tested without Streamlit runtime
- Holdout evidence labels, approximate Wilson intervals, evidence-ranked suggestions: IMPLEMENTED, tested on fixtures
- Filtered exports, product search, country overview controls: SOURCE READY, browser QA pending
- Cohort segmentation experiments and robustness sensitivity analysis: REMAINING

## P2
- Causal cross-sell experiment, profit-sensitive bundling and backend API: NOT IMPLEMENTED; require live business data and justified need

## Quality
- `python -m pytest -q`: 22 passed, 2 skipped (mlxtend and streamlit absent), 2026-10-08
- `python -m compileall -q src app tests`: PASS
- Synthetic-only 48,000-line / 12,000-basket pipeline scale run: PASS, 870 pairwise rules, artifact validation PASS; not a benchmark on real UCI data
- Staging artifact tampering test: PASS (corrupted support rejected)
- Source text no-em-dash check: TO VERIFY in final gate
- Source security/secret scan: TO VERIFY in final gate
- Wheel build: NOT VERIFIED (pip wheel build timed out in this runtime)
- Full UCI workbook analysis: NOT RUN (DNS unavailable)
- Actual Streamlit rendering, browser and accessibility QA: NOT RUN
- CI and deployment smoke tests: NOT RUN

## Data and product state
- Data: official workbook not obtained; all test datasets are explicitly synthetic
- Backend: reproducible CLI + analytical pipeline + output verifier
- Frontend: implemented Streamlit source with interactive explorer, affinity graph, decision candidate export and data quality views
- Prototype: SOURCE ONLY; not demonstrated in browser
- Production: NOT DEPLOYED

## Google Drive
- Latest checkpoint: NOT CREATED (milestone still blocked on real-data and runtime gates)
- Local ZIP: controlled handoff only, not a Drive backup

## Remote
- GitLab: inspected; no BasketLens project in accessible scope, no push/MR
- GitHub: inspected; no BasketLens repository owned by linked user, no push
- CI: NOT RUN

## Known blockers
- Runtime cannot resolve UCI or PyPI DNS; container.download also failed
- mlxtend and Streamlit are absent
- Local Git author uses verified authenticated GitLab profile; first commit created
- Full packaging wheel build timed out; use ZIP of local source for continuation

## Do not repeat
- Do not restart source coding, tests, or documentation from scratch
- Preserve implemented statistical and validation integrity improvements
- Do not present synthetic fixtures/stress data as real retailer findings
- Do not claim observational lift as causal uplift, conversion increase or profit
- Do not push, create an MR, merge or deploy without applicable release gates

## Approval required
- Phase 2: APPROVED by user, confirmed continuation
- Push: APPROVED on 2026-10-08, pending destination and release prerequisites
- Merge: APPROVED on 2026-10-08, conditional on CI, diff review, runtime and real-data verification
