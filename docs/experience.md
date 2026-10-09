# BasketLens: an audience-first retail research experience

## Audience and goal

The primary audience is a recruiter, business stakeholder, or portfolio reviewer who has not necessarily studied association-rule mining. The product should communicate what was observed and how an analyst would use that evidence without promising sales uplift.

The interface is in plain international English, with an opt-out for the longer explanations. A technical reviewer can still inspect exact counts, filter rules, download CSV reports, and read the detailed methodology.

## Product identity

BasketLens is an editorial retail-research workbench, not a generic SaaS landing page. Its warm off-white paper, deep forest green and restrained clay accent are inspired by a field notebook and a retail analyst's written recommendations. Georgia is used only for editorial headings; system sans serif remains the functional UI font. There are no synthetic retail photos, fabricated testimonials, decorative gradients, fake awards, or generic AI badges.

## The reader's journey

1. **Sales overview:** Start with historical sales value, basket count, average basket value, and the share with multiple products. The country filter is visible at the point of use. Each metric is attributed to eligible positive-sale invoices, not profit or net revenue.
2. **Association explorer:** Search for a product, set minimum lift and co-purchases, see a specific rule explained as a sentence, then compare the readable table and optionally the pairwise network. The training rule table is ordered by earlier co-purchases, not later results.
3. **Build a basket:** Start with a one-click training-era example or manually choose products. Candidates are explained and can be downloaded. Holdout evidence is shown as descriptive later co-occurrence, not a predicted response to a recommendation.
4. **Data quality & methodology:** Follow the lineage from source invoice to later validation. Distinguish exclusions from additional quarantined invoices. Include honest limitations and downloadable reports.

## Visual and interaction standards

- Built primarily from Streamlit semantic widgets for keyboard, screen reader, and reliable mobile support.
- Search is literal and case-insensitive across product descriptions and codes, including multi-item antecedents.
- On mobile, primary content is a single narrative column; tabs may scroll horizontally rather than overflow the page.
- Disabled motion preference is respected. Hover interactions do not hide important information.
- Every data chart has adjacent plain-language context or an accessible table alternative.
- High-density data is capped visually; users can export all filtered rows.
- Empty, missing-data, and load-error states provide real instructions and do not invent results.
- Streamlit's sidebar remains collapsed initially so it cannot intercept mobile tab interactions.
- The public exhibit remains aggregate-only with a SHA-256 verified source. Full-data local mode is preserved.

## Statistical integrity

The underlying UCI data, cleaning, chronological train/holdout split, mining algorithms, rule arithmetic, and confidence/lift definitions are unchanged by this presentation upgrade. Training outcomes determine displayed rule order; later outcomes are used only for descriptive evidence and candidate review. Confidence and lift never mean incremental conversion or incremental revenue.

## Verification

- Unit-test the country-based basket snapshot, search, human-oriented table units, rule ordering, and terminology.
- Run real Streamlit AppTest and browser smoke on the GitLab CI runner with the public exhibit.
- Verify desktop and mobile interaction, focus, tab accessibility, state changes, no horizontal overflow, downloads, and network graph.
- Compare the published exhibit hash and rule counts to the previous verified release.
- Do not label the public hosted app reviewed until an actual Streamlit Cloud URL and runtime can be inspected.