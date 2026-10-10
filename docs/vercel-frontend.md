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
- Vercel: Personal account, import GitHub repository, root directory `site`, framework `Other`, output `dist`, committed `vercel.json`
- No environment variables, user login, server functions, database or external trackers
- No new ML inference, data upload or on-request Python mining
- Original app: `app/streamlit_app.py` remains the complete analytical research workbench

This static approach is intentionally smaller than Next.js. If portfolio traffic and required interactions justify unifying the full research application later, re-evaluate Next.js and/or a separate Python service after explicit API and evidence contracts. Vercel does not itself improve UI quality.

## Publication gate

A passing local/CI build is not evidence of a live Vercel deployment. A personal Vercel project and anonymous production URL must be independently verified before it is announced on LinkedIn. In particular, verify links, the data toggle, keyboard access, mobile overflow, and Streamlit guest access status. The GitLab source of truth and GitHub public mirror should match before production goes live.

## Rollback

If the site release causes problems, disable the linked Vercel project or revert the site change in Git; the original Streamlit analytical app is unchanged and remains the fallback. Keep source/data privacy audits intact.
