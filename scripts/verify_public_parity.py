"""Ensure the exact checked-in public exhibit matches a fresh, audited UCI build."""
from __future__ import annotations

import argparse
from pathlib import Path

from pandas.testing import assert_frame_equal
from basketlens.public_demo import FRAMES, load_public_demo


def verify(published: Path, generated: Path) -> None:
    pub = load_public_demo(published)
    fresh = load_public_demo(generated)
    if pub["publication"] != fresh["publication"] or pub["quality"] != fresh["quality"]:
        raise AssertionError("Public exhibit metadata and quality differ")
    left, right = dict(pub["manifest"]), dict(fresh["manifest"])
    left.pop("generated_at_utc", None)
    right.pop("generated_at_utc", None)
    if left != right:
        raise AssertionError("Public exhibit provenance differs from freshly generated run")
    for name in FRAMES:
        assert_frame_equal(pub[name], fresh[name], check_dtype=False,
                           check_exact=False, rtol=1e-10, atol=1e-8)
    print("PUBLIC_EXHIBIT_PARITY_PASS aggregate tables, rules, holdout and source fingerprint")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--generated", type=Path, required=True)
    args = parser.parse_args()
    verify(args.published, args.generated)


if __name__ == "__main__":
    main()
