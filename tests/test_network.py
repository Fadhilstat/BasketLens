"""The affinity network must faithfully represent observed pairwise rules."""
import pandas as pd

from basketlens.network import affinity_edges, network_figure


def test_network_omits_multi_sku_antecedents_and_deduplicates_directions():
    frame = pd.DataFrame({
        "antecedent": ["A", "B", "A||B", "B"],
        "consequent": ["B", "A", "C", "C"],
        "antecedent_size": [1, 1, 2, 1],
        "consequent_size": [1, 1, 1, 1],
        "joint_count": [12, 12, 10, 3],
        "lift": [1.8, 1.8, 2.1, 1.2],
        "confidence": [.6, .5, .8, .2]
    })
    edges = affinity_edges(frame, min_joint=2)
    assert len(edges) == 2
    assert {tuple(x) for x in edges[["product_a", "product_b"]].to_numpy()} == {("A", "B"), ("B", "C")}
    limited = affinity_edges(frame, max_edges=1, max_nodes=2)
    assert len(limited) == 1
    figure = network_figure(edges, {"A": "Mug", "B": "Tray", "C": "Vase"})
    assert len(figure.data) == len(edges) + 1


def test_empty_network_works():
    assert affinity_edges(pd.DataFrame()).empty
    assert len(network_figure(pd.DataFrame(), {}).data) == 0
