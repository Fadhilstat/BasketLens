"""CLI workflow tests on synthetic inputs, without spawning expensive subprocesses."""
import json

from basketlens.cli import main


def test_doctor_reports_real_environment_readiness(capsys):
    assert main(["doctor", "--input", "/no/such/source.xlsx"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert not status["source_workbook_available"]
    assert status["dependencies"]["pandas"]


def test_build_then_verify_using_synthetic_source(raw_fixture, tmp_path, capsys):
    source = tmp_path / "not_uci_synthetic_TEST_ONLY.csv"
    raw_fixture.drop(columns=["source_sheet", "source_row"]).rename(columns={
        "invoice_no": "Invoice", "stock_code": "StockCode", "unit_price": "Price",
        "customer_id": "Customer ID", "invoice_date": "InvoiceDate"
    }).to_csv(source, index=False)
    processed = tmp_path / "output"
    assert main(["build", "--input", str(source), "--output", str(processed),
                 "--algorithm", "pairwise", "--min-support", ".01",
                 "--min-item-count", "1", "--min-joint-count", "1",
                 "--min-confidence", "0", "--min-lift", "0",
                 "--train-fraction", ".7"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["basket_count_all"] == 10
    assert main(["verify", "--output", str(processed)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PASS"
