# BasketLens | Consulting case study

## Executive recommendation

**Use recurring basket associations to prioritise low-risk commercial experiments, not to claim uplift.**

Retailers know which products sell well; they often lack clear, auditable evidence of which combinations are repeatedly purchased together. BasketLens turns historical UK retail invoices into directional association rules and checks the same relationships on a later time window.

## Dataset and methodology

Official UCI Online Retail II (Chen, 2019, DOI 10.24432/C5CG6D), December 2009 to December 2011:

| Stage | Source-backed result |
| --- | ---: |
| All source lines | 1,067,371 |
| Routine quality exclusions | 30,317 |
| Quarantined lines from 83 contradictory-date invoices | 5,773 |
| Eligible source lines | 1,031,281 |
| Eligible invoice baskets | 40,280 |
| Training / later holdout baskets | 32,224 / 8,056 |
| Full FP-Growth rules mined | 113,001 |
| Curated training-selected public rules | 1,500 |

The source is independently checked against a sparse one-to-one pairwise baseline. Training rule discovery precedes the chronological holdout. The public exhibit contains aggregates, not raw invoice lines or customer identifiers.

## Observed example: a pair of jumbo bags

**Antecedent:** JUMBO BAG PINK POLKADOT (22386)

**Consequent:** JUMBO BAG RED RETROSPOT (85099B)

| Statistic | Training period | Later holdout |
| --- | ---: | ---: |
| Joint baskets | 1,166 | 279 |
| Antecedent occurrences | Not required to show the training rule | 416 |
| Confidence | 63.1294% | 67.0673% |
| Lift | 6.2401x | 6.7706x |

**Interpretation:** in earlier baskets with the Pink Polkadot bag, 63.1% also contained the Red Retrospot bag. The later conditional co-occurrence was 67.1% (279 of 416 baskets containing the Pink Polkadot bag).

The pair was selected on **training co-occurrence and confidence**, not on its later performance. The later sample is used as an out-of-time descriptive check. These are not sales uplift or profit effects.

## What an analyst should recommend

**Hypothesis:** the two bags may be reasonable candidates for optional adjacent placement, a product-navigation prompt, or a bundle offer.

**Before a trial:** verify SKU availability, contribution margins, price positioning, returns behaviour and promotion costs. The historical dataset lacks these inputs.

**Experiment proposal:** randomly assign eligible sessions/stores to offer versus control, hold other conditions consistent where possible, and measure completed purchases and contribution margin. Set sample size, allocation and guardrails in advance. Reject a proposal if inventory or margin constraints invalidate the opportunity.

## What has and has not been proved

**Demonstrated:** reproducible cleaning and invoice audit, deterministic rule mining, non-leaky time split, later co-occurrence diagnostics, privacy-safe public release, responsive interactive exploration, real browser and CI tests.

**Not demonstrated:** treatment effectiveness, incremental revenue, contemporary demand, causal customer preferences, inventory optimisation or profit gain.

## Links

- [Guest-verified Vercel portfolio](https://basketlens-fadhil-9768s-projects.vercel.app/)
- [Streamlit analytical application source](https://github.com/Fadhilstat/BasketLens/blob/main/app/streamlit_app.py) (hosted guest access did not pass on 2026-10-10)
- [Source repository](https://github.com/Fadhilstat/BasketLens)
- [UCI official dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- [Full method and limitations](methodology.md)

This case study uses only source-backed published metrics. The consulting deck PNG export follows the same measurements.
