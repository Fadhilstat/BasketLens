# HANDOFF.md

## Project and objective

BasketLens is a hire-ready, portable local-first Market Basket Analysis application for historical non-store UK giftware transactions. It investigates product co-occurrence, audits exclusions, checks associations on later invoices and helps analysts shortlist cross-sell tests. Target roles: Data Analyst, BI Analyst and Analytics Engineer. It cannot prove that displaying recommendations increases sales or margin.

## Current phase and milestone

Phase 2, M1 Data Foundation plus M2 Streamlit Analyst Experience. STATUS: IN_PROGRESS. User approved Phase 2 and approved continuation. User approved push and merge, subject to release gates. The local branch is `feat/basketlens-m1-m2`; first local commit is 41afe37b626047d613d22eaeb5bea0519ca44217, using the verified connected GitLab profile as author. No remote repository for BasketLens is currently owned by the linked GitLab/GitHub accounts, so no push or merge has occurred.

## Architecture and implemented source

- `src/basketlens/ingestion.py`: two-sheet official UCI XLSX or CSV adapter, canonical names and source lineage.
- `cleaning.py`: source line eligibility, non-finite numeric rejection, cancellation and service exclusions; explicit fail-closed invoice date/country conflict or optional full-invoice quarantine.
- `mining.py`: deterministic top-SKU selection, candidate coverage reporting, sparse pairwise baseline and mlxtend FP-Growth (max itemset length 3).
- `evaluation.py`: strictly chronological training/holdout split and later conditional co-occurrence checks.
- `insights.py`: descriptive repeat-evidence labels, Wilson intervals and evidence-ranked candidate suggestions.
- `network.py`: bounded, unique pairwise product affinity network with deterministic layout.
- `reporting.py`: no-PII product/country/month/basket summaries.
- `validation.py`: independent arithmetic, consistency and identifier-exclusion checks on all generated artifacts.
- `pipeline.py`: stages reports, verifies the complete output, and swaps it into place with recovery for failed activation.
- `download.py`: direct official UCI ZIP fetch with limits and digest metadata.
- `cli.py`: `doctor`, `download`, `build` and `verify` commands.
- `app/streamlit_app.py`: overview, association explorer, bounded graph, later evidence with intervals, product-based suggestions, CSV/JSON exports, and methodology/data-quality checks.
- `tests/`: 22 passing offline tests plus 2 optional runtime integration modules, all using synthetic-only fixtures.
- `docs/`: architecture, methodology and step-by-step verification protocol.
- `.gitlab-ci.yml`, `.github/workflows/ci.yml`: CI entrypoints on supported runners after approved push.

## Source and licensing

Dataset: [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), Daqing Chen, UCI Machine Learning Repository, DOI 10.24432/C5CG6D, CC BY 4.0. Approximately 1,067,371 original line records spanning 2009 to 2011. It was not downloaded or processed here, because network DNS was unavailable. No original rows, trained real-data rule findings or validated production metrics are included in the local handoff ZIP.

## Verified locally on 2026-10-08

- Python syntax compilation passed for `src`, `app` and `tests`.
- `python -m pytest -q`: 22 tests passed, 2 skipped because genuine mlxtend/Streamlit runtimes were missing.
- Synthetic-only stress run: 48,000 lines/12,000 baskets, 870 pairwise rules, and independent output verification passed. Results have no relationship to the UCI retailer.
- The verifier rejected intentionally tampered Support and a subsequent rebuild restored valid output.
- Source/output SHA format, quality arithmetic, aggregates, temporal rule arithmetic and non-export of customer-ID columns are enforced.
- Affinity network code is tested as a Plotly figure, but was not rendered within Streamlit in a browser.
- Wheel packaging attempt timed out. Do not claim wheel build success.

## Pending high-priority checks

1. Obtain official UCI XLSX from source and inspect SHA, two sheets, actual row counts and date coverage.
2. Install all dependencies on a reachable Python 3.11 system.
3. Run `python -m basketlens.cli doctor` and then `python -m basketlens.cli build --algorithm pairwise`; run `verify` and examine quality output.
4. Run full FP-Growth and `verify`; compare identical 1-to-1 rule metrics between pairwise and FP-Growth.
5. Inspect candidate product and basket coverage, full-data invoice conflict counts, time cutoffs and holdout stability; avoid reporting highly sparse spurious rules.
6. Launch Streamlit locally, test UI state and real browser/device interaction, responsive rendering, keyboard focus and downloads.
7. Complete release gate and backup; then request literal APPROVE PUSH. Later request literal APPROVE MERGE after remote CI/MR QA.

## Known limitations and design decisions

- Non-merchandise service-code exclusions are conservative and may need auditing for the real workbook.
- Positive line amounts are not reconciled net sales, profit or margin.
- Analytic basket support counts all eligible invoices, including single-product baskets.
- The product candidate cap can hide associations; the manifest reports coverage.
- A holdout Wilson interval assumes approximate binomial independence, which may be violated by repeat customers. No multiple-testing correction or treatment-effect model exists.
- Global association rules do not change with the sales overview country selector.
- Historical associations from 2009-2011 cannot be assumed to generalize to current retail operations.
- Raw data, local source files, and generated artifacts stay gitignored, and no customer ID is persisted in analytical outputs.
- No secrets are required; do not add API credentials to git.

## Exact continuity instruction

Read `RUN_STATE.md`, inspect local Git and source, preserve existing files, obtain real dataset/install prerequisites, run full model and browser QA. Continue from that blocker, not from brainstorming or recreating modules. The local source ZIP is a recovery artifact, not a repository release. Git remains the intended code authority, Drive an optional verified recovery checkpoint, and GitLab a controlled release surface with explicit push and merge approvals.
