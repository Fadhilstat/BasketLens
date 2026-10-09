"""Inspect inconsistent source invoices before allowing conservative quarantine.

Writes only aggregate data-quality counts. Never prints invoice or customer IDs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from basketlens.cleaning import clean_transactions
from basketlens.ingestion import load_transactions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/online_retail_II.xlsx"))
    parser.add_argument("--report", type=Path, default=Path("reports"))
    parser.add_argument("--max-loss-fraction", type=float, default=0.01)
    args = parser.parse_args()
    raw = load_transactions(args.input)
    sale_lines, quality = clean_transactions(raw)
    groups = sale_lines.groupby("basket_id", sort=False).agg(
        distinct_dates=("invoice_date", "nunique"),
        distinct_countries=("country", "nunique"),
        lines=("stock_code", "size"),
    )
    date_conflicts = groups["distinct_dates"].gt(1)
    country_conflicts = groups["distinct_countries"].gt(1)
    affected = groups.loc[date_conflicts | country_conflicts]
    affected_lines = int(affected["lines"].sum())
    eligible_lines = int(quality["valid_rows"])
    ratio = affected_lines / eligible_lines if eligible_lines else 1
    summary = {
        "status": "PASS" if ratio <= args.max_loss_fraction else "FAIL",
        "source_rows": int(quality["input_rows"]),
        "eligible_lines": eligible_lines,
        "affected_source_invoices": int(len(affected)),
        "date_conflict_invoices": int(date_conflicts.sum()),
        "country_conflict_invoices": int(country_conflicts.sum()),
        "both_conflicts": int((date_conflicts & country_conflicts).sum()),
        "affected_sale_lines": affected_lines,
        "affected_sale_line_fraction": ratio,
        "max_allowed_fraction": args.max_loss_fraction,
        "policy": "Entire conflicted invoice removed, not guessed or silently repaired.",
    }
    args.report.mkdir(parents=True, exist_ok=True)
    (args.report / "source_conflict_audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SOURCE_CONFLICT_AUDIT " + json.dumps(summary, sort_keys=True))
    if ratio > args.max_loss_fraction:
        raise SystemExit("Source invoice conflicts exceed the allowed quarantine cap")


if __name__ == "__main__":
    main()
