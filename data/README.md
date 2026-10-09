# Local data directory

Do not commit real customer records, raw invoices, or derived basket-level data by default.

- `raw/`: Gitignored original UCI workbook and source metadata.
- `processed/`: Gitignored generated analysis products and run manifests.

Official source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
Credit: Daqing Chen (2019), Online Retail II, UCI, CC BY 4.0.

Use `python -m basketlens.cli download` and `python -m basketlens.cli build --algorithm fpgrowth`.
If the download fails, save the manually downloaded original workbook at
`data/raw/online_retail_II.xlsx`.
