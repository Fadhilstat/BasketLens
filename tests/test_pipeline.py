import json
import pandas as pd
from basketlens.mining import RuleConfig
from basketlens.pipeline import run_pipeline


def test_pipeline_creates_reproducible_summaries(tmp_path, raw_fixture):
    source = tmp_path / "fixture_TEST_ONLY.csv"
    # Match the actual legacy column names to check round-trip input adapter.
    frame = raw_fixture.drop(columns=["source_sheet", "source_row"]).rename(columns={
        "invoice_no":"Invoice", "stock_code":"StockCode", "unit_price":"Price",
        "customer_id":"Customer ID", "invoice_date":"InvoiceDate"
    })
    frame.to_csv(source, index=False)
    output = tmp_path / "processed"
    cfg = RuleConfig(algorithm="pairwise", min_support=.01, max_products=3,
                     min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0)
    manifest = run_pipeline(source, output, cfg, train_fraction=.7)
    assert manifest["basket_count_all"] == 10
    assert manifest["rule_count"] > 0
    assert manifest["train_baskets"] + manifest["holdout_baskets"] == 10
    assert len(manifest["source_sha256"]) == 64
    assert (output / "rules.csv").is_file()
    assert (output / "evaluation.csv").is_file()
    assert (output / "monthly_country.csv").is_file()
    assert (output / "products.csv").is_file()
    assert (output / "basket_summary.csv.gz").is_file()
    q = json.loads((output / "quality.json").read_text())
    assert q["valid_rows"] == 20
    rules = pd.read_csv(output / "rules.csv")
    assert (rules["joint_count"] >= 1).all()
    metadata = json.loads((output / "manifest.json").read_text())
    assert metadata["method"]["algorithm"] == "pairwise"
    # Atomic replacement should allow reruns without stale output.
    again = run_pipeline(source, output, cfg, train_fraction=.7)
    assert again["rule_count"] == manifest["rule_count"]
    assert not (tmp_path / "processed.previous").exists()
