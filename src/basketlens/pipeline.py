"""Offline data build with reproducible metadata and atomic output replacement."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile

from basketlens.cleaning import clean_transactions, build_baskets, quarantine_inconsistent_baskets
from basketlens.ingestion import load_transactions
from basketlens.mining import RuleConfig, mine_rules
from basketlens.evaluation import temporal_split, evaluate_rules
from basketlens.reporting import summaries
from basketlens.validation import validate_artifacts


def file_hash(path: Path) -> str:
    hash_ = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hash_.update(block)
    return hash_.hexdigest()


def run_pipeline(input_path: str | Path, output_dir: str | Path,
                 config: RuleConfig, max_rows_per_sheet: int | None = None,
                 train_fraction: float = 0.8, inconsistent_policy: str = "fail") -> dict:
    """Build candidate rules on past baskets, test them on future baskets."""
    config.validate()
    input_path, output_dir = Path(input_path).resolve(), Path(output_dir).resolve()
    if output_dir == input_path.parent or input_path == output_dir:
        raise ValueError("Output directory must not be the raw input directory")
    raw = load_transactions(input_path, max_rows_per_sheet)
    sales, quality = clean_transactions(raw)
    sales, source_conflicts = quarantine_inconsistent_baskets(sales, policy=inconsistent_policy)
    quality["analysis_eligible_rows"] = int(len(sales))
    quality["source_invoice_conflicts"] = source_conflicts
    baskets, items, basket_quality = build_baskets(sales)
    if basket_quality["date_inconsistent_invoices"] or basket_quality["country_inconsistent_invoices"]:
        raise AssertionError("Inconsistent invoice survived the source invoice policy")
    train, test, cutoff = temporal_split(baskets, train_fraction=train_fraction)
    train_items = items[items["basket_id"].isin(set(train["basket_id"]))]
    test_items = items[items["basket_id"].isin(set(test["basket_id"]))]
    rules, mining_meta = mine_rules(train, train_items, config)
    evaluation = evaluate_rules(rules, test, test_items)
    agg = summaries(sales, baskets)
    metadata = {
        "project": "BasketLens", "source_file": input_path.name,
        "source_sha256": file_hash(input_path),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_note": "Local input, confirm provenance and UCI license independently",
        "row_limit_per_sheet": max_rows_per_sheet,
        "inconsistent_invoice_policy": inconsistent_policy,
        "partial_data": max_rows_per_sheet is not None,
        "method": asdict(config),
        "train_fraction_requested": train_fraction,
        "cutoff_utc_naive": str(cutoff),
        "train_baskets": int(len(train)), "holdout_baskets": int(len(test)),
        "basket_count_all": int(len(baskets)), "rule_count": int(len(rules)),
        "evaluated_rule_count": int(len(evaluation)),
        "data_first_invoice": str(baskets["invoice_date"].min()),
        "data_last_invoice": str(baskets["invoice_date"].max()),
        "candidate_mining": mining_meta,
        "notes": [
            "Association is not incremental uplift, profit, or causality",
            "Only products selected from training baskets can appear in rules",
            "Holdout is strictly later in time; no customer identifier is stored",
            "All GBP amounts are historical sales values before cancellation/return reconciliation",
        ],
    }
    quality["basket_checks"] = basket_quality
    if sum(quality["reason_counts"].values()) != quality["input_rows"]:
        raise AssertionError("Exclusive quality counts do not sum to input")
    if metadata["train_baskets"] + metadata["holdout_baskets"] != len(baskets):
        raise AssertionError("Temporal split does not cover all baskets")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".basketlens-build-", dir=output_dir.parent) as staging_path:
        staging = Path(staging_path) / "processed"
        staging.mkdir()
        for name, data in agg.items():
            data.to_csv(staging / f"{name}.csv", index=False)
        baskets.to_csv(staging / "basket_summary.csv.gz", index=False, compression="gzip")
        rules.to_csv(staging / "rules.csv", index=False)
        evaluation.to_csv(staging / "evaluation.csv", index=False)
        (staging / "quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
        (staging / "manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        # Refuse to replace a previous valid build with inconsistent analytics.
        validate_artifacts(staging)
        prior = output_dir.with_name(output_dir.name + ".previous")
        if prior.exists():
            if prior.is_dir():
                shutil.rmtree(prior)
            else:
                prior.unlink()
        try:
            if output_dir.exists():
                os.replace(output_dir, prior)
            os.replace(staging, output_dir)
        except OSError:
            if not output_dir.exists() and prior.exists():
                os.replace(prior, output_dir)
            raise
        if prior.exists():
            shutil.rmtree(prior)
    return metadata
