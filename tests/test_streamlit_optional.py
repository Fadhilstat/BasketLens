"""Browserless Streamlit script smoke tests when Streamlit is installed.

This tests rendering logic only. It does not replace visual, mobile or keyboard QA.
"""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest

from basketlens.mining import RuleConfig
from basketlens.pipeline import run_pipeline


APP = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def test_dashboard_handles_unprepared_data(tmp_path, monkeypatch):
    monkeypatch.setenv("BASKETLENS_DATA_DIR", str(tmp_path))
    rendered = AppTest.from_file(str(APP), default_timeout=15).run()
    assert len(rendered.exception) == 0


def test_dashboard_renders_synthetic_generated_artifacts(tmp_path, monkeypatch, raw_fixture):
    source = tmp_path / "synthetic_TEST_ONLY.csv"
    raw_fixture.drop(columns=["source_sheet", "source_row"]).rename(columns={
        "invoice_no": "Invoice", "stock_code": "StockCode", "unit_price": "Price",
        "customer_id": "Customer ID", "invoice_date": "InvoiceDate"
    }).to_csv(source, index=False)
    output = tmp_path / "prepared"
    run_pipeline(source, output, RuleConfig(
        min_item_count=1, min_joint_count=1, min_support=.01,
        min_confidence=0, min_lift=0, max_products=3), train_fraction=.7)
    monkeypatch.setenv("BASKETLENS_DATA_DIR", str(output))
    rendered = AppTest.from_file(str(APP), default_timeout=25).run()
    assert len(rendered.exception) == 0
    assert len(rendered.metric) >= 3
