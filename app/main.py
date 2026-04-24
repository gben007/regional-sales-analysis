import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.data.clean import build_master
from src.data.load import load_sheets
from src.features.engineer import add_features

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Regional Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Data (cached — Excel loads once per session) ───────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    return add_features(build_master(load_sheets()))

df_all = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filters")

    years = sorted(df_all["order_date"].dt.year.unique())
    year_range = st.slider(
        "Year range", min_value=years[0], max_value=years[-1],
        value=(years[0], years[-1]),
    )

    sel_regions = st.multiselect(
        "US Region",
        options=sorted(df_all["us_region"].unique()),
        default=sorted(df_all["us_region"].unique()),
    )

    sel_channels = st.multiselect(
        "Channel",
        options=sorted(df_all["channel"].unique()),
        default=sorted(df_all["channel"].unique()),
    )

# ── Apply filters ──────────────────────────────────────────────────────────────
df = df_all[
    df_all["order_date"].dt.year.between(*year_range)
    & df_all["us_region"].isin(sel_regions)
    & df_all["channel"].isin(sel_channels)
]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📊 USA Regional Sales Dashboard")
st.caption(
    f"Acme Co. · {year_range[0]}–{year_range[1]} · "
    f"{len(df):,} orders · {len(sel_regions)} region(s) · {len(sel_channels)} channel(s)"
)

