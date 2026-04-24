"""Tests for src.features.engineer — derived column correctness."""
import pandas as pd
import numpy as np

NEW_COLUMNS = [
    "total_cost", "profit", "profit_margin_pct",
    "order_month_name", "order_month_num", "order_month",
]

VALID_MONTH_NAMES = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
}


class TestAddFeatures:
    def test_new_columns_added(self, featured_df):
        for col in NEW_COLUMNS:
            assert col in featured_df.columns, f"Missing column: '{col}'"

    def test_total_cost_formula(self, featured_df):
        expected = featured_df["quantity"] * featured_df["cost"]
        pd.testing.assert_series_equal(
            featured_df["total_cost"], expected,
            check_names=False, rtol=1e-5,
        )

    def test_profit_formula(self, featured_df):
        expected = featured_df["revenue"] - featured_df["total_cost"]
        pd.testing.assert_series_equal(
            featured_df["profit"], expected,
            check_names=False, rtol=1e-5,
        )

    def test_profit_margin_formula(self, featured_df):
        expected = (featured_df["profit"] / featured_df["revenue"]) * 100
        pd.testing.assert_series_equal(
            featured_df["profit_margin_pct"], expected,
            check_names=False, rtol=1e-5,
        )

    def test_profit_margin_range(self, featured_df):
        assert (featured_df["profit_margin_pct"] >= 0).all(), "Negative margin found"
        assert (featured_df["profit_margin_pct"] <= 100).all(), "Margin above 100% found"

    def test_order_month_num_range(self, featured_df):
        assert featured_df["order_month_num"].between(1, 12).all()

    def test_order_month_name_valid(self, featured_df):
        found = set(featured_df["order_month_name"].unique())
        assert found.issubset(VALID_MONTH_NAMES), f"Unexpected month names: {found - VALID_MONTH_NAMES}"

    def test_order_month_is_period(self, featured_df):
        assert hasattr(featured_df["order_month"].dtype, "freq"), (
            "order_month should be a PeriodDtype column"
        )

    def test_does_not_mutate_input(self, clean_df):
        """add_features must return a copy — the input df must be unchanged."""
        from src.features.engineer import add_features
        original_cols = set(clean_df.columns)
        add_features(clean_df)
        assert set(clean_df.columns) == original_cols, "add_features mutated the input DataFrame"

    def test_row_count_unchanged(self, clean_df, featured_df):
        assert len(featured_df) == len(clean_df)
