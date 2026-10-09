"""Export a small, verified aggregate-only exhibit for Streamlit Community Cloud."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from basketlens.public_demo import PUBLIC_FILENAME, build_public_demo, load_public_demo


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/public_demo"))
    parser.add_argument("--emit", action="store_true",
                        help="Print base64 as labelled chunks for a controlled release transfer")
    args = parser.parse_args()
    result = build_public_demo(args.input, args.output)
    loaded = load_public_demo(args.output / PUBLIC_FILENAME)
    assert loaded["publication"]["visible_rule_count"] == result["visible_rule_count"]
    print("PUBLIC_DEMO_VALIDATED " + json.dumps(result, sort_keys=True), flush=True)
    if args.emit:
        code = (args.output / PUBLIC_FILENAME).read_text(encoding="ascii").strip()
        print(f"PUBLIC_DEMO_BASE64_BEGIN {len(code)}", flush=True)
        for idx in range(0, len(code), 8000):
            print(f"PUBLIC_DEMO_B64 {idx // 8000:04d} {code[idx:idx+8000]}", flush=True)
        print("PUBLIC_DEMO_BASE64_END", flush=True)
        print("PUBLIC_DEMO_SHA256 " +
              (args.output / f"{PUBLIC_FILENAME}.sha256").read_text().strip(), flush=True)


if __name__ == "__main__":
    main()
