"""Tampering checks use only generated, explicitly synthetic fixture data."""
from __future__ import annotations

import pandas as pd
import pytest

from basketlens.mining import RuleConfig
from basketlens.pipeline import run_pipeline
from basketlens.validation import validate_artifacts


def fixture_run(tmp_path, raw_fixture):
    source = tmp_path / "synthetic_TEST_ONLY.csv"
    raw_fixture.drop(columns=["source_sheet", "source_row"]).rename(columns={
        "invoice_no": "Invoice", "stock_code": "StockCode", "unit_price": "Price",
        "invoice_date": "InvoiceDate", "customer_id": "Customer ID"
    }).to_csv(source, index=False)
    dest = tmp_path / "processed"
    config = RuleConfig(min_item_count=1, min_joint_count=1, min_confidence=0,
                        min_support=.01, min_lift=0, max_products=3)
    run_pipeline(source, dest, config, train_fraction=.7)
    return source, dest, config


def test_artifact_verifier_accepts_valid_synthetic_build(tmp_path, raw_fixture):
    _, dest, _ = fixture_run(tmp_path, raw_fixture)
    summary = validate_artifacts(dest)
    assert summary["status"] == "PASS"
    assert summary["basket_count"] == 10
    assert summary["rule_count"] > 0


def test_artifact_verifier_rejects_corruption(tmp_path, raw_fixture):
    source, dest, config = fixture_run(tmp_path, raw_fixture)
    rules = pd.read_csv(dest / "rules.csv")
    rules.loc[0, "support"] = 0.999999
    rules.to_csv(dest / "rules.csv", index=False)
    with pytest.raises(ValueError, match="support arithmetic mismatch"):
        validate_artifacts(dest)
    # Rebuild must replace corrupted data with a validated complete export.
    run_pipeline(source, dest, config, train_fraction=.7)
    assert validate_artifacts(dest)["status"] == "PASS"