if df.empty:
    st.warning("No data matches the current filters — adjust the sidebar.")
    st.stop()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_overview, tab_products, tab_geo, tab_customers, tab_channels = st.tabs(
    ["Overview", "Products", "Geography", "Customers", "Channels"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Revenue",  f"${df['revenue'].sum() / 1e6:.1f} M")
    k2.metric("Total Profit",   f"${df['profit'].sum()  / 1e6:.1f} M")
    k3.metric("Avg Margin",     f"{df['profit_margin_pct'].mean():.1f} %")
    k4.metric("Unique Orders",  f"{df['order_number'].nunique():,}")

    st.divider()

    # Monthly revenue trend
    monthly = (
        df.groupby("order_month", sort=True)["revenue"]
        .sum()
        .reset_index()
    )
    monthly["order_month"] = monthly["order_month"].astype(str)

    fig = px.line(
        monthly, x="order_month", y="revenue",
        title="Monthly Revenue Trend",
        labels={"order_month": "Month", "revenue": "Revenue (USD)"},
        markers=True,
    )
    fig.update_traces(line_color="#003f8a", marker_color="#003f8a")
    fig.update_layout(yaxis_tickformat=".2s", xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Seasonality — exclude partial 2018 year
    df_full = df[df["order_date"].dt.year != 2018]
    seasonal = (
        df_full.groupby(["order_month_num", "order_month_name"])["revenue"]
        .sum()
        .sort_index()
        .reset_index()
    )
    fig2 = px.bar(
        seasonal, x="order_month_name", y="revenue",
        title="Revenue by Calendar Month (excl. partial 2018)",
        labels={"order_month_name": "Month", "revenue": "Total Revenue (USD)"},
        color_discrete_sequence=["#1a6faf"],
    )
    fig2.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_products:
    col_a, col_b = st.columns(2)

    with col_a:
        top_rev = (
            df.groupby("product_name")["revenue"].sum()
            .nlargest(10).reset_index()
            .sort_values("revenue")
        )
        fig = px.bar(
            top_rev, x="revenue", y="product_name", orientation="h",
            title="Top 10 Products by Revenue",
            labels={"revenue": "Revenue (USD)", "product_name": ""},
            color_discrete_sequence=["#2ecc71"],
        )
        fig.update_layout(xaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        top_profit = (
            df.groupby("product_name")["profit"].mean()
            .nlargest(10).reset_index()
            .sort_values("profit")
        )
        fig = px.bar(
            top_profit, x="profit", y="product_name", orientation="h",
            title="Top 10 Products by Avg Profit",
            labels={"profit": "Avg Profit (USD)", "product_name": ""},
            color_discrete_sequence=["#27ae60"],
        )
        fig.update_layout(xaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.box(
        df, x="product_name", y="unit_price",
        title="Unit Price Distribution per Product",
        labels={"product_name": "Product", "unit_price": "Unit Price (USD)"},
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GEOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════
with tab_geo:
    state_sales = (
        df.groupby("state")["revenue"].sum().reset_index()
    )
    state_sales["revenue_m"] = state_sales["revenue"] / 1e6

    fig = px.choropleth(
        state_sales,
        locations="state", locationmode="USA-states",
        color="revenue_m", scope="usa",
        color_continuous_scale="Blues",
        labels={"revenue_m": "Revenue (M USD)"},
        title="Total Sales by State",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        region_sales = (
            df.groupby("us_region")["revenue"].sum()
            .reset_index().sort_values("revenue", ascending=False)
        )
        fig = px.bar(
            region_sales, x="us_region", y="revenue",
            title="Revenue by US Region",
            labels={"us_region": "Region", "revenue": "Revenue (USD)"},
            color_discrete_sequence=["#1a6faf"],
        )
        fig.update_layout(yaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        top_states = (
            df.groupby("state_name")["revenue"].sum()
            .nlargest(10).reset_index().sort_values("revenue")
        )
        fig = px.bar(
            top_states, x="revenue", y="state_name", orientation="h",
            title="Top 10 States by Revenue",
            labels={"revenue": "Revenue (USD)", "state_name": ""},
            color_discrete_sequence=["#1a6faf"],
        )
        fig.update_layout(xaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════
with tab_customers:
    col_a, col_b = st.columns(2)
    rev_by_cust = df.groupby("customer_name")["revenue"].sum()

    with col_a:
        top_c = rev_by_cust.nlargest(10).reset_index().sort_values("revenue")
        fig = px.bar(
            top_c, x="revenue", y="customer_name", orientation="h",
            title="Top 10 Customers by Revenue",
            labels={"revenue": "Revenue (USD)", "customer_name": ""},
            color_discrete_sequence=["#2980b9"],
        )
        fig.update_layout(xaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        bot_c = rev_by_cust.nsmallest(10).reset_index().sort_values("revenue")
        fig = px.bar(
            bot_c, x="revenue", y="customer_name", orientation="h",
            title="Bottom 10 Customers by Revenue",
            labels={"revenue": "Revenue (USD)", "customer_name": ""},
            color_discrete_sequence=["#e74c3c"],
        )
        fig.update_layout(xaxis_tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    cs = (
        df.groupby("customer_name")
        .agg(
            total_revenue=("revenue", "sum"),
            avg_margin=("profit_margin_pct", "mean"),
            orders=("order_number", "nunique"),
        )
        .reset_index()
    )
    cs["total_revenue_m"] = cs["total_revenue"] / 1e6

    fig = px.scatter(
        cs, x="total_revenue_m", y="avg_margin", size="orders",
        hover_name="customer_name",
        title="Customer Segmentation: Revenue vs. Profit Margin",
        labels={
            "total_revenue_m": "Total Revenue (M USD)",
            "avg_margin": "Avg Margin (%)",
            "orders": "Orders",
        },
        color_discrete_sequence=["#2980b9"],
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CHANNELS
# ══════════════════════════════════════════════════════════════════════════════
with tab_channels:
    col_a, col_b = st.columns(2)

    with col_a:
        chan_rev = df.groupby("channel")["revenue"].sum().reset_index()
        fig = px.pie(
            chan_rev, values="revenue", names="channel",
            title="Sales Mix by Channel",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        chan_margin = (
            df.groupby("channel")["profit_margin_pct"].mean()
            .reset_index().sort_values("profit_margin_pct", ascending=False)
        )
        fig = px.bar(
            chan_margin, x="channel", y="profit_margin_pct",
            title="Avg Profit Margin by Channel",
            labels={"channel": "Channel", "profit_margin_pct": "Avg Margin (%)"},
            text_auto=".2f",
            color_discrete_sequence=["#8e44ad"],
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    aov = df.groupby("order_number")["revenue"].sum().reset_index()
    fig = px.histogram(
        aov, x="revenue", nbins=50,
        title="Order Value Distribution (AOV)",
        labels={"revenue": "Order Value (USD)", "count": "Orders"},
        color_discrete_sequence=["#3498db"],
    )
    st.plotly_chart(fig, use_container_width=True)

    sample = df.sample(min(5000, len(df)), random_state=42)
    fig = px.scatter(
        sample, x="unit_price", y="profit_margin_pct", opacity=0.5,
        title="Profit Margin % vs. Unit Price (5k sample)",
        labels={"unit_price": "Unit Price (USD)", "profit_margin_pct": "Margin (%)"},
        color_discrete_sequence=["#27ae60"],
    )
    st.plotly_chart(fig, use_container_width=True)
