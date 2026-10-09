"""Basket association miners with bounded candidate space and transparent metrics."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

RULE_COLUMNS = [
    "antecedent", "consequent", "antecedent_size", "consequent_size",
    "train_baskets", "antecedent_count", "consequent_count", "joint_count",
    "support", "antecedent_support", "consequent_support", "confidence",
    "lift", "leverage", "algorithm"
]

@dataclass(frozen=True)
class RuleConfig:
    algorithm: str = "pairwise"
    max_products: int = 160
    min_support: float = 0.002
    min_item_count: int = 15
    min_joint_count: int = 20
    min_confidence: float = 0.15
    min_lift: float = 1.05
    max_itemset_len: int = 3

    def validate(self) -> None:
        if self.algorithm not in {"pairwise", "fpgrowth"}:
            raise ValueError("algorithm must be pairwise or fpgrowth")
        if self.max_products < 2 or self.max_products > 600:
            raise ValueError("max_products must be between 2 and 600")
        if not 0 < self.min_support <= 1 or not 0 <= self.min_confidence <= 1:
            raise ValueError("support and confidence must be between 0 and 1")
        if self.min_item_count < 1 or self.min_joint_count < 1 or self.min_lift < 0:
            raise ValueError("Minimum counts must be positive and min_lift nonnegative")
        if self.max_itemset_len < 2 or self.max_itemset_len > 3:
            raise ValueError("max_itemset_len must be 2 or 3")


def _selected_items(items: pd.DataFrame, config: RuleConfig) -> list[str]:
    counts = items.drop_duplicates(["basket_id", "stock_code"])["stock_code"].value_counts()
    eligible = counts[counts >= config.min_item_count]
    # Stable tie-breaking by SKU makes product selection reproducible across runs.
    ranked = sorted(eligible.items(), key=lambda entry: (-int(entry[1]), str(entry[0])))
    return [str(product) for product, _ in ranked[:config.max_products]]


def _transaction_matrix(baskets: pd.DataFrame, items: pd.DataFrame,
                        products: list[str]) -> csr_matrix:
    """Only selected candidates populate the matrix; all baskets remain in denominator."""
    ids = {str(b): i for i, b in enumerate(baskets["basket_id"].astype(str))}
    codes = {p: j for j, p in enumerate(products)}
    relevant = items.loc[items["stock_code"].isin(products), ["basket_id", "stock_code"]].drop_duplicates()
    row = relevant["basket_id"].astype(str).map(ids)
    col = relevant["stock_code"].astype(str).map(codes)
    valid = row.notna() & col.notna()
    arr = csr_matrix((np.ones(int(valid.sum()), dtype=np.int32),
                      (row[valid].to_numpy(dtype=int), col[valid].to_numpy(dtype=int))),
                     shape=(len(baskets), len(products)), dtype=np.int32)
    arr.data[:] = 1
    return arr


def _candidate_diagnostics(matrix: csr_matrix, products: list[str],
                           items: pd.DataFrame) -> dict:
    per_basket = matrix.getnnz(axis=1)
    n = matrix.shape[0]
    return {
        "candidate_products": len(products),
        "training_products_all": int(items["stock_code"].nunique()),
        "baskets_with_selected_product": int((per_basket >= 1).sum()),
        "baskets_with_two_selected_products": int((per_basket >= 2).sum()),
        "candidate_basket_coverage": float((per_basket >= 1).sum() / n) if n else 0.0,
        "candidate_pair_coverage": float((per_basket >= 2).sum() / n) if n else 0.0,
        "product_selection": "Top SKUs by training-basket frequency; SKU lexical tie-break",
    }


def _finish_rules(rules: pd.DataFrame, config: RuleConfig) -> pd.DataFrame:
    if rules.empty:
        return pd.DataFrame(columns=RULE_COLUMNS)
    out = rules.loc[(rules["support"] >= config.min_support) &
                    (rules["joint_count"] >= config.min_joint_count) &
                    (rules["confidence"] >= config.min_confidence) &
                    (rules["lift"] >= config.min_lift)].copy()
    if out.empty:
        return pd.DataFrame(columns=RULE_COLUMNS)
    return (out[RULE_COLUMNS].sort_values(["lift", "joint_count", "confidence"],
                 ascending=[False, False, False]).reset_index(drop=True))


def mine_pairwise(baskets: pd.DataFrame, items: pd.DataFrame,
                  config: RuleConfig) -> tuple[pd.DataFrame, dict]:
    """Exact observed 1->1 associations on a frequency-selected product universe.

    Uses sparse matrix multiplication. Do not call this FP-Growth; the algorithm
    is a bounded pairwise baseline with interpretable coverage restrictions.
    """
    config.validate()
    n = int(len(baskets))
    if n == 0:
        raise ValueError("No training baskets")
    products = _selected_items(items, config)
    if len(products) < 2:
        X = _transaction_matrix(baskets, items, products)
        return pd.DataFrame(columns=RULE_COLUMNS), {
            **_candidate_diagnostics(X, products, items), "train_baskets": n}
    X = _transaction_matrix(baskets, items, products)
    meta = {**_candidate_diagnostics(X, products, items), "train_baskets": n}
    popularity = np.asarray(X.sum(axis=0)).ravel().astype(int)
    joints = (X.T @ X).tocoo()
    floor = max(config.min_joint_count, math.ceil(config.min_support * n - 1e-9))
    keep = (joints.row < joints.col) & (joints.data >= floor)
    a, b, together = joints.row[keep], joints.col[keep], joints.data[keep].astype(int)
    if len(a) == 0:
        return pd.DataFrame(columns=RULE_COLUMNS), meta
    # Both directions have the same joint support but different confidences.
    a_all = np.concatenate([a, b])
    b_all = np.concatenate([b, a])
    joint_all = np.concatenate([together, together])
    antecedent_n = popularity[a_all]
    consequent_n = popularity[b_all]
    support_ab = joint_all / n
    antecedent_s = antecedent_n / n
    consequent_s = consequent_n / n
    confidence = joint_all / antecedent_n
    lift = confidence / consequent_s
    out = pd.DataFrame({
        "antecedent": [products[i] for i in a_all],
        "consequent": [products[i] for i in b_all],
        "antecedent_size": 1, "consequent_size": 1,
        "train_baskets": n, "antecedent_count": antecedent_n,
        "consequent_count": consequent_n, "joint_count": joint_all,
        "support": support_ab, "antecedent_support": antecedent_s,
        "consequent_support": consequent_s, "confidence": confidence,
        "lift": lift, "leverage": support_ab - (antecedent_s * consequent_s),
        "algorithm": "pairwise_sparse",
    })
    return _finish_rules(out, config), meta


def mine_fpgrowth(baskets: pd.DataFrame, items: pd.DataFrame,
                   config: RuleConfig) -> tuple[pd.DataFrame, dict]:
    """Bounded FP-Growth (itemsets size <= 3). Requires mlxtend at runtime."""
    config.validate()
    try:
        from mlxtend.frequent_patterns import fpgrowth, association_rules
    except ImportError as exc:
        raise RuntimeError("FP-Growth requires mlxtend. Install the full project dependencies.") from exc
    n = int(len(baskets))
    if n == 0:
        raise ValueError("No training baskets")
    products = _selected_items(items, config)
    if len(products) < 2:
        X = _transaction_matrix(baskets, items, products)
        return pd.DataFrame(columns=RULE_COLUMNS), {
            **_candidate_diagnostics(X, products, items), "train_baskets": n}
    X = _transaction_matrix(baskets, items, products)
    meta = {**_candidate_diagnostics(X, products, items), "train_baskets": n}
    # Bound dense memory explicitly; 160 x 50k ~ 8 MB boolean matrix.
    if X.shape[0] * X.shape[1] > 35_000_000:
        raise MemoryError("Candidate matrix too large for FP-Growth. Reduce max_products or use pairwise.")
    binary = pd.DataFrame(X.toarray().astype(bool), columns=products)
    freq = fpgrowth(binary, min_support=config.min_support,
                    use_colnames=True, max_len=config.max_itemset_len)
    if freq.empty or max(map(len, freq["itemsets"])) < 2:
        return pd.DataFrame(columns=RULE_COLUMNS), meta
    try:
        assoc = association_rules(freq, metric="confidence", min_threshold=config.min_confidence,
                                  num_itemsets=n)
    except TypeError:
        assoc = association_rules(freq, metric="confidence", min_threshold=config.min_confidence)
    if assoc.empty:
        return pd.DataFrame(columns=RULE_COLUMNS), meta
    assoc = assoc.loc[assoc["consequents"].map(len).eq(1) &
                      assoc["antecedents"].map(len).le(2)].copy()
    if assoc.empty:
        return pd.DataFrame(columns=RULE_COLUMNS), meta
    out = pd.DataFrame({
        "antecedent": assoc["antecedents"].map(lambda x: "||".join(sorted(x))).to_numpy(),
        "consequent": assoc["consequents"].map(lambda x: "||".join(sorted(x))).to_numpy(),
        "antecedent_size": assoc["antecedents"].map(len).to_numpy(),
        "consequent_size": assoc["consequents"].map(len).to_numpy(),
        "train_baskets": n,
        "antecedent_count": np.rint(assoc["antecedent support"].to_numpy() * n).astype(int),
        "consequent_count": np.rint(assoc["consequent support"].to_numpy() * n).astype(int),
        "joint_count": np.rint(assoc["support"].to_numpy() * n).astype(int),
        "support": assoc["support"].to_numpy(),
        "antecedent_support": assoc["antecedent support"].to_numpy(),
        "consequent_support": assoc["consequent support"].to_numpy(),
        "confidence": assoc["confidence"].to_numpy(),
        "lift": assoc["lift"].to_numpy(),
        "leverage": assoc["leverage"].to_numpy(),
        "algorithm": "fpgrowth",
    })
    return _finish_rules(out, config), {**meta, "frequent_itemsets": int(len(freq))}


def mine_rules(baskets: pd.DataFrame, items: pd.DataFrame,
               config: RuleConfig) -> tuple[pd.DataFrame, dict]:
    if config.algorithm == "pairwise":
        return mine_pairwise(baskets, items, config)
    return mine_fpgrowth(baskets, items, config)


def matching_rules(rules: pd.DataFrame, cart: list[str]) -> pd.DataFrame:
    """Return every matching rule before deduplication or ranking."""
    if not cart or rules.empty:
        return pd.DataFrame(columns=list(rules.columns) + ["matched_items"])
    selected = set(cart)
    valid = rules.loc[rules["antecedent"].astype(str).map(
        lambda s: set(s.split("||")).issubset(selected)) &
        (~rules["consequent"].astype(str).map(lambda s: bool(set(s.split("||")) & selected)))].copy()
    if valid.empty:
        return valid.assign(matched_items=pd.Series(dtype=int))
    valid["matched_items"] = valid["antecedent_size"]
    return valid


def recommend(rules: pd.DataFrame, cart: list[str], limit: int = 10) -> pd.DataFrame:
    """Training-only baseline ranking. Prefer holdout-aware candidates for decisions."""
    valid = matching_rules(rules, cart)
    if valid.empty:
        return valid
    valid = valid.sort_values(["matched_items", "lift", "confidence", "joint_count"],
                              ascending=[False, False, False, False])
    return valid.drop_duplicates("consequent").head(limit).reset_index(drop=True)
