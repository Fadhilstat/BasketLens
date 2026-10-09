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
    assert figure.data[-1].mode == "markers"
    assert all("SKU:" in text for text in figure.data[-1].hovertext)


def test_empty_network_works():
    assert affinity_edges(pd.DataFrame()).empty
    assert len(network_figure(pd.DataFrame(), {}).data) == 0


def test_affinity_network_does_not_overlap_product_labels():
    from basketlens.network import network_figure
    import pandas as pd
    edges = pd.DataFrame([{"product_a": "A", "product_b": "B", "joint_count": 100,
                           "lift": 2.3, "confidence_ab": .6}])
    fig = network_figure(edges, {"A": "JUMBO PINK BAG", "B": "JUMBO RED BAG"})
    assert fig.data[-1].mode == "markers"
    assert "text" not in fig.data[-1].mode
    assert all("SKU:" in text for text in fig.data[-1].hovertext)
    assert fig.layout.height == 410