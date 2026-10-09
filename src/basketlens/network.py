"""Deterministic and bounded product affinity network for exploratory reporting."""
from __future__ import annotations

import math
from html import escape

import networkx as nx
import pandas as pd
import plotly.graph_objects as go

EDGE_COLUMNS = ["product_a", "product_b", "joint_count", "lift", "confidence_ab"]


def affinity_edges(rules: pd.DataFrame, max_edges: int = 36,
                   max_nodes: int = 24, min_joint: int = 1) -> pd.DataFrame:
    """Deduplicate symmetric 1-to-1 rules and restrict visual network size.

    Multi-product antecedents are valid rules but not honest pairwise graph edges.
    """
    if max_edges < 1 or max_nodes < 2 or min_joint < 1:
        raise ValueError("Invalid network display limits")
    if rules.empty:
        return pd.DataFrame(columns=EDGE_COLUMNS)
    selected = rules.loc[(rules["antecedent_size"] == 1) &
                         (rules["consequent_size"] == 1) &
                         (rules["joint_count"] >= min_joint)].copy()
    if selected.empty:
        return pd.DataFrame(columns=EDGE_COLUMNS)
    selected["product_a"] = selected[["antecedent", "consequent"]].min(axis=1)
    selected["product_b"] = selected[["antecedent", "consequent"]].max(axis=1)
    selected = selected.loc[selected["product_a"].ne(selected["product_b"])]
    selected = selected.sort_values(["joint_count", "lift", "antecedent"],
                                    ascending=[False, False, True])
    selected = selected.drop_duplicates(["product_a", "product_b"])
    chosen, nodes = [], set()
    for row in selected.itertuples(index=False):
        candidates = nodes | {row.product_a, row.product_b}
        if len(candidates) > max_nodes:
            continue
        chosen.append({"product_a": row.product_a, "product_b": row.product_b,
                       "joint_count": int(row.joint_count), "lift": float(row.lift),
                       "confidence_ab": float(row.confidence)})
        nodes = candidates
        if len(chosen) == max_edges:
            break
    return pd.DataFrame(chosen, columns=EDGE_COLUMNS)


def network_figure(edges: pd.DataFrame, name_map: dict[str, str]) -> go.Figure:
    """One trace per graph edge with data-only hover information."""
    fig = go.Figure()
    if edges.empty:
        return fig
    graph = nx.Graph()
    for row in edges.itertuples(index=False):
        graph.add_edge(row.product_a, row.product_b, weight=math.log1p(row.joint_count))
    positions = nx.spring_layout(graph, seed=42, weight="weight", iterations=160,
                                 k=1.4 / math.sqrt(max(1, graph.number_of_nodes())))
    max_count = max(edges["joint_count"])
    for row in edges.itertuples(index=False):
        start, end = positions[row.product_a], positions[row.product_b]
        label = (f"{row.product_a} + {row.product_b}<br>"
                 f"{row.joint_count:,} co-purchase baskets<br>Training lift: {row.lift:.2f}")
        width = 1.0 + 2.5 * math.log1p(row.joint_count) / math.log1p(max_count)
        fig.add_trace(go.Scatter(x=[start[0], end[0]], y=[start[1], end[1]],
                                 mode="lines", line={"color": "#afc2b5", "width": width},
                                 text=[label, label], hovertemplate="%{text}<extra></extra>",
                                 showlegend=False))
    nodes = sorted(graph.nodes())
    node_text = [f"{escape(str(name_map.get(node, 'Unknown product')).strip().title())}"
                 f"<br>SKU: {escape(str(node))}<br>Visible links: {graph.degree(node)}" for node in nodes]
    # The old text labels collided. Keep details in accessible table and in
    # per-node hover/touch descriptions, not on top of each other in the graph.
    fig.add_trace(go.Scatter(x=[positions[node][0] for node in nodes],
                             y=[positions[node][1] for node in nodes], mode="markers",
                             hovertext=node_text, hovertemplate="%{hovertext}<extra></extra>",
                             marker={"color": "#147a58",
                                     "size": [min(25, 12 + graph.degree(node) * 2) for node in nodes],
                                     "line": {"color": "#ffffff", "width": 1.7}},
                             showlegend=False))
    fig.update_layout(height=410, margin={"l": 12, "r": 12, "t": 12, "b": 12},
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis={"visible": False}, yaxis={"visible": False},
                      hovermode="closest", dragmode="pan")
    return fig