"""BasketLens retail research workbench with accessible, explained findings.

All displayed findings are historical observations, not causal sales uplift.
"""
from __future__ import annotations

from html import escape
import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from basketlens.insights import annotate_evidence, recommend_with_holdout
from basketlens.network import affinity_edges, network_figure
from basketlens.presentation import (
    compact_rule_table, example_basket_seed, filter_rule_view, lift_meaning, product_name,
    quality_reason_label, snapshot_from_rollup,
)
from basketlens.public_demo import PUBLIC_FILENAME, load_public_demo

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = Path(os.environ.get("BASKETLENS_DATA_DIR", "data/processed"))
PUBLIC_PATH = ROOT / "data" / "public_demo" / PUBLIC_FILENAME
FOREST = "#426a57"
CLAY = "#ad714d"
PAPER = "#f7f6f2"
MUTED = "#56685c"

st.set_page_config(page_title="BasketLens | Retail research", page_icon="🧺",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>" + (ROOT / "app" / "assets" / "basketlens.css").read_text(encoding="utf-8") +
            "</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_full_data(base: str, manifest_mtime: float) -> dict:
    """Analyst mode for full local processed artifacts."""
    path = Path(base)
    result = {
        "manifest": json.loads((path / "manifest.json").read_text(encoding="utf-8")),
        "quality": json.loads((path / "quality.json").read_text(encoding="utf-8")),
    }
    for name in ("products", "countries", "monthly", "monthly_country", "rules", "evaluation"):
        types = ({"stock_code": str} if name == "products" else
                 {"antecedent": str, "consequent": str} if name in {"rules", "evaluation"} else None)
        result[name] = pd.read_csv(path / f"{name}.csv", dtype=types)
    baskets = pd.read_csv(path / "basket_summary.csv.gz", usecols=[
        "country", "item_count", "basket_revenue_gbp"], dtype={"country": str})
    result["basket_rollup"] = baskets.groupby(
        ["country", "item_count"], dropna=False, as_index=False
    ).agg(basket_count=("basket_revenue_gbp", "size"),
          sales_gbp=("basket_revenue_gbp", "sum"))
    return result


@st.cache_data(show_spinner=False)
def load_published(path: str, asset_mtime: float) -> dict:
    """Public mode using only the checksum-verified aggregate exhibit."""
    return load_public_demo(Path(path))


def reading_note(title: str, explanation: str, *, clay: bool = False) -> None:
    kind = " bl-reading-note--clay" if clay else ""
    st.markdown(f'<div class="bl-reading-note{kind}"><strong>{escape(title)}</strong> '
                f'{escape(explanation)}</div>', unsafe_allow_html=True)


def chart_layout(fig: go.Figure, *, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=4, r=8, t=12, b=14),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=12, color="#34483d"),
        showlegend=False, hoverlabel=dict(bgcolor="#20372f", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor="#e7e9e2", zeroline=False,
                     tickfont=dict(color=MUTED))
    return fig


def rule_badge(rule: pd.Series, names: dict[str, str]) -> None:
    antecedent = product_name(str(rule["antecedent"]), names, limit=42)
    consequent = product_name(str(rule["consequent"]), names, limit=42)
    description = lift_meaning(float(rule["lift"]))
    st.markdown(
        '<section class="bl-rule-spotlight">'
        '<div class="bl-eyebrow">A pairing worth examining</div>'
        f'<div class="bl-rule-name">{escape(antecedent)} + {escape(consequent)}</div>'
        '<p class="bl-rule-description">'
        f'Found together in {int(rule["joint_count"]):,} earlier baskets. '
        f'{escape(description)} This is a historical pattern, not a proven sales opportunity.'
        '</p></section>', unsafe_allow_html=True,
    )


if not (BASE_DIR / "manifest.json").exists() and not PUBLIC_PATH.is_file():
    st.title("BasketLens")
    st.subheader("Historical retail research, explained clearly")
    st.info("The research exhibit has not been prepared on this installation yet.")
    st.write("Generate the official UCI analytics files, or add the verified public exhibit to the repository.")
    st.code("python -m basketlens.cli download\n"
            "python -m basketlens.cli build --algorithm fpgrowth\n"
            "streamlit run app/streamlit_app.py", language="bash")
    st.caption("Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii).")
    st.stop()

