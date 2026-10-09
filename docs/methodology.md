# Methodology and interpretation

## Scope

Source is UCI Online Retail II. The provided workbook has two year sheets, with a historically mixed wholesaler/consumer customer base. Reported outputs describe only positive merchandise invoice lines that pass the eligibility filters.

## Cleaning decisions

Rejection precedence: missing invoice; invoice marked as cancelled; invalid date; missing product code/description; nonpositive or missing quantity; nonpositive or missing price; known service or accounting codes; eligible sale. Every source line belongs to exactly one mutually exclusive quality category. Missing customer IDs do not exclude legitimate transactions.

Known service codes excluded by exact code are listed in `cleaning.py`. A small set of exact descriptions are also removed. This approach errs toward conservative exclusion rather than substring matching words such as "discount" in otherwise legitimate merchandise names. The rule list is configurable in code and should be reviewed when inspecting actual source distributions.

Returns and cancellations are not netted against original invoices. Reported sales values are **gross positive merchandise values**, not audited net revenue. Price includes no cost or margin information.

## Basket definition and cohort split

A basket is `source_sheet::invoice_no`. A basket has one invoice timestamp and country. SKU presence is Boolean; quantities do not increase Support or Confidence directly. One-item baskets remain in denominators. Each invoice belongs either to earlier training or later holdout based on timestamp, with identical cutoff timestamps kept on the same side.

When product selection is capped, support denominators still use all train baskets, not only baskets containing candidate SKUs.

## Association metrics

- `support(A -> B) = count(A and B) / N`.
- `confidence(A -> B) = count(A and B) / count(A)`.
- `lift(A -> B) = confidence(A -> B) / [count(B) / N]`.
- `leverage(A -> B) = support(A and B) - support(A) * support(B)`.

For a 2-to-1 rule, A denotes the full antecedent pair, not two independently sufficient single-SKU rules.

## Rule selection

Candidates must pass minimum product frequency, minimum joint count, support, confidence, and lift. FP-Growth includes itemsets up to three products. The bounded product universe and all thresholds are recorded in the manifest. Results can change when candidate caps or thresholds change and therefore cannot be compared naively across configurations.

## Time-based evaluation

Training uses only earlier invoices. Later invoices measure:

- **Fires:** later baskets containing all antecedent SKUs.
- **Hits:** later baskets containing antecedent and consequent SKUs.
- **Holdout confidence:** Hits / Fires when Fires > 0.
- **Holdout baseline support:** share of later baskets containing the consequent.
- **Holdout lift:** Holdout confidence / later baseline support, when defined.
- **Holdout coverage:** Fires / later baskets.

This is an out-of-time association check. The observed transactions happened without the proposed recommendation feature being deployed. The evaluator cannot measure incremental revenue, average treatment effects, causal conversion lift, or whether users would accept bundles.

## Analytical warnings

- High lift may be driven by niche items with few joint purchases.
- A popular item can have high confidence even with lift around 1.
- Multiple rules are selected from the same historical period. Without correction, statistical inference about the strongest rules risks selection bias.
- Cross-border comparisons can reflect underlying inventory, currency conversion, customer mix, and wholesaler concentration. This dataset does not support all adjustments.
- Product codes and names are historical, and no stock availability or modern catalogue is available.
- No evidence exists yet that using these recommendations improves retail outcomes.

## Roadmap for controlled evaluation

A future real retailer could randomize eligible sessions to display versus not display cross-sell suggestions, with safeguards for inventory and customer experience. Specify primary outcome and guardrails before launch, calculate required sample size from real baseline conversion, and measure incremental completed orders, returns, and contribution margin if available. That experiment is beyond this historical dataset and is not claimed here.

## Holdout evidence labels and uncertainty

Dashboard candidate ranking first prioritizes rules whose association was observed again with holdout lift above 1 and at least 20 holdout antecedent appearances. Others are explicitly marked as sparse or not repeated above baseline. These are practical review labels, **not significance tests**. Analysts can change the minimum holdout observations when inspecting the explorer.

A Wilson score interval describes the later conditional co-occurrence proportion (hits divided by firings) when there are firings. It is not a confidence interval for a treatment effect, sales lift, or profit. Repeat customers and related basket observations mean that binomial independence may not hold, so nominal 95% coverage is not guaranteed.

Top-SKU selection uses training frequency with lexical SKU tie-breaking. The manifest reports how many training baskets contain at least one selected product and how many contain at least two, so the product universe limitation is visible.

## Invoice consistency checks

Every source invoice should have one country and one timestamp. By default an inconsistency stops the build. The optional quarantine policy excludes the entire inconsistent invoice, not just the conflicting line, and records removed row and invoice counts. This avoids inventing a corrected country or date. Non-finite quantity and price values are never treated as valid sales.

## Output verification

The independent validator checks source-hash formatting, exclusive line-quality totals, invoice uniqueness, cross-view aggregate sales, exact arithmetic for training rules, holdout arithmetic, identical rule keys, and absence of exported customer ID columns. New builds are verified in a staging directory before replacing prior analytics. These consistency checks do not prove raw source authenticity or causal business value.
