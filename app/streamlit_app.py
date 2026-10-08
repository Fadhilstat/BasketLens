"""Interactive BasketLens retail research interface."""
from __future__ import annotations

import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from basketlens.insights import annotate_evidence, recommend_with_holdout
from basketlens.network import affinity_edges, network_figure

st.set_page_config(page_title="BasketLens | Retail intelligence", page_icon="🧺",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root {--paper:#f8f6f0;--ink:#252a26;--muted:#636962;--accent:#83552f;}
html, body, [class*="css"] {font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;}
.stApp {background:var(--paper); color:var(--ink);}
.block-container {max-width:1320px; padding-top:1.7rem; padding-bottom:4rem;}
h1,h2,h3 {color:var(--ink); letter-spacing:-.028em;}
h1 {font-family:Georgia, 'Times New Roman',serif; font-size:clamp(2.2rem,4.4vw,3.7rem)!important;}
[data-testid="stMetric"] {background:#fffefa; border:1px solid #e6e2d8; padding:1rem; border-radius:.45rem;}
[data-testid="stSidebar"] {background:#efeee7;}
[data-testid="stMetricValue"] {color:#333c31;}
.stButton > button, .stDownloadButton > button {border-radius:.35rem; min-height:2.5rem;}
:focus-visible {outline:3px solid #7b6746!important; outline-offset:2px;}
.muted {color:#68706a; font-size:.91rem;}
.eyebrow {text-transform:uppercase; letter-spacing:.13em; font-size:.79rem;
          font-weight:700; color:#825a39;}
.note {border-left:3px solid #ae926b; padding:.7rem 1rem; background:#f0ebe0; color:#444a40;}
</style>""", unsafe_allow_html=True)

BASE_DIR = Path(os.environ.get("BASKETLENS_DATA_DIR", "data/processed"))

@st.cache_data(show_spinner=False)
def load_data(base: str, manifest_mtime: float) -> dict:
    path = Path(base)
    result = {
        "manifest": json.loads((path / "manifest.json").read_text(encoding="utf-8")),
        "quality": json.loads((path / "quality.json").read_text(encoding="utf-8")),
    }
    for name in ("products", "countries", "monthly", "monthly_country", "rules", "evaluation"):
        types = ({"stock_code": str} if name == "products" else
                 {"antecedent": str, "consequent": str} if name in {"rules", "evaluation"} else None)
        result[name] = pd.read_csv(path / f"{name}.csv", dtype=types)
    result["baskets"] = pd.read_csv(path / "basket_summary.csv.gz", parse_dates=["invoice_date"])
    return result

if not (BASE_DIR / "manifest.json").exists():
    st.markdown('<p class="eyebrow">Research workspace · data not prepared</p>', unsafe_allow_html=True)
    st.title("BasketLens")
    st.write("Analyse real transaction patterns and test cross-selling rules against later orders.")
    st.warning("No processed dataset found. Generate the research artifacts before launching the dashboard.")
    st.code("python -m basketlens.cli download\npython -m basketlens.cli build --algorithm fpgrowth\nstreamlit run app/streamlit_app.py", language="bash")
    st.markdown("Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)."
                " If the download command fails, download the workbook from UCI manually into `data/raw/`.")
    st.stop()

try:
    d = load_data(str(BASE_DIR.resolve()), (BASE_DIR / "manifest.json").stat().st_mtime)
except (OSError, ValueError, json.JSONDecodeError, KeyError) as error:
    st.error(f"Cannot read processed analytics data: {error}")
    st.stop()

m, q = d["manifest"], d["quality"]
products = d["products"]
name_map = dict(zip(products["stock_code"].astype(str), products["description"].fillna("Unknown")))

def display_product(sku: str) -> str:
    values = str(sku).split("||")
    return " + ".join(f"{name_map.get(part, 'Unknown item')} ({part})" for part in values)

st.sidebar.markdown("<div class='eyebrow'>BasketLens / Research</div>", unsafe_allow_html=True)
st.sidebar.caption("Dataset: UCI-style retail transactions. Analysis does not use live sales.")
st.sidebar.markdown("**Build details**")
st.sidebar.write(f"Model: `{m['method']['algorithm']}`")
st.sidebar.write(f"Rule training baskets: {m['train_baskets']:,}")
st.sidebar.write(f"Holdout baskets: {m['holdout_baskets']:,}")
st.sidebar.write(f"Cutoff: {m['cutoff_utc_naive'][:10]}")
if m.get("partial_data"):
    st.sidebar.warning("Partial dataset build. Results are for testing only.")
country_options = ["All countries"] + d["countries"]["country"].astype(str).tolist()
selected_country = st.sidebar.selectbox("Country for sales overview", country_options,
                                         help="Changes sales KPIs only. Rules are trained across all countries.")
st.sidebar.info("Country selection affects the overview only. The model and holdout remain global.")

st.markdown(f'<p class="eyebrow">Historical commerce analysis / {m["data_first_invoice"][:10]}'
            f' to {m["data_last_invoice"][:10]}</p>', unsafe_allow_html=True)
st.title("BasketLens")
st.markdown("<div class='muted'>Turn purchase patterns into testable retail decisions."
            " Based on observed transactions, not sales uplift experiments.</div>", unsafe_allow_html=True)
st.write("")

overview, explorer, builder, quality = st.tabs([
    "Sales overview", "Association explorer", "Build a basket", "Data quality & methodology"
])

with overview:
    st.subheader("Historical performance")
    if selected_country == "All countries":
        monthly = d["monthly"]
        selected_baskets = d["baskets"]
    else:
        monthly = d["monthly_country"].loc[
            d["monthly_country"]["country"].astype(str).eq(selected_country)]
        selected_baskets = d["baskets"].loc[d["baskets"]["country"].astype(str).eq(selected_country)]
    col1, col2, col3 = st.columns(3)
    col1.metric("Recorded sales value", f"£{selected_baskets['basket_revenue_gbp'].sum():,.0f}")
    col2.metric("Valid baskets", f"{len(selected_baskets):,}")
    col3.metric("Average basket value", f"£{selected_baskets['basket_revenue_gbp'].mean():,.2f}" if len(selected_baskets) else "N/A")
    if not monthly.empty:
        fig = px.line(monthly.sort_values("month"), x="month", y="sales_gbp", markers=True,
                      labels={"month":"Invoice month", "sales_gbp":"Sales value (£)"},
                      color_discrete_sequence=["#83552f"])
        fig.update_layout(height=335, margin=dict(l=5, r=10, t=20, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No monthly sales data for the selected country.")
    c1,c2 = st.columns([1.4,1])
    with c1:
        st.markdown("**Largest products by historical sales value**")
        st.caption("Global product ranking. Country filter does not affect this chart.")
        top = products.nlargest(12, "sales_gbp").copy()
        top["product"] = top["description"].astype(str).str.slice(0, 36)
        fig2 = px.bar(top.sort_values("sales_gbp"), x="sales_gbp", y="product", orientation="h",
                      labels={"sales_gbp":"Sales value (£)","product":"Product"},
                      color_discrete_sequence=["#a77e52"])
        fig2.update_layout(height=470, margin=dict(l=5,r=10,t=5,b=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        st.markdown("**Basket composition**")
        dist = selected_baskets["item_count"].clip(upper=20).value_counts().sort_index().reset_index()
        dist.columns = ["distinct_products", "baskets"]
        if not dist.empty:
            fig3 = px.bar(dist, x="distinct_products", y="baskets",
                          labels={"distinct_products":"Distinct SKUs (20 includes 20+)", "baskets":"Baskets"},
                          color_discrete_sequence=["#587062"])
            fig3.update_layout(height=360, margin=dict(l=5,r=10,t=5,b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)
        st.caption("Basket means one invoice within its source year. Item count uses distinct SKUs.")

with explorer:
    st.subheader("Association explorer")
    st.caption("Association rules are trained on earlier baskets. Filtering below changes the display, not the trained model.")
    rules = d["rules"].copy()
    if rules.empty:
        st.warning("No rules passed the configured thresholds. Rebuild with suitable settings.")
    else:
        highest_lift = max(1.0, float(rules["lift"].max()))
        min_lift = st.slider("Minimum observed training lift", min_value=0.0,
                             max_value=float(max(2.0, round(highest_lift + 0.5, 1))),
                             value=float(min(1.2, highest_lift)), step=0.1)
        min_joint = st.number_input("Minimum training co-occurrences", min_value=1,
                                   max_value=max(1, int(rules["joint_count"].max())),
                                   value=min(20, max(1, int(rules["joint_count"].max()))))
        checked = rules.loc[rules["lift"].ge(min_lift) & rules["joint_count"].ge(min_joint)].copy()
        st.caption(f"{len(checked):,} of {len(rules):,} rules match your display filters.")
        if not checked.empty:
            checked["If basket has"] = checked["antecedent"].map(display_product)
            checked["Recommend"] = checked["consequent"].map(display_product)
            shown = checked[["If basket has", "Recommend", "support", "confidence", "lift", "joint_count"]].copy()
            st.dataframe(shown.rename(columns={"support":"Support", "confidence":"Confidence",
                                              "lift":"Lift", "joint_count":"Transactions together"}),
                         use_container_width=True, hide_index=True)
            st.download_button("Export filtered rules (CSV)", checked.to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_filtered_rules.csv", mime="text/csv")
        else:
            st.info("No rules meet these thresholds. Adjust the filters.")
        st.subheader("Product affinity map")
        st.caption("Each line is an observed two-product association."
                   " Multiple-item antecedents are excluded from this pairwise map."
                   " Layout distances have no numerical meaning.")
        edge_limit = st.slider("Maximum links on the map", min_value=5, max_value=40, value=26,
                               help="Only the strongest displayed co-purchases are drawn to keep the map legible.")
        edges = affinity_edges(checked, max_edges=edge_limit, max_nodes=24, min_joint=1)
        if edges.empty:
            st.info("There are no eligible two-product links under these filters.")
        else:
            st.plotly_chart(network_figure(edges, name_map), use_container_width=True)
            st.caption(f"Showing {len(edges)} unique product pairs. Link thickness reflects co-purchase count.")
    st.subheader("Out-of-time stability")
    evaluation = d["evaluation"].copy()
    if evaluation.empty:
        st.info("No rules available for holdout evaluation.")
    else:
        min_fires = st.number_input("Minimum holdout rule firings", min_value=1,
                                    value=20, step=1,
                                    help="Descriptive evidence threshold, not a significance test.")
        evaluation = annotate_evidence(evaluation, min_fires=int(min_fires))
        stable = evaluation.loc[evaluation["fires"].ge(min_fires)].copy()
        if stable.empty:
            st.info("No rules fire often enough in the holdout. Reduce this threshold to inspect exploratory results.")
        else:
            stable["If"] = stable["antecedent"].map(display_product)
            stable["Then"] = stable["consequent"].map(display_product)
            st.dataframe(stable[["If", "Then", "fires", "hits", "train_confidence",
                                        "holdout_confidence", "holdout_confidence_low_95",
                                        "holdout_confidence_high_95", "holdout_lift", "evidence_label"]]
                         .rename(columns={"fires": "Holdout appearances", "hits": "Together later",
                                          "train_confidence": "Training confidence",
                                          "holdout_confidence": "Later confidence",
                                          "holdout_confidence_low_95": "95% Wilson lower",
                                          "holdout_confidence_high_95": "95% Wilson upper",
                                          "holdout_lift": "Later lift", "evidence_label": "Evidence label"}),
                         hide_index=True, use_container_width=True)
            st.download_button("Export holdout evaluation (CSV)", stable.to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_holdout_evaluation.csv", mime="text/csv")
    st.markdown("<div class='note'>Holdout labels are descriptive, not significance tests."
                " Wilson intervals describe conditional proportions under simplified independence assumptions;"
                " repeat customers, multiple rules and seasonal effects can make them optimistic."
                " Lift is not the causal effect of recommending a product.</div>",
                unsafe_allow_html=True)

with builder:
    st.subheader("Build a basket")
    st.write("Choose one or more products. BasketLens finds rules whose antecedents are present in your selection.")
    all_skus = sorted(set(products["stock_code"].astype(str)) &
                      (set("||".join(d["rules"]["antecedent"].astype(str)).split("||"))
                       if not d["rules"].empty else set()))
    selected_skus = st.multiselect("Products currently in the basket", options=all_skus,
                                   format_func=display_product,
                                   placeholder="Search for a product by name or stock code")
    if not selected_skus:
        st.info("Select a product to explore related purchases.")
    elif d["rules"].empty:
        st.warning("This build has no association rules available.")
    else:
        matching = recommend_with_holdout(d["rules"], d["evaluation"],
                                         selected_skus, limit=12, min_fires=20)
        if matching.empty:
            st.info("No matching associations under the training thresholds. This is not a statement that the products never sell together.")
        else:
            st.markdown(f"**{len(matching)} suggestions based on observed co-occurrence**")
            matching["Product"] = matching["consequent"].map(display_product)
            matching["Triggered by"] = matching["antecedent"].map(display_product)
            st.dataframe(matching[["Product", "Triggered by", "confidence", "lift", "joint_count",
                                   "fires", "holdout_confidence", "evidence_label"]]
                         .rename(columns={"confidence": "Training confidence", "lift": "Training lift",
                                          "joint_count": "Training baskets together",
                                          "fires": "Later rule appearances",
                                          "holdout_confidence": "Later confidence",
                                          "evidence_label": "Evidence"}),
                         use_container_width=True, hide_index=True)
            st.download_button("Export these candidates (CSV)", matching.to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_cart_candidates.csv", mime="text/csv")
            st.caption("Candidates with repeated later co-occurrence appear first. Sparse candidates remain"
                       " visible for review. This is not personalized prediction, an A/B test, or proof of sales uplift.")

with quality:
    st.subheader("Trust the data before the rules")
    a,b,c = st.columns(3)
    a.metric("Raw line items", f"{q['input_rows']:,}")
    b.metric("Analysed sale lines", f"{q.get('analysis_eligible_rows', q['valid_rows']):,}")
    c.metric("Excluded lines", f"{q['excluded_rows']:,}")
    reasons = pd.DataFrame([{"Quality outcome":key.replace("_", " ").title(), "Rows":value}
                            for key,value in q["reason_counts"].items()])
    st.dataframe(reasons, use_container_width=True, hide_index=True)
    source_conflicts = q.get("source_invoice_conflicts", {})
    st.caption(f"Missing customer-ID rows: {q['missing_customer_id_rows']:,}. "
               f"Possible exact duplicate lines retained: {q['potential_exact_duplicate_rows']:,}. "
               f"Lines quarantined due to invoice conflicts: {source_conflicts.get('quarantined_rows', 0):,}.")
    st.markdown("**Methodological boundaries**")
    st.markdown("""
    - Sales use strictly positive quantity and price and exclude explicit cancellations and non-merchandise service codes.
    - Return lines are excluded from positive sale baskets. This is gross eligible sales value, not reconciled net revenue.
    - Single-product baskets remain in support denominators; counting only multi-product baskets would bias support.
    - Model candidates are selected using training-basket frequency, not future information.
    - Conflicting invoice timestamps/countries cause a failed build, unless quarantine is explicitly requested; all affected invoice lines are then excluded and reported.
    - Train/test ordering is chronological by invoice timestamp. Holdout confidence only measures later co-occurrence.
    - Association does not establish incremental conversion, profit, causality, or individualized recommendations.
    """)
    st.download_button("Download build manifest (JSON)", json.dumps(m, indent=2).encode("utf-8"),
                       file_name="basketlens_manifest.json", mime="application/json")
    st.download_button("Download quality report (JSON)", json.dumps(q, indent=2).encode("utf-8"),
                       file_name="basketlens_quality.json", mime="application/json")
    st.caption("Credit: Daqing Chen, Online Retail II, UCI Machine Learning Repository, CC BY 4.0.")
