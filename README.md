# BasketLens

**Retail Market Basket & Cross-Selling Intelligence**

BasketLens is an end-to-end research application that turns historical UK retailer invoice lines into auditable product association rules, checks whether the rules persist in later orders, and allows analysts to explore cross-sell candidates through a Streamlit interface.

**Current status:** Source code is available on GitLab and GitHub feature branches for release review. GitLab CI passed 25 tests with real installed dependencies. A full UCI dataset audit is in progress; the first attempt detected 83 source invoices with conflicting dates and/or countries and failed closed. A new CI audit measures the precise exclusion fraction before explicitly quarantining inconsistent invoices. No validated full-data report or public dashboard is claimed until that CI evidence passes.

## Business problem

Retailers can view popular products, but popularity alone does not answer which products tend to appear together in invoices. BasketLens supports a retail analyst who needs to:

1. Reconcile positive merchandise sale lines before calculating baskets.
2. Quantify the prevalence of product combinations using support, confidence, lift, and observed counts.
3. Inspect whether associations persist on chronologically later invoices.
4. Explore candidate cross-sell suggestions, with the evidence behind each one.
5. Export rule and quality reports for business review.

**Research question:** Which product combinations co-occur reliably enough to justify prioritising a cross-selling experiment?

## Data

- **Official source:** [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Creator:** Daqing Chen (2019)
- **DOI:** https://doi.org/10.24432/C5CG6D
- **License:** CC BY 4.0. Attribution is required for public derivative work.
- **Coverage:** 1 December 2009 to 9 December 2011, approximately 1,067,371 source invoice lines.
- **Raw format:** `online_retail_II.xlsx`, two year sheets. Dataset includes invoices, stock codes, descriptions, quantities, dates, prices, customers, and countries.

The source contains cancellations, returns, missing customer IDs, non-merchandise line items, and wholesale orders. Raw data and generated analysis artifacts are `.gitignore`d, and customer IDs are not written to processed analytics files.

> The workbook must be obtained from the official UCI source. Test fixtures in `tests/` are synthetic and must never be presented as analytical findings about the retailer.

## Quick start

Recommended Python: 3.11. Running the full pipeline requires internet access and enough memory to parse the UCI workbook.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'

# Check local environment and original dataset availability.
python -m basketlens.cli doctor

# Download original dataset into ignored local storage.
python -m basketlens.cli download

# Train on earlier baskets, evaluate on later baskets, and audit outputs.
python -m basketlens.cli build --algorithm fpgrowth
python -m basketlens.cli verify

# Interactive dashboard with processed artifacts.
streamlit run app/streamlit_app.py
```

**Manual data download fallback:** If the CLI download encounters a network error, open the [UCI Online Retail II dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii), download the official workbook, and save it as `data/raw/online_retail_II.xlsx`. No login, API key, or external retailer credentials are required.

**Lower-dependency alternative:**

```bash
python -m basketlens.cli build --algorithm pairwise
```

The pairwise baseline computes exact 1-to-1 rules using a sparse co-occurrence matrix. It is **not** FP-Growth and cannot find 2-to-1 rules. FP-Growth uses `mlxtend` when the package is installed.

For debugging only, use `--max-rows-per-sheet 3000 --min-item-count 2 --min-joint-count 2`. Subset output is explicitly tagged as partial, not representative. The default invoice inconsistency policy is to fail closed. Only after reviewing anomalous invoices should an analyst explicitly choose `--inconsistent-policy quarantine` to remove and count all lines from conflicting invoices.

## Dashboard

| View | Real user value |
| --- | --- |
| Sales overview | Inspect eligible historical merchandise sales, basket sizes, and product rankings |
| Association explorer | Filter association rules, inspect the bounded product affinity map, and review later confidence intervals |
| Build a basket | Select products and inspect suggestions ranked by repeated holdout evidence, with candidate CSV export |
| Data quality & methodology | Review excluded lines, data rules, test cutoff, and limitations |

Country selection only changes **sales overview** metrics. It does not retrain the global recommendation model. All buttons and exports are wired to generated data files. Empty and unprepared-data states are handled.

## Methodology in brief

1. Read both Excel year sheets and standardise legacy column names (`Invoice`, `Price`, `Customer ID`).
2. Keep source sheet and row lineage. Namespace invoice numbers by source sheet to avoid collisions across years.
3. Flag cancellations, invalid dates, missing product fields, non-finite/non-positive quantities/prices, and service codes. Keep valid positive merchandise sale lines.
4. Fail on conflicting invoice timestamps/countries by default; a separately requested quarantine mode drops whole conflicting invoices and records lost coverage.
5. Count a basket as a **source sheet + invoice ID**. Product presence uses distinct SKUs, including single-item invoices in denominators.
6. Chronologically split baskets into training and future holdout without splitting equal timestamps.
7. Select frequent SKUs **on training baskets only**, with deterministic tie-breaking, frequency caps, and reported candidate coverage.
8. Mine FP-Growth rules (antecedent size 1 or 2, consequent size 1) or a sparse pairwise baseline.
9. In holdout baskets, measure antecedent firings, consequent hits, later confidence, baseline support, lift, and approximate Wilson confidence intervals.
10. Validate the generated artifacts independently before replacing an existing valid build. Explore rules, a bounded affinity map, evidence labels, and exports.

See [Detailed methodology](docs/methodology.md) for the precise interpretation and limitations.

### Metrics

For products A and B across N invoices:

- **Support(A -> B):** count(invoices containing A and B) / N
- **Confidence(A -> B):** count(invoices containing A and B) / count(invoices containing A)
- **Lift(A -> B):** Confidence(A -> B) / Support(B)

Lift above 1 indicates greater co-occurrence than expected under independence. It is **not** a causal recommendation uplift, a profit estimate, or a guaranteed conversion increase.

## Technical architecture

```text
UCI official XLSX (2 sheets) or exported CSV
     |
     v
Schema adapter + source lineage + quality reasons
     |
     v
Eligible positive merchandise sale lines
     |
     +--> Basket headers + distinct SKU membership
     |          |
     |          +--> Chronological train/holdout split
     |                         |
     |                         +--> FP-Growth or sparse pairwise miner
     |                         +--> Out-of-time rule evaluation
     |
     +--> Monthly, country, SKU and basket summaries
                               |
                               v
                  Atomic processed artifact bundle
                               |
                               v
                     Streamlit + Plotly interface
```

### Stack

Python 3.11, Pandas, SciPy, mlxtend (FP-Growth), Streamlit, Plotly, NetworkX, Pytest, GitLab CI, GitHub Actions. Dataset and generated reporting use CSV/JSON for simple, portable deployment. DuckDB is deliberately not a runtime requirement in this version, because the current data volume does not justify another service.

## Repository

```text
basketlens/
├── app/streamlit_app.py
├── src/basketlens/
│   ├── ingestion.py
│   ├── cleaning.py
│   ├── mining.py
│   ├── insights.py
│   ├── network.py
│   ├── validation.py
│   ├── evaluation.py
│   ├── reporting.py
│   ├── pipeline.py
│   ├── download.py
│   └── cli.py
├── tests/
├── docs/architecture.md
├── docs/methodology.md
├── docs/verification.md
├── data/raw/             # gitignored source dataset
├── data/processed/       # gitignored outputs
├── .gitlab-ci.yml
├── .github/workflows/ci.yml
├── RUN_STATE.md
├── HANDOFF.md
└── pyproject.toml
```

## Testing

```bash
python -m compileall -q src app
python -m pytest -q
```

Tests cover schema adaptation, source-sheet invoice identity, cancellations/returns, missing IDs, non-finite values, explicit invoice quarantine, service-line exclusions, support denominators, candidate coverage, pairwise rule calculations, holdout-aware recommendations, Wilson intervals, affinity graph construction, temporal leakage prevention, holdout confidence/lift, tampered-artifact detection, end-to-end CLI calls, and rerun replacement. Optional full-library integration tests for actual mlxtend and Streamlit run only when installed. See [verification protocol](docs/verification.md).

GitLab CI and GitHub Actions have run the unit tests. GitLab release checks additionally download UCI data, evaluate the source invoice conflict rate, run full-data pairwise and FP-Growth, and verify the Streamlit application headlessly. See current pipeline results for the evidence of completion; job configuration alone is not proof of success.

## Security and privacy

- No API keys needed for a local dataset and dashboard.
- User-provided source file remains in the gitignored `data/raw` directory.
- Customer IDs are not persisted in generated dashboard data.
- Download is restricted by file format and maximum archive size. The archive is never extracted to untrusted paths.
- Automated reports include hashes and time cutoffs for reproducibility.
- Code is not pushed or merged without distinct user approvals.

## Important limitations

- Positive sales are not reconciled net sales after returns or cancellations. Excluding returns does not imply returns had no economic impact.
- Unknown non-merchandise codes, duplicate invoice records, missing descriptions, and wholesale behaviour may affect associations.
- The top-product cap limits the product universe, even when other products occur in baskets.
- Historic retail products and cross-selling patterns may not transfer to modern commerce.
- Low holdout firings can make later lift unstable. Wilson intervals on holdout confidence are approximate and can be too optimistic when repeated customers create dependent observations. No multiple-testing adjustment is implemented.
- No inventory, cost of goods, discounts reconciliation, margins, or randomized experiment is provided by this dataset.
- Association rules are not recommendations that have been A/B-tested or evidence of incremental sales.

## Roadmap

- **P0:** Real-data build verification, actual FP-Growth execution, Streamlit browser QA, reproducible data checks, production readiness.
- **P1:** Holdout evidence labels and confidence intervals are implemented in source. Remaining: browser verification, alternate candidate budgets, category-aware false-positive review.
- **P2:** Explicit what-if bundling simulator with user-entered assumptions, country-specific recomputation, API integration if real use demands it.

## Development and release workflow

Development is local first. One coherent milestone per branch with 1 to 3 meaningful commits, one GitLab merge request, explicit `APPROVE PUSH` before remote push, and `APPROVE MERGE` before merging. GitLab is the controlled development surface; a verified GitHub release can be mirrored after approval.

Project continuity is in `RUN_STATE.md` and `HANDOFF.md`. No push or deployment exists at the time of this draft.

## License and attribution

BasketLens application code: [MIT](LICENSE). Dataset: Chen, D. (2019). *Online Retail II*. UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Data is not bundled or redistributed in this repository.

## Author

Data analytics portfolio project. Author's GitHub and LinkedIn links can be added after the project is published and verified.


## Public Streamlit deployment (planned, not yet live)

The production entrypoint is \`app/streamlit_app.py\`, on branch \`main\` of
https://github.com/Fadhilstat/BasketLens. The root \`requirements.txt\` installs
the project package and its dependencies. Use Python 3.11 or 3.12 on
Streamlit Community Cloud.

The public app loads \`data/public_demo/basketlens_public_v1.b64\` and verifies
its companion SHA-256 checksum. This aggregate-only exhibit is built from
official UCI Online Retail II in CI and contains a limited subset of rules
selected using training-period measures, with matched chronological holdout
evidence. It contains no customer IDs, invoice IDs or raw invoice rows.

For deployment, visit https://share.streamlit.io and select repository
\`Fadhilstat/BasketLens\`, branch \`main\`, and main file
\`app/streamlit_app.py\`. Wait until the exhibit has been committed and its
GitHub CI passed. No API keys are required. Do not present a Streamlit URL
as live until the hosted app has been opened and smoke-tested.

Local full-data analysts can still point \`BASKETLENS_DATA_DIR\` at a complete
verified analytics build. The public display is curated; full-data counts
in its manifest and quality report refer to the offline historical analysis,
not to the number of display rules. UCI credit: Daqing Chen (2019),
DOI 10.24432/C5CG6D, CC BY 4.0.

## Audience-first reading experience (M4)

The Streamlit frontend follows an editorial retail research design with a forest-green and
warm-paper palette. It keeps the four tested workflows but prioritises plain-language explanations.
The country filter appears in the sales overview. Pairings can be searched by product or stock
code; confidence and lift are explained using ordinary shopping examples; the basket builder has
a one-click example and still exports evidence-ranked candidates.

A new `docs/experience.md` explains layout decisions, accessibility, empty states and the
non-causal boundaries. Source data, the 1,500-rule public exhibit, checksum, and computation
methods are unchanged. The current release has been tested with synthetic fixtures locally;
a real-data GitLab/browser CI rerun is required before merging.


## M5 reference-inspired dashboard

The M5 frontend makes BasketLens easier to scan with a soft-gray workspace,
white rounded panels, deep green accents, responsive navigation, a clear product
ranking, and visually grouped sales/basket charts. It is based on the user's
green/white dashboard references but uses only real historical UCI aggregate
metrics and preserves existing analytic methods and downloads.

Four functional research tabs remain: Sales overview, Association explorer,
Build a basket, and Data quality & methodology. Resource shortcuts link to
official UCI documentation, project methodology and the GitHub source.
The curated public exhibit is unchanged and contains no raw invoices or customer IDs.
See [M5 design rationale](docs/design-m5.md).

The M5 reference mockups use illustrative chart shapes. The shipped Streamlit
app renders source-backed charts and real measurements. A live Streamlit
Community Cloud URL has not been verified here; do not claim it is deployed.
