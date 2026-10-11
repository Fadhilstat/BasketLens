# BasketLens | Public Vercel frontend contract

## Decision and scope

BasketLens publicly serves a **static, interactive retail intelligence dashboard** from `site/` on Vercel. M6.3 first introduced the companion, but it now includes the earlier/later comparison, a searchable 1,500-rule Explorer and a hypothetical Basket Builder. It serves only reviewed aggregate historical evidence, with no invoice-level queries or live model inference.

The Python/Streamlit workbench in `app/streamlit_app.py` is kept for local reproducibility, **not** an actively maintained public Streamlit Cloud app. GitLab `main` is the canonical source and GitHub is the public code mirror. The restrained pine-and-paper design remains project-specific.

## Verified input facts

The facts shown here are copied from the validated `README.md` and `docs/portfolio-case-study.md`: 1,067,371 UCI lines; 40,280 eligible baskets; 32,224 training, 8,056 holdout; 1,500 curated public rules; 83 inconsistent invoices; case 22386 to 85099B with 1,166 earlier joint baskets, 63.1294% earlier confidence and 6.2401 lift, and 279 of 416 later antecedent baskets with 67.0673% confidence and 6.7706 lift. Values are embedded into the static HTML on purpose. They are an immutable selection from the verified exhibit and must be updated only after upstream evidence is revalidated.

No actual experiment was conducted. Association confidence is not causal conversion uplift. The headline and the evidence note make this limitation prominent.

## Verified interaction contract

- Finding/Method/Decision navigation anchors lead to real sections.
- The two period tabs update confidence, lift, counts, bar width, descriptive copy and progressbar accessible values. ArrowLeft/ArrowRight/Home/End work without a mouse.
- The copy-evidence action uses the native clipboard API when available, with useful fallback text if copying is denied.
- Native `details` show the data exclusions.
- Public source links target the official UCI dataset, GitHub case study and research code. No hosted Streamlit Cloud URL is promised as a second public demo.
- Responsive at 320, 390, 768, 1024 and 1440 px with no document overflow in Chromium. Reduced-motion and visible focus styles are included.

## Architecture and deployment

- Source: `site/index.html` (self-contained HTML, CSS and JS for predictable static delivery)
- Build: `node site/scripts/build.mjs` emits audited static HTML/JS, `explorer.v1.json`, Basket Builder modules and the public `release.json` commit fingerprint under `site/dist/`
- Tests: Node built-in test runner and Playwright Chromium smoke
- Vercel: Hobby project linked to GitLab source `fadhilrusydih/basketlens`, root directory `site`, framework Other, Node 22, output `dist`, committed `vercel.json`; GitHub remains the public mirror
- No application secrets, login, server functions, database or external trackers. The Vercel Git build uses platform `VERCEL_GIT_COMMIT_SHA`, while GitLab CI uses `CI_COMMIT_SHA` for exact-source evidence.
- No new ML inference, data upload or on-request Python mining
- Original app: `app/streamlit_app.py` remains the complete analytical research workbench

This static approach is intentionally smaller than Next.js. If portfolio traffic and required interactions justify unifying the full research application later, re-evaluate Next.js and/or a separate Python service after explicit API and evidence contracts. Vercel does not itself improve UI quality.

## Publication gate

A build PASS or deployment READY alone does not prove public availability. Before promotion, independently test signed-out navigation, train/holdout tabs, Explorer and Basket Builder, keyboard and mobile behavior, then compare the public `release.json` SHA with GitLab `main` and confirm reviewed GitHub mirror parity. The retired hosted Streamlit URL is not a release gate.

## Rollback

If the static site regresses, redeploy a previously tested READY Vercel release or revert the scoped GitLab change through a reviewed MR, then rerun the anonymous guest/provenance checks. The local Streamlit research workbench is not a public failover. No database migration is required.


## Deployment evidence (2026-10-10)

**Historical M6.3 checkpoint:** the original GitLab `main` commit `3cf2ca5` deployed on 2026-10-10. This historical SHA is not the current production target.

**Verified M7.3 checkpoint (2026-10-11):** GitLab main `54dd759c40d364214223de2f25b2f81a03b63adb`, Vercel production `dpl_3yoPq1manXE6926wXximwnYzzw1j` READY, [GitLab pipeline 2935480963](https://gitlab.com/fadhilrusydih/basketlens/-/pipelines/2935480963) SUCCESS and [GitHub Actions 38126462439](https://github.com/Fadhilstat/BasketLens/actions/runs/38126462439) SUCCESS. Public `release.json` matched the canonical SHA and approved exhibit fingerprint. After a newer deployment, establish its identity from the live [release manifest](https://basketlens-fadhil-9768s-projects.vercel.app/release.json) and current GitLab main.

## Anonymous release proof

GitLab CI job https://gitlab.com/fadhilrusydih/basketlens/-/jobs/17080255194 used a fresh unauthenticated Chromium browser against https://basketlens-fadhil-9768s-projects.vercel.app/ and returned PASS at desktop 1440 px, mobile 390 px and narrow mobile 320 px. Every page responded HTTP 200, with the expected case-study heading, training/holdout control, keyboard navigation, non-overflow layout and methodology section. Screenshots and a JSON summary are stored as expiring job artifacts. This proves the Vercel portfolio page for the inspected deployment, not the external Streamlit dashboard or any commercial uplift.


## Public CTA correction

Historical Streamlit hosted guest QA failed in GitLab job 17080255195. The public Vercel site points visitors to the reproducible GitHub case study, not that retired hosted URL. Python/Streamlit source remains available for local analysis.


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

## M6.8 typography and Vercel as sole public frontend

The pine-green and warm-paper retail dashboard keeps its existing structure. Manrope handles functional content, labels and numerical dashboard data; Instrument Serif handles editorial headings, with system fallbacks. Google Fonts is an optional external styling dependency, not an application runtime. Site remains Vercel Root Directory `site`, no API/backend/VPS. The failed optional Streamlit Cloud hosted guest CI job was retired while source and mandatory UCI parity and Vercel guest tests were preserved. Revert this commit and redeploy the preceding Vercel release to roll back without data migration.

## M6.9 motion design decision

Microinteractions are intentionally tied to real user actions rather than decorative loops. Hover is enabled only for devices with true hover/fine pointers, selected tabs respond with a 160ms background transition, and the verified evidence bar uses 360ms width interpolation. Only five meaningful analysis containers have a one-time 320ms entrance cue triggered with IntersectionObserver. This is progressive enhancement: their default appearance is fully visible, even if JS fails. Motion uses compositor-friendly opacity and translate rather than animating layout height or dimensions. On `prefers-reduced-motion: reduce`, CSS transitions are disabled and JS effects are skipped or cancelled. The static Vercel deployment, verified data, publication URLs and research limits are unchanged.


## M7.0 cost-aware CI for a static Vercel site
Full-source UCI rebuilding is warranted for analytics-impacting changes, not routine presentation updates. The GitLab `real_dataset_audit` job now automatically runs on MR changes to dataset, Python source/tests, audit scripts, analytic dependencies and CI itself. UI/docs-only MRs instead offer an explicit optional manual full audit, while always-on Python unit, source-hash protected Vercel JSON build, browser regression and signed-out guest checks remain. This reduces repeated download and heavy FP-Growth runner workload without weakening data-affecting change gates. No Vercel runtime changes, database, scheduler or additional monitoring service. An actual later UI-only MR is needed to measure the savings; do not claim unmeasured time/resource reduction.
