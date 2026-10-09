"""Fast, no-network GitHub and cloud release check for the public exhibit."""
from pathlib import Path

from basketlens.public_demo import PUBLIC_FILENAME, load_public_demo

path = Path(__file__).resolve().parents[1] / "data" / "public_demo" / PUBLIC_FILENAME
data = load_public_demo(path)
assert len(data["rules"]) == 1500, "Expected curated public rule sample"
assert data["publication"]["full_rule_count"] == 113001, "Expected UCI audited full rule count"
assert int(data["basket_rollup"]["basket_count"].sum()) == 40280
print("PUBLISHED_LOAD_PASS 1500 selected rules, 40280 baskets, SHA256 verified")
