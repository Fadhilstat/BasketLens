# BasketLens M5.2: anonymous hosted release gate

The new `scripts/hosted_smoke.py` verifies the actual deployed Streamlit app from a new, credential-free Chromium page. This is an independent release check, not a replacement for real UCI CI or local UI regression.

## Run

```bash
python -m pip install 'playwright>=1.50,<2'
python -m playwright install chromium
python -m pytest -q tests/test_hosted_smoke.py
python scripts/hosted_smoke.py --url https://basketlens-retail.streamlit.app/ --report reports/hosted-smoke
```

The exit code is 0 only if both 1440x900 desktop and 390x844 mobile checks pass. The runner inspects actual dashboard KPIs, 4 unique pairing cards, product search, sample basket, methodology, keyboard focus, header alignment and horizontal overflow. An anonymous login redirect or Streamlit runtime error blocks the release. Failed redirects are logged with token-free URLs.

## Status and ownership

The M5.1 GitLab MR !5 and GitHub PR #5 are already merged. GitLab M5.1 real-data browser QA passed and post-merge pipeline had 41 passing tests. At M5.2 preparation, anonymous requests to the Streamlit URL still redirected to login, so production public access is not verified. Check Streamlit Community Cloud's owner-managed app sharing and confirm source GitHub repository `Fadhilstat/BasketLens`, branch `main`, entrypoint `app/streamlit_app.py`. Run the hosted check after updating sharing. Do not bypass the host's authentication or expose credentials.

## Data integrity

No source UCI data, published aggregate exhibit, checksum, statistical model, analytical computation or source customer data is changed by this milestone. The live check is not asserted to pass until actually run successfully.
