import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive profit, margin, and date-part columns from the clean master."""
    df = df.copy()
    df["total_cost"]        = df["quantity"] * df["cost"]
    df["profit"]            = df["revenue"] - df["total_cost"]
    df["profit_margin_pct"] = (df["profit"] / df["revenue"]) * 100
    df["order_month_name"]  = df["order_date"].dt.month_name()
    df["order_month_num"]   = df["order_date"].dt.month
    df["order_month"]       = df["order_date"].dt.to_period("M")
    return df
