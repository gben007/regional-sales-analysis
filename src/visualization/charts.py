import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import pandas as pd

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 4)

_M_FMT = mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M")


def plot_monthly_trend(df: pd.DataFrame) -> None:
    monthly = df.groupby("order_month")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(15, 4))
    monthly.plot(ax=ax, marker="o", color="navy")
    ax.yaxis.set_major_formatter(_M_FMT)
    ax.set(title="Monthly Sales Trend", xlabel="Month", ylabel="Total Revenue (Millions)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_monthly_seasonality(df: pd.DataFrame) -> None:
    df_ = df[df["order_date"].dt.year != 2018]
    monthly = (
        df_.groupby(["order_month_num", "order_month_name"])["revenue"]
        .sum()
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(monthly.index.get_level_values(1), monthly.values, marker="o", color="navy")
    ax.yaxis.set_major_formatter(_M_FMT)
    ax.set(title="Overall Monthly Sales Trend (Excl. 2018)",
           xlabel="Month", ylabel="Total Revenue (Millions)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_top_products_revenue(df: pd.DataFrame, n: int = 10) -> None:
    top = df.groupby("product_name")["revenue"].sum().nlargest(n) / 1e6
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(x=top.values, y=top.index, palette="viridis", ax=ax)
    ax.set(title=f"Top {n} Products by Revenue (Millions)",
           xlabel="Total Revenue (Millions)", ylabel="Product")
    plt.tight_layout()
    plt.show()


def plot_top_products_margin(df: pd.DataFrame, n: int = 10) -> None:
    top = (
        df.groupby("product_name")["profit"]
        .mean()
        .sort_values(ascending=False)
        .head(n)
    )
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(x=top.values, y=top.index, palette="viridis", ax=ax)
    ax.set(title=f"Top {n} Products by Avg Profit",
           xlabel="Average Profit (USD)", ylabel="Product")
    plt.tight_layout()
    plt.show()


def plot_channel_mix(df: pd.DataFrame) -> None:
    chan = df.groupby("channel")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(chan.values, labels=chan.index, autopct="%1.1f%%",
           startangle=140, colors=sns.color_palette("coolwarm"))
    ax.set_title("Total Sales by Channel")
    plt.tight_layout()
    plt.show()


def plot_aov_distribution(df: pd.DataFrame) -> None:
    aov = df.groupby("order_number")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.hist(aov, bins=50, color="skyblue", edgecolor="black")
    ax.set(title="Distribution of Average Order Value",
           xlabel="Order Value (USD)", ylabel="Number of Orders")
    plt.tight_layout()
    plt.show()


def plot_margin_vs_price(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(df["unit_price"], df["profit_margin_pct"], alpha=0.6, color="green")
    ax.set(title="Profit Margin % vs. Unit Price",
           xlabel="Unit Price (USD)", ylabel="Profit Margin (%)")
    plt.tight_layout()
    plt.show()


def plot_price_boxplot(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.boxplot(data=df, x="product_name", y="unit_price", color="g", ax=ax)
    ax.set(title="Unit Price Distribution per Product",
           xlabel="Product", ylabel="Unit Price (USD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_region_sales(df: pd.DataFrame) -> None:
    region = df.groupby("us_region")["revenue"].sum().sort_values(ascending=False) / 1e6
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=region.values, y=region.index, palette="Greens_r", ax=ax)
    ax.set(title="Total Sales by US Region",
           xlabel="Total Sales (Millions USD)", ylabel="US Region")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()


def plot_state_choropleth(df: pd.DataFrame) -> None:
    state_sales = (
        df.groupby("state")["revenue"].sum().reset_index()
    )
    state_sales["revenue_m"] = state_sales["revenue"] / 1e6
    fig = px.choropleth(
        state_sales,
        locations="state",
        locationmode="USA-states",
        color="revenue_m",
        scope="usa",
        labels={"revenue_m": "Total Sales (M USD)"},
        color_continuous_scale="Blues",
        hover_data={"revenue_m": ":.2f"},
        title="Total Sales by State",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0),
                      coloraxis_colorbar=dict(title="Sales (M USD)", ticksuffix="M"))
    fig.show()


def plot_state_revenue_orders(df: pd.DataFrame, n: int = 10) -> None:
    state_rev = (
        df.groupby("state_name")
        .agg(revenue=("revenue", "sum"), orders=("order_number", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(n)
    )
    for col, title, label in [
        ("revenue", f"Top {n} States by Revenue", "Total Revenue (Million USD)"),
        ("orders",  f"Top {n} States by Order Count", "Order Count"),
    ]:
        fig, ax = plt.subplots(figsize=(15, 4))
        vals = state_rev[col] / 1e6 if col == "revenue" else state_rev[col]
        sns.barplot(x=state_rev.index, y=vals, palette="coolwarm", ax=ax)
        ax.set(title=title, xlabel="State", ylabel=label)
        plt.tight_layout()
        plt.show()


def plot_channel_margin(df: pd.DataFrame) -> None:
    cm = df.groupby("channel")["profit_margin_pct"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=cm.index, y=cm.values, palette="coolwarm", ax=ax)
    for i, v in enumerate(cm.values):
        ax.text(i, v + 0.5, f"{v:.2f}%", ha="center", fontweight="bold")
    ax.set(title="Average Profit Margin by Channel",
           xlabel="Sales Channel", ylabel="Avg Profit Margin (%)")
    plt.tight_layout()
    plt.show()


def plot_top_bottom_customers(df: pd.DataFrame, n: int = 10) -> None:
    rev = df.groupby("customer_name")["revenue"].sum()
    top    = rev.nlargest(n)
    bottom = rev.nsmallest(n)
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    sns.barplot(x=top.values / 1e6,    y=top.index,    palette="Blues_r", ax=axes[0])
    sns.barplot(x=bottom.values / 1e6, y=bottom.index, palette="Reds",    ax=axes[1])
    axes[0].set(title=f"Top {n} Customers by Revenue",    xlabel="Revenue (M USD)", ylabel="Customer")
    axes[1].set(title=f"Bottom {n} Customers by Revenue", xlabel="Revenue (M USD)", ylabel="Customer")
    plt.tight_layout()
    plt.show()


def plot_customer_segmentation(df: pd.DataFrame) -> None:
    cs = df.groupby("customer_name").agg(
        total_revenue_m=("revenue",          lambda x: x.sum() / 1e6),
        avg_margin=     ("profit_margin_pct", "mean"),
        orders=         ("order_number",      "nunique"),
    )
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=cs, x="total_revenue_m", y="avg_margin",
                    size="orders", sizes=(20, 200), alpha=0.7, ax=ax)
    ax.set(title="Customer Segmentation: Revenue vs. Profit Margin",
           xlabel="Total Revenue (Million USD)", ylabel="Avg Profit Margin (%)")
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    num_cols = ["quantity", "unit_price", "revenue", "cost", "profit"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="viridis", ax=ax)
    ax.set_title("Correlation Matrix")
    plt.tight_layout()
    plt.show()