try:
    with st.spinner("Opening historical research..."):
        if (BASE_DIR / "manifest.json").exists():
            d = load_full_data(str(BASE_DIR.resolve()), (BASE_DIR / "manifest.json").stat().st_mtime)
        else:
            d = load_published(str(PUBLIC_PATH), PUBLIC_PATH.stat().st_mtime)
except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as error:
    st.error("The analytics exhibit could not be opened.")
    st.caption(f"Diagnostic: {error}")
    st.stop()

manifest, quality = d["manifest"], d["quality"]
products = d["products"]
names = dict(zip(products["stock_code"].astype(str),
                 products["description"].fillna("Unknown product").astype(str)))
published = d.get("publication")
period_start = pd.to_datetime(manifest["data_first_invoice"]).strftime("%b %Y")
period_end = pd.to_datetime(manifest["data_last_invoice"]).strftime("%b %Y")

with st.sidebar:
    st.markdown("### Reading guide")
    st.caption("BasketLens uses historical retail receipts. Nothing here describes live shopping activity.")
    show_notes = st.checkbox("Show plain-language explanations", value=True, key="plain_notes")
    st.divider()
    st.markdown("**Study sample**")
    st.write(f"{int(manifest['basket_count_all']):,} valid baskets")
    st.write(f"{int(manifest['train_baskets']):,} earlier baskets for rule discovery")
    st.write(f"{int(manifest['holdout_baskets']):,} later baskets for checking patterns")
    st.caption("A basket means a single eligible invoice. The holdout is later in time, not a controlled trial.")
    if published:
        st.caption(f"Public selection: {int(published['visible_rule_count']):,} rules shown "
                   f"from {int(published['full_rule_count']):,} candidates.")
    if manifest.get("partial_data"):
        st.warning("Partial input analysis. Interpret findings as a test only.")
    st.divider()
    st.markdown("**Reading the metrics**")
    st.caption("Confidence: how often B appears when A is in an earlier basket.")
    st.caption("Lift: how much more often products appear together than their baseline frequencies suggest.")
    st.caption("Later evidence: whether similar co-occurrence also appeared in held-out transactions.")
    st.caption("[UCI dataset and license](https://archive.ics.uci.edu/dataset/502/online+retail+ii)")

public_line = (f"Curated view: {int(published['visible_rule_count']):,} of "
               f"{int(published['full_rule_count']):,} rule candidates" if published else
               "Full local research workspace")
st.markdown(
    '<section class="bl-hero"><div class="bl-hero-grid"><div>'
    '<div class="bl-eyebrow">Retail research / Historical transactions</div>'
    '<h1>BasketLens</h1>'
    '<p class="bl-hero-lede">What do people tend to buy together?</p>'
    '<p class="bl-hero-note">Start with the shopping picture, examine product pairings, '
    'then test a sample basket. Every insight is based on recorded purchases, '
    'not a sales experiment.</p></div>'
    '<div class="bl-hero-side">'
    '<span>DATA COVERAGE</span>'
    f'<strong>{escape(period_start)} to {escape(period_end)}</strong>'
    f'<span>{escape(public_line)}</span>'
    '<span style="margin-top:.7rem">Daqing Chen / UCI Online Retail II</span>'
    '</div></div></section>', unsafe_allow_html=True,
)
st.markdown(
    '<div class="bl-flow">'
    '<span>01 &nbsp; Understand sales</span>'
    '<span>02 &nbsp; Find pairings</span>'
    '<span>03 &nbsp; Try a basket</span>'
    '<span>04 &nbsp; Review the evidence</span>'
    '</div>', unsafe_allow_html=True,
)

# Preserve the explicit tab labels used by automated desktop/mobile smoke tests.
overview, explorer, builder, quality_tab = st.tabs([
    "Sales overview", "Association explorer", "Build a basket", "Data quality & methodology",
])

