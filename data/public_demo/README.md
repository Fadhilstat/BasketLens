# BasketLens public exhibit

The generated basketlens_public_v1.b64 is a compressed aggregate-only JSON exhibit with a companion SHA-256 checksum.
It is produced by scripts/build_public_demo.py after full-data CI verification on UCI Online Retail II.

It includes product and country aggregates, selected training-period association rules,
matched later-period holdout evidence and grouped basket composition.
It excludes source invoices, customer identifiers and individual transaction records.

UCI attribution: Daqing Chen (2019), Online Retail II, DOI 10.24432/C5CG6D, CC BY 4.0.
Sales values and co-occurrence patterns are descriptive, not measured incremental uplift.
