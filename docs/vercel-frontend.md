# M6.3 | BasketLens public portfolio companion

## Decision and scope

This is a small, separate, static Vercel-compatible reader experience. The authoritative Python analytics application and the original Streamlit interface remain untouched. The new `site/` surface is a non-sensitive, aggregate-only *case study*, not an interactive replacement for the dashboard. A cleanly separated public front door makes the project easier for a recruiter or business stakeholder to evaluate without waiting on historical dataset processing.

The dossier reflects the existing BasketLens visual direction (forest green, restrained paper background, editorial hierarchy), rather than importing a generic template or rebranding the research. It has only one meaningful interactive visualization: a keyboard-operated earlier/later evidence comparison.

## Verified input facts

The facts shown here are copied from the validated `README.md` and `docs/portfolio-case-study.md`: 1,067,371 UCI lines; 40,280 eligible baskets; 32,224 training, 8,056 holdout; 1,500 curated public rules; 83 inconsistent invoices; case 22386 to 85099B with 1,166 earlier joint baskets, 63.1294% earlier confidence and 6.2401 lift, and 279 of 416 later antecedent baskets with 67.0673% confidence and 6.7706 lift. Values are embedded into the static HTML on purpose. They are an immutable selection from the verified exhibit and must be updated only after upstream evidence is revalidated.

No actual experiment was conducted. Association confidence is not causal conversion uplift. The headline and the evidence note make this limitation prominent.

## Verified interaction contract

- Finding/Method/Decision navigation anchors lead to real sections.
- The two period tabs update confidence, lift, counts, bar width, descriptive copy and progressbar accessible values. ArrowLeft/ArrowRight/Home/End work without a mouse.
- The copy-evidence action uses the native clipboard API when available, with useful fallback text if copying is denied.
- Native `details` show the data exclusions.
- External source, dataset and original application links are real. The original Streamlit app is marked as guest-access unverified.
- Responsive at 320, 390, 768, 1024 and 1440 px with no document overflow in Chromium. Reduced-motion and visible focus styles are included.

## Architecture and deployment

- Source: `site/index.html` (self-contained HTML, CSS and JS for predictable static delivery)
- Build: `node site/scripts/build.mjs` copies the audited entrypoint to `site/dist/`
- Tests: Node built-in test runner and Playwright Chromium smoke
- Vercel: Hobby project linked to GitLab source `fadhilrusydih/basketlens`, root directory `site`, framework Other, Node 22, output `dist`, committed `vercel.json`; GitHub remains the public mirror
- No environment variables, user login, server functions, database or external trackers
- No new ML inference, data upload or on-request Python mining
- Original app: `app/streamlit_app.py` remains the complete analytical research workbench

This static approach is intentionally smaller than Next.js. If portfolio traffic and required interactions justify unifying the full research application later, re-evaluate Next.js and/or a separate Python service after explicit API and evidence contracts. Vercel does not itself improve UI quality.

## Publication gate

A passing local/CI build is not evidence of a live Vercel deployment. A personal Vercel project and anonymous production URL must be independently verified before it is announced on LinkedIn. In particular, verify links, the data toggle, keyboard access, mobile overflow, and Streamlit guest access status. The GitLab source of truth and GitHub public mirror should match before production goes live.

## Rollback

If the site release causes problems, disable the linked Vercel project or revert the site change in Git; the original Streamlit analytical app is unchanged and remains the fallback. Keep source/data privacy audits intact.


## Deployment evidence (2026-10-10)

The portfolio front door is now deployed from GitLab `fadhilrusydih/basketlens`, branch `main`, commit `3cf2ca5`, via connected Vercel project `prj_BiqgK3ZnFN9vKURIftb5m1dxB8wF`. The production URL is https://basketlens-fadhil-9768s-projects.vercel.app/ and Vercel reported READY after cloning and running the declared build. GitLab remains source of truth; GitHub `Fadhilstat/BasketLens` is the portfolio mirror. Node is pinned to major version 22 to prevent automatic major upgrades. Production authentication is disabled while preview authentication stays enabled. Signed-out guest interaction is a separate CI release gate and must not be inferred from READY.


## Anonymous release proof