with overview:
    st.markdown('<p class="bl-section-kicker">01 / The business picture</p>', unsafe_allow_html=True)
    st.subheader("Start with what the baskets tell us")
    st.caption("All figures below are based on positive, eligible historical sales. They are not net revenue or profit.")
    options = ["All countries"] + d["countries"]["country"].dropna().astype(str).tolist()
    selected_country = st.selectbox("Show sales for", options, key="country_scope",
                                    help="This changes sales summaries only. Association rules are global.")
    if selected_country == "All countries":
        monthly = d["monthly"]
        rollup = d["basket_rollup"]
    else:
        monthly = d["monthly_country"].loc[
            d["monthly_country"]["country"].astype(str).eq(selected_country)]
        rollup = d["basket_rollup"].loc[
            d["basket_rollup"]["country"].astype(str).eq(selected_country)]
    snapshot = snapshot_from_rollup(rollup)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Eligible sales value", f"£{snapshot.sales_gbp:,.0f}",
                help="Positive eligible sale-line value, not adjusted for returned goods or profit.")
    col2.metric("Baskets analysed", f"{snapshot.baskets:,}")
    col3.metric("Average per basket", f"£{snapshot.average_gbp:,.2f}"
                if snapshot.average_gbp is not None else "N/A")
    col4.metric("Baskets with 2+ products", f"{snapshot.multi_product_share:.1%}"
                if snapshot.multi_product_share is not None else "N/A",
                help="Share of eligible invoices with at least two distinct product codes.")
    if show_notes:
        scope = "this historical dataset" if selected_country == "All countries" else selected_country
        if snapshot.baskets:
            reading_note("What this means.",
                         f"In {scope}, a recorded basket was worth £{snapshot.average_gbp:,.2f} "
                         f"on average. {snapshot.multi_product_share:.1%} of baskets contained at least two "
                         "different products. This describes historical buying, not sales generated by recommendations.")
        else:
            reading_note("No eligible baskets.", "Select another country to inspect recorded activity.")
    st.markdown("#### How did eligible sales change over time?")
    if monthly.empty:
        st.info("No monthly sales were recorded for this selection.")
    else:
        plot = monthly.sort_values("month").copy()
        trend = px.line(plot, x="month", y="sales_gbp", markers=True,
                        labels={"month": "Invoice month", "sales_gbp": "Eligible sales (£)"})
        trend.update_traces(line=dict(color=FOREST, width=3), marker=dict(size=7, color=CLAY),
                            hovertemplate="%{x}<br>£%{y:,.0f}<extra></extra>")
        chart_layout(trend, height=330)
        trend.update_xaxes(title=None, type="category", showgrid=False)
        trend.update_yaxes(title="Sales value (£)", tickprefix="£", tickformat=",.0f")
        st.plotly_chart(trend, use_container_width=True, config={"displayModeBar": False})
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown("#### Which products had the highest sales value?")
        st.caption("This product ranking always covers the entire dataset, even when a country is selected.")
        best = products.nlargest(10, "sales_gbp").copy()
        best["product"] = best["description"].astype(str).str.slice(0, 30)
        if best.empty:
            st.info("No product aggregates available for ranking.")
        else:
            top_chart = px.bar(best.sort_values("sales_gbp"), x="sales_gbp", y="product",
                               orientation="h", labels={"sales_gbp": "Sales value (£)", "product": ""})
            top_chart.update_traces(marker_color=FOREST,
                                    hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>")
            chart_layout(top_chart, height=375)
            top_chart.update_yaxes(showgrid=False)
            top_chart.update_xaxes(tickprefix="£", tickformat=",.0f")
            st.plotly_chart(top_chart, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.markdown("#### How many products are in each basket?")
        st.caption("Each basket counts distinct stock codes. The last group includes 10 or more.")
        counts = (rollup.assign(size=rollup["item_count"].clip(upper=10))
                  .groupby("size", as_index=False)["basket_count"].sum())
        if counts.empty:
            st.info("No basket composition is available for this selection.")
        else:
            composition = px.bar(counts, x="size", y="basket_count",
                                 labels={"size": "Distinct products (10 includes 10+)",
                                         "basket_count": "Baskets"})
            composition.update_traces(marker_color=CLAY,
                                      hovertemplate="%{x} different products<br>%{y:,} baskets<extra></extra>")
            chart_layout(composition, height=375)
            composition.update_xaxes(dtick=1)
            st.plotly_chart(composition, use_container_width=True, config={"displayModeBar": False})
    st.caption("Next: open Association explorer to see which products repeatedly appeared together.")

with explorer:
    st.markdown('<p class="bl-section-kicker">02 / Product relationships</p>', unsafe_allow_html=True)
    st.subheader("Which products appeared together?")
    st.caption("The relationships were discovered using earlier baskets. Changing a filter only changes the view.")
    if show_notes:
        reading_note("A useful way to read a rule.",
                     "If a basket contains product A, confidence is the percentage of those earlier "
                     "baskets that also contained B. Lift compares this against B's overall popularity. "
                     "Lift above 1 means the pair occurred more often than a simple independence baseline.")
    if published:
        st.caption(f"Public exhibit: {int(published['visible_rule_count']):,} training-selected rules "
                   f"shown from {int(published['full_rule_count']):,} candidate rules. "
                   "Later outcomes did not determine which rules were published.")
    rules = d["rules"].copy()
    if rules.empty:
        st.warning("No association rules are available with the current build thresholds.")
        filtered = rules
    else:
        a, b, c = st.columns([1.1, 1, 1], gap="medium")
        with a:
            search = st.text_input("Search by product or SKU", placeholder="e.g. heart, mug, 85123A",
                                   help="Searches both sides of a product rule.")
        with b:
            max_lift = max(2.0, min(12.0, float(rules["lift"].max())))
            default_lift = min(1.2, max_lift)
            min_lift = st.slider("Minimum lift", min_value=0.0, max_value=max_lift,
                                 value=default_lift, step=0.1,
                                 help="Lift 1.0 is the training-basket independence baseline.")
        with c:
            max_joint = max(1, int(rules["joint_count"].max()))
            min_joint = st.number_input("At least this many baskets together", min_value=1,
                                        max_value=max_joint, value=min(20, max_joint),
                                        help="Larger counts generally offer more descriptive context.")
        filtered = filter_rule_view(rules, names, minimum_lift=min_lift,
                                    minimum_joint=int(min_joint), search=search)
        st.caption(f"{len(filtered):,} of {len(rules):,} available rules match your filters. "
                   "The strongest-looking lift alone does not establish a useful business action.")
        if filtered.empty:
            st.info("No rules match your search and thresholds. Try a shorter product name or lower the filters.")
        else:
            singles = filtered.loc[(filtered["antecedent_size"] == 1) &
                                   (filtered["consequent_size"] == 1)]
            rule_badge(singles.iloc[0] if not singles.empty else filtered.iloc[0], names)
            st.markdown("#### Compare the strongest displayed pairings")
            top = compact_rule_table(filtered.head(80))
            st.dataframe(top, hide_index=True, use_container_width=True, height=330,
                         column_config={
                             "Purchased together": st.column_config.NumberColumn(format="%d"),
                             "Confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
                             "Lift (x)": st.column_config.NumberColumn(format="%.2fx"),
                         })
            st.caption(f"Showing up to 80 of {len(filtered):,} matching rules, ordered by training co-purchases. "
                       "Download contains all filtered rules.")
            st.download_button("Download these rules (CSV)",
                               data=filtered[["antecedent", "consequent", "joint_count", "support",
                                              "confidence", "lift"]].to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_pairings.csv", mime="text/csv")
        with st.expander("Product affinity map", expanded=True):
            st.caption("Lines connect two products seen in the same earlier basket. "
                       "This is an exploratory network, not a geographic map or a predictor.")
            edge_limit = st.slider("Connections shown", 5, 40, 24,
                                   help="Reduce the number for a cleaner, easier-to-read network.")
            edges = affinity_edges(filtered, max_edges=edge_limit, max_nodes=22, min_joint=1)
            if edges.empty:
                st.info("No two-product connections satisfy the current filters.")
            else:
                fig = network_figure(edges, names)
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                st.caption(f"Showing {len(edges)} unique pairs. Position and distance do not represent a metric.")
    st.markdown("#### Did these pairings appear in later orders?")
    st.caption("A later time window checks whether the co-occurrence was repeated. It is not an A/B test.")
    evaluation = d["evaluation"]
    if evaluation.empty:
        st.info("No later-period evaluation is available for these rules.")
    else:
        minimum_fires = st.number_input("Minimum times the starting product appeared later",
                                        min_value=1, value=20, step=1,
                                        help="A descriptive sample-size threshold, not statistical significance.")
        later = annotate_evidence(evaluation, min_fires=int(minimum_fires))
        if not rules.empty and not filtered.empty:
            keys = filtered[["antecedent", "consequent", "antecedent_label", "consequent_label"]]
            later = keys.merge(later, on=["antecedent", "consequent"], how="inner",
                               validate="one_to_one")
        stable = later.loc[later["fires"].ge(minimum_fires)].copy()
        if stable.empty:
            st.info("No displayed rule has enough later observations for the selected threshold.")
        else:
            if show_notes:
                repeated = int(stable["evidence_label"].eq("Repeated association").sum())
                reading_note("How to interpret this check.",
                             f"{repeated:,} of {len(stable):,} displayed rules with enough later observations "
                             "had lift above 1 in the holdout. That is descriptive repetition, not "
                             "a statistically significant effect or proven conversion improvement.", clay=True)
            stable["Starting product"] = stable["antecedent"].map(
                lambda s: product_name(s, names, limit=32))
            stable["Additional product"] = stable["consequent"].map(
                lambda s: product_name(s, names, limit=32))
            stable["Earlier confidence (%)"] = stable["train_confidence"] * 100
            stable["Later confidence (%)"] = stable["holdout_confidence"] * 100
            st.dataframe(stable[["Starting product", "Additional product", "fires", "hits",
                                 "Earlier confidence (%)", "Later confidence (%)", "holdout_lift",
                                 "evidence_label"]].head(80).rename(columns={
                                     "fires": "Starting product seen later", "hits": "Both seen later",
                                     "holdout_lift": "Later lift", "evidence_label": "Descriptive evidence"
                                 }), hide_index=True, use_container_width=True, height=300,
                         column_config={
                             "Earlier confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
                             "Later confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
                             "Later lift": st.column_config.NumberColumn(format="%.2fx"),
                         })
            st.download_button("Download later-period comparison (CSV)",
                               data=stable.to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_later_evidence.csv", mime="text/csv")
    if show_notes:
        st.caption("Technical note: Wilson intervals assume simplified binomial independence. "
                   "Repeat customers, seasonality and checking many rules can make uncertainty look smaller "
                   "than it really is. Confidence and lift are descriptive co-occurrence metrics.")

with builder:
    st.markdown('<p class="bl-section-kicker">03 / Interactive example</p>', unsafe_allow_html=True)
    st.subheader("Build a basket")
    st.write("Choose one or more products. BasketLens checks which other products appeared "
             "with those items in earlier orders.")
    st.caption("This simulates an analyst's investigation, not a personalized shopping prediction.")
    all_skus = sorted(set(products["stock_code"].astype(str)) &
                      (set("||".join(d["rules"]["antecedent"].astype(str)).split("||"))
                       if not d["rules"].empty else set()))
    if "basket_products" not in st.session_state:
        st.session_state["basket_products"] = []
    # The example uses a frequently observed training antecedent, never future outcomes.
    example_sku = example_basket_seed(d["rules"], all_skus)
    if example_sku and st.button("Fill an example basket", type="secondary",
                                 help="Picks a commonly observed starting product from the training period."):
        st.session_state["basket_products"] = [example_sku]
    selected = st.multiselect("Products currently in the basket", options=all_skus,
                              format_func=lambda code: product_name(code, names, limit=55),
                              placeholder="Search for an item by name or code",
                              key="basket_products")
    if not selected:
        st.info("Select a product, or use the example basket to see how this analysis works.")
    elif d["rules"].empty:
        st.warning("No association rules were generated for this research build.")
    else:
        matches = recommend_with_holdout(d["rules"], d["evaluation"],
                                         selected, limit=12, min_fires=20)
        if matches.empty:
            st.info("No published rule starts with this selection. It does not mean these products "
                    "have never sold together. Try a different product.")
        else:
            st.markdown(f"#### {len(matches)} related product candidates")
            lead = matches.iloc[0]
            rule_badge(lead, names)
            st.caption("Candidates with repeated later co-occurrence appear first. This later check "
                       "ranks suggestions for investigation; it is not a measure of recommendation uplift.")
            shown = matches.copy()
            shown["Product to investigate"] = shown["consequent"].map(lambda x: product_name(x, names))
            shown["Based on these items"] = shown["antecedent"].map(lambda x: product_name(x, names))
            shown["Earlier confidence (%)"] = shown["confidence"] * 100
            shown["Later confidence (%)"] = shown["holdout_confidence"] * 100
            st.dataframe(shown[["Product to investigate", "Based on these items",
                                "joint_count", "Earlier confidence (%)", "lift", "fires",
                                "Later confidence (%)", "evidence_label"]].rename(columns={
                                    "joint_count": "Earlier co-purchases", "lift": "Earlier lift",
                                    "fires": "Seen later", "evidence_label": "Evidence"
                                }), hide_index=True, use_container_width=True,
                         column_config={
                             "Earlier confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
                             "Later confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
                             "Earlier lift": st.column_config.NumberColumn(format="%.2fx"),
                         })
            st.download_button("Download this basket's candidates (CSV)",
                               data=matches.to_csv(index=False).encode("utf-8"),
                               file_name="basketlens_basket_candidates.csv", mime="text/csv")
    if show_notes:
        reading_note("What would a retailer do next?",
                     "Review whether the pairing makes merchandising sense, check margin and availability, "
                     "then measure any actual effect through a controlled experiment. "
                     "These historical rules alone cannot establish additional sales.", clay=True)

with quality_tab:
    st.markdown('<p class="bl-section-kicker">04 / Method and limitations</p>', unsafe_allow_html=True)
    st.subheader("What can we trust in this analysis?")
    st.write("A useful pairing begins with a trustworthy basket. The pipeline excludes invalid sales "
             "and records invoices that cannot be interpreted consistently.")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Source line items", f"{quality['input_rows']:,}")
    q2.metric("Eligible sale lines analysed",
              f"{quality.get('analysis_eligible_rows', quality['valid_rows']):,}")
    q3.metric("Excluded lines", f"{quality['excluded_rows']:,}",
              help="Invalid, canceled and non-merchandise records. Quarantined lines are separate.")
    quarantined = quality.get("source_invoice_conflicts", {}).get("quarantined_rows", 0)
    q4.metric("Additional quarantined lines", f"{quarantined:,}",
              help="Complete invoices were removed when source dates or countries conflicted.")
    st.markdown("#### Where did the data go?")
    st.markdown('<div class="bl-flow"><span>Invoice records</span><span>Eligibility checks</span>'
                '<span>One basket per invoice</span><span>Rules from earlier orders</span>'
                '<span>Check against later orders</span></div>', unsafe_allow_html=True)
    reason_rows = [
        {"Quality outcome": quality_reason_label(reason), "Source lines": int(count)}
        for reason, count in quality["reason_counts"].items()
    ]
    reasons = pd.DataFrame(reason_rows)
    st.dataframe(reasons, hide_index=True, use_container_width=True,
                 column_config={"Source lines": st.column_config.NumberColumn(format="%d")})
    if show_notes:
        reading_note("Important distinction.",
                     "Excluded lines come from invalid or non-sale records. Quarantined lines are "
                     "otherwise eligible rows from invoices with conflicting source metadata, "
                     "so they are reported separately instead of counting the same line twice.")
    with st.expander("Methodology, definitions and honest limitations", expanded=True):
        st.markdown("""
- **Positive eligible sales, not net revenue:** cancellations, nonpositive amounts and selected service codes are excluded. Historical returns and profit are not reconciled.
- **Basket:** one invoice within its source year, including baskets with a single product.
- **Train first, check later:** candidate products and association rules are selected from earlier transactions only.
- **Support:** share of earlier baskets containing all items in a rule.
- **Confidence:** among earlier baskets containing the starting product(s), the share also containing the additional product.
- **Lift:** how often items co-occur relative to an independence baseline. Lift above 1 is not a revenue multiplier.
- **Quarantine:** invoices with incompatible source dates or countries are removed as a whole. No timestamp is guessed.
- **Later evidence:** descriptive repetition in subsequent transactions, not statistical significance or proof of uplift.
- **Scope:** historical UK giftware transactions from 2009 to 2011. Patterns may not apply to today's shoppers.
        """)
    if published:
        st.info(f"This public dashboard displays {published['visible_rule_count']:,} "
                "training-selected rules, not the complete rule universe. "
                "The 40,280-basket analytics totals describe the full eligible historical dataset.")
    st.download_button("Download data quality summary (JSON)",
                       json.dumps(quality, indent=2).encode("utf-8"),
                       file_name="basketlens_quality.json", mime="application/json")
    st.download_button("Download analysis manifest (JSON)",
                       json.dumps(manifest, indent=2).encode("utf-8"),
                       file_name="basketlens_manifest.json", mime="application/json")

st.markdown(
    '<footer class="bl-footer">BasketLens is a historical, explanatory retail study. '
    'Data: <a href="https://archive.ics.uci.edu/dataset/502/online+retail+ii">'
    'UCI Online Retail II</a> by Daqing Chen, CC BY 4.0. '
    'Pairings are not causal conversion estimates or evidence of incremental profit.</footer>',
    unsafe_allow_html=True,
)