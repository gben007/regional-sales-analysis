import pandas as pd


def build_master(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge all sheets into one analysis-ready DataFrame."""
    df_sales     = sheets["sales"]
    df_customers = sheets["customers"]
    df_products  = sheets["products"]
    df_regions   = sheets["regions"]
    df_budgets   = sheets["budgets"]

    # State regions sheet has its real column names in row 0
    df_state_reg = sheets["state_regions"].copy()
    df_state_reg.columns = df_state_reg.iloc[0]
    df_state_reg = df_state_reg[1:].reset_index(drop=True)

    df = (
        df_sales
        .merge(df_customers, how="left",
               left_on="Customer Name Index", right_on="Customer Index")
        .merge(df_products, how="left",
               left_on="Product Description Index", right_on="Index")
        .merge(df_regions, how="left",
               left_on="Delivery Region Index", right_on="id")
        .merge(df_state_reg[["State Code", "Region"]], how="left",
               left_on="state_code", right_on="State Code")
        .merge(df_budgets, how="left", on="Product Name")
    )

    df = df.drop(columns=["Customer Index", "Index", "id", "State Code"],
                 errors="ignore")

    df.columns = df.columns.str.lower()

    df = df[[
        "ordernumber", "orderdate", "customer names", "channel",
        "product name", "order quantity", "unit price", "line total",
        "total unit cost", "state_code", "state", "region",
        "latitude", "longitude", "2017 budgets",
    ]].rename(columns={
        "ordernumber":    "order_number",
        "orderdate":      "order_date",
        "customer names": "customer_name",
        "product name":   "product_name",
        "order quantity": "quantity",
        "unit price":     "unit_price",
        "line total":     "revenue",
        "total unit cost":"cost",
        "state_code":     "state",
        "state":          "state_name",
        "region":         "us_region",
        "latitude":       "lat",
        "longitude":      "lon",
        "2017 budgets":   "budget",
    })

    # Budget only applies to 2017 orders
    df.loc[df["order_date"].dt.year != 2017, "budget"] = pd.NA

    return df