GitLab CI job https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194 used a fresh unauthenticated Chromium browser against https://basketlens-fadhil-9768s-projects.vercel.app/ and returned PASS at desktop 1440 px, mobile 390 px and narrow mobile 320 px. Every page responded HTTP 200, with the expected case-study heading, training/holdout control, keyboard navigation, non-overflow layout and methodology section. Screenshots and a JSON summary are stored as expiring job artifacts. This proves the Vercel portfolio page for the inspected deployment, not the external Streamlit dashboard or any commercial uplift.


## Public CTA correction

The separate Streamlit hosted guest test failed to load its dashboard on desktop/mobile in GitLab job 17080255195. The Vercel dossier therefore replaces its secondary hero CTA with the accessible GitHub consulting case study. Publication remains evidence-first: the Vercel case study is independently accessible, while deeper hosted Streamlit exploration is an open operational issue.


## M6.5 design decision: retail intelligence dashboard

Owner feedback (2026-10-10): the M6.4 portfolio was visually distant from the approved green-and-cream retail analytics reference, because its large reading sections looked like a research article. The approved redesign changes only `site/index.html` presentation, research navigation and associated UI tests. Desktop introduces a restrained pine left rail, case-report heading, comparative association hero, four audited cohort metrics, true training/holdout bars, a selected pair panel, a data-quality audit strip and commercial test brief. Tablet and phone use a compact navigable header and stacked panels. Neither Vercel hosting nor generic templates independently create good UX. No dependency, server data fetch, private record, sign-in or new quantitative estimate was added.

UX acceptance criteria: 1440/1024/768/390/320 px without horizontal overflow; live tab switch and keyboard ArrowLeft/ArrowRight; visible navigation destinations and accessible focus; reduced-motion preference; complete source-backed figures; primary CTA to the on-page finding and secondary to the real GitHub case study. Results are historical co-occurrence, not an A/B test. This milestone keeps `app/streamlit_app.py` and all checksum-verified aggregate datasets unchanged.


## M6.6: public Rule Explorer without a live compute backend

The fixed featured case remains available, but research reviewers can now inspect the 1,500 curated training-selected associations from UCI Online Retail II directly on Vercel. The static build reads the **already published, aggregate-only** compressed exhibit; rejects a changed checksum, unwanted schema and private fields; joins each rule to its holdout evidence; and writes only a narrow browser-safe JSON structure. Because Vercel isolates the root `site` folder, `site/data/` contains an exact fingerprint-checked copy of the canonical publication, while CI asserts the canonical bytes when available.

The explorer supports literal SKU/product-name search, minimum training lift, minimum earlier co-purchase count, 1-versus-2 product antecedents, accurate empty states, explicit retry after asset load failure, accessible touch/keyboard controls and capped first-screen results. Ordering is entirely based on training co-purchase evidence. Later-period hits and fires are displayed as observational context only, not a classifier, forecast, ranked recommendation, purchase prediction or measured sales effect.

Release gates: Node site tests check export schema, record count, confirmed Pink Polkadot example and leakage controls; Chromium offline UI fixture tests exercise interaction states on five viewport sizes; independent GitLab guest Chromium checks the deployed `explorer.v1.json` and version fingerprint after merging to `main`. No database, auth, runtime API or environment secrets are introduced. The separate hosted Streamlit limitation remains unchanged.


## M6.7 example Basket Builder and decision boundary

One new section completes the portfolio visitor journey: select up to three catalogued antecedent products, start from the verified 22386 historical example, inspect rule consequents that are not already in the basket, review training co-purchases/confidence/lift and separately labelled later hits/fires. More-specific matching antecedents rank first; all tie-breakers are earlier-training metrics. This ranking is **not the deployed Streamlit suggestion scorer**, and it never uses holdout results for selection. Inference about incremental sales, probability of customer purchase, inventory availability and profitability is explicitly unsupported. Controls use real HTML buttons and inputs, textContent for untrusted labels, visible empty/error states and mobile stacks.

Runtime remains static Vercel (Root Directory `site`, Node 22). Build copies two dependency-free ES modules into `site/dist`. Data is shared in the browser with the verified Rule Explorer asset rather than fetched again. Rollback is a Vercel redeploy of the prior production commit; no database state or migration exists. Expected idle compute and VPS impact: zero additional service runtime.
