"""Public exhibit is reproducible and contains no invoice or customer details."""
import json

import pandas as pd
import pytest

from basketlens.mining import RuleConfig
from basketlens.pipeline import run_pipeline
from basketlens.public_demo import PUBLIC_FILENAME, build_public_demo, load_public_demo


def test_public_bundle_uses_aggregate_only_outputs(tmp_path, raw_fixture):
    source = tmp_path / "source.csv"
    raw_fixture.drop(columns=["source_sheet", "source_row"]).to_csv(source, index=False)
    output = tmp_path / "processed"
    cfg = RuleConfig(algorithm="pairwise", min_support=.01, max_products=3,
                     min_item_count=1, min_joint_count=1, min_confidence=0, min_lift=0)
    run_pipeline(source, output, cfg, train_fraction=.7, inconsistent_policy="quarantine")
    # Synthetic fixture only: verify provenance guard using test manifest.
    mpath = output / "manifest.json"
    manifest = json.loads(mpath.read_text())
    manifest["method"]["algorithm"] = "fpgrowth"
    mpath.write_text(json.dumps(manifest))
    dest = tmp_path / "public"
    result = build_public_demo(output, dest, pair_limit=10, multi_limit=2)
    exhibit = load_public_demo(dest / PUBLIC_FILENAME)
    assert result["status"] == "PASS"
    assert exhibit["basket_rollup"]["basket_count"].sum() == 10
    assert len(exhibit["rules"]) == len(exhibit["evaluation"])
    assert not {"customer_id", "invoice_no", "source_row", "basket_id"} & set(exhibit["basket_rollup"])
    encoded = (dest / PUBLIC_FILENAME).read_text()
    (dest / PUBLIC_FILENAME).write_text(
        encoded[:12] + ("A" if encoded[12] != "A" else "B") + encoded[13:]
    )
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_public_demo(dest / PUBLIC_FILENAME)


def test_train_rule_selection_never_uses_holdout_metrics():
    from basketlens.public_demo import _select_rules
    rules = pd.DataFrame([
        {"antecedent": "A", "consequent": "B", "joint_count": 40, "confidence": .3, "lift": 1.1},
        {"antecedent": "A", "consequent": "C", "joint_count": 20, "confidence": .8, "lift": 2.4},
        {"antecedent": "A||B", "consequent": "C", "joint_count": 100, "confidence": .8, "lift": 4.0},
    ])
    out = _select_rules(rules, pair_limit=1, multi_limit=1)
    assert list(out.antecedent) == ["A", "A||B"]
    assert list(out.consequent) == ["B", "C"]
