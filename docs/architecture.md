# BasketLens system design

## Decision boundary

The use case is transparent cross-selling research using *historical observational* invoices. It is not an e-commerce checkout service, a customer-data platform, or an autonomous marketing engine. All outputs are analytical suggestions requiring human interpretation and experiment design.

## Data contracts

Canonical raw fields:

| Name | Type | Quality checks |
| --- | --- | --- |
| invoice_no | string | non-empty; prefix C indicates cancellation |
| stock_code | string | non-empty; excludes documented service codes |
| description | string | non-empty; conservative service exclusion |
| quantity | number | strictly positive for eligible sale |
| invoice_date | datetime | parseable, used in time split |
| unit_price | number | strictly positive GBP price |
| country | string | blanks set to Unknown |
| customer_id | optional string | missingness counted; dropped before outputs |
| source_sheet | string | included in basket ID |
| source_row | integer | preserves source lineage |

`build_baskets` returns basket headers and product memberships. SKU is deduplicated **only for presence**, while quantity and sales value retain the full line sums. Identical original lines are flagged, not silently removed.

## Processing

`ingestion.py` adapts the old workbook names and the two separate sheets. `cleaning.py` applies mutually exclusive rejection reasons, returns eligible sale lines, and builds invoices. `reporting.py` builds aggregate facts. `evaluation.py` splits earlier and later transactions, then measures rule outcomes on the holdout data. `pipeline.py` writes all outputs to a temporary directory and replaces the complete artifact directory in a same-filesystem rename operation with rollback on failed activation.

Artifacts never contain customer IDs. They contain item-level catalogue data, aggregated monthly/country data, basket totals, association rules, and quality/manifest metadata.

## Analytical engine

**Pairwise:** frequency-selected candidates, SciPy sparse transaction matrix, and co-occurrence counts from X-transpose times X. All eligible training baskets contribute to the support denominator. Both directions are evaluated separately.

**FP-Growth:** mlxtend discovers frequent itemsets up to size 3 on the training subset. Consequents are restricted to one SKU, and antecedents to one or two SKUs. For a transparent compute ceiling, the item universe is limited to the top training-frequency products, with a fixed maximum dense candidate-matrix size.

**Holdout:** train basket timestamps strictly precede the holdout boundary. Candidate frequency selection, itemset mining, and rule thresholds use training data only. The holdout evaluator counts later antecedent firings and successes, preserving NaN when a rule never fires. The code does not label this measurement an A/B test.

## UI interaction contract

- Overview country filter changes historical sales KPI and trend only.
- Rule explorer filters existing model output by lift and co-occurrence count.
- Basket builder selects known SKUs and triggers exact antecedent subset matches.
- Data quality view exposes all exclusion counts and manifest settings.
- CSV and JSON export buttons operate on real files loaded into the session.
- Empty artifact or empty rule outputs display useful guidance rather than invented examples.

## Threat model and bounds

- Local data download is limited to one XLSX member of the official ZIP URL, with maximum archive and uncompressed sizes and ZIP validation.
- No secrets are stored, and no external services are contacted after the dataset has been downloaded.
- Original customer identifiers are not exported to dashboard data.
- User-controlled product names are rendered by Streamlit as text, not custom HTML.
- No checkout, user authentication, payment, or data-writing endpoint exists.
- The application assumes a trusted analyst runs dataset-building commands. It is not intended to host arbitrary customer file uploads.

## Deployment options

The MVP can run locally or on a Streamlit host with prepared read-only artifacts. A dataset licensing check and hosting memory measurement must precede production publication. If public hosting cannot ship the generated artifacts as part of a controlled deployment, connect a private artifact store or create a smaller clearly labeled demonstration cohort after actual-data verification.

Do not add a database, hosted backend, or external AI service unless measurements justify it.

## Source quality failure behaviour

`cleaning.py` rejects non-finite values, and `quarantine_inconsistent_baskets` prevents an invoice containing more than one timestamp or country from contaminating the model. It fails closed by default. Explicit `quarantine` mode drops all lines in each affected invoice and reports the count before mining. The build manifest records that choice and the quality report records its coverage impact.

`validation.py` independently checks the staged output's arithmetic before `pipeline.py` changes the active data directory. A failed check leaves the earlier artifact directory intact. `python -m basketlens.cli verify` can audit a saved artifact bundle without needing the raw workbook.

## Decision support and visualization

`insights.py` computes Wilson bounds for later conditional co-occurrence and ranks eligible suggestions by later evidence before in-sample lift. Its descriptive labels do not establish causal effects or statistical significance. `network.py` draws a bounded graph of unique two-product associations; the graph deliberately omits two-product antecedent rules rather than misrepresenting them as ordinary pairwise links. Graph distance is not a measured affinity metric.

See `docs/verification.md` for the full source-data and interface release checks.
