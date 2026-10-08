"""Command-line entry point for reproducible BasketLens builds."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from basketlens.mining import RuleConfig


def parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(description="BasketLens retail market basket analysis")
    sub = parent.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("download", help="Download official UCI Online Retail II ZIP")
    fetch.add_argument("--dir", default="data/raw", help="Gitignored raw dataset directory")
    doctor = sub.add_parser("doctor", help="Check the local runtime and data readiness")
    doctor.add_argument("--input", default="data/raw/online_retail_II.xlsx")
    doctor.add_argument("--output", default="data/processed")
    verify = sub.add_parser("verify", help="Audit the processed output without the raw workbook")
    verify.add_argument("--output", default="data/processed")
    build = sub.add_parser("build", help="Clean, mine and validate retail association rules")
    build.add_argument("--input", default="data/raw/online_retail_II.xlsx")
    build.add_argument("--output", default="data/processed")
    build.add_argument("--algorithm", choices=["pairwise", "fpgrowth"], default="fpgrowth")
    build.add_argument("--max-products", type=int, default=160)
    build.add_argument("--min-support", type=float, default=0.002)
    build.add_argument("--min-item-count", type=int, default=15)
    build.add_argument("--min-joint-count", type=int, default=20)
    build.add_argument("--min-confidence", type=float, default=0.15)
    build.add_argument("--min-lift", type=float, default=1.05)
    build.add_argument("--max-itemset-len", type=int, default=3)
    build.add_argument("--train-fraction", type=float, default=0.8)
    build.add_argument("--inconsistent-policy", choices=["fail", "quarantine"],
                       default="fail", help="Fail closed or explicitly drop conflicting invoices")
    build.add_argument("--max-rows-per-sheet", type=int, default=None,
                       help="Development-only subset (marked partial, not full-data conclusions)")
    return parent


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "download":
            from basketlens.download import download_uci
            path = download_uci(Path(args.dir))
            print(f"Downloaded: {path}")
            return 0
        if args.command == "doctor":
            from importlib.util import find_spec
            import sys
            dependencies = {name: find_spec(name) is not None for name in
                            ("pandas", "numpy", "scipy", "openpyxl", "mlxtend",
                             "streamlit", "plotly", "networkx", "requests")}
            report = {"python_version": sys.version.split()[0],
                      "source_workbook_available": Path(args.input).is_file(),
                      "processed_manifest_available": (Path(args.output) / "manifest.json").is_file(),
                      "dependencies": dependencies,
                      "note": "This readiness check does not verify dataset provenance or model quality."}
            print(json.dumps(report, indent=2))
            return 0
        if args.command == "verify":
            from basketlens.validation import validate_artifacts
            print(json.dumps(validate_artifacts(args.output), indent=2))
            return 0
        from basketlens.pipeline import run_pipeline
        config = RuleConfig(algorithm=args.algorithm, max_products=args.max_products,
                            min_support=args.min_support, min_item_count=args.min_item_count,
                            min_joint_count=args.min_joint_count,
                            min_confidence=args.min_confidence, min_lift=args.min_lift,
                            max_itemset_len=args.max_itemset_len)
        result = run_pipeline(args.input, args.output, config, args.max_rows_per_sheet,
                              args.train_fraction, args.inconsistent_policy)
        print(json.dumps({k: result[k] for k in ["basket_count_all", "train_baskets",
                         "holdout_baskets", "rule_count", "cutoff_utc_naive"]}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, MemoryError) as error:
        parser().exit(1, f"BasketLens error: {error}\n")

if __name__ == "__main__":
    raise SystemExit(main())
