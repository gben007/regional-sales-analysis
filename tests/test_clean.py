"""Tests for src.data.clean — merge, rename, and budget pipeline."""
import pytest

EXPECTED_COLUMNS = [
    "order_number", "order_date", "customer_name", "channel",
    "product_name", "quantity", "unit_price", "revenue", "cost",
    "state", "state_name", "us_region", "lat", "lon", "budget",
]

NON_NULL_COLUMNS = [
    "order_number", "order_date", "customer_name", "channel",
    "product_name", "quantity", "unit_price", "revenue", "cost",
    "state", "state_name", "us_region", "lat", "lon",
]

VALID_CHANNELS   = {"Wholesale", "Distributor", "Export"}
VALID_US_REGIONS = {"South", "West", "Midwest", "Northeast"}


class TestBuildMaster:
    def test_row_count(self, clean_df):
        assert len(clean_df) == 64104

    def test_column_names(self, clean_df):
        assert list(clean_df.columns) == EXPECTED_COLUMNS

    @pytest.mark.parametrize("col", NON_NULL_COLUMNS)
    def test_no_nulls_in_key_columns(self, clean_df, col):
        null_count = clean_df[col].isna().sum()
        assert null_count == 0, f"Column '{col}' has {null_count} nulls"

    def test_revenue_always_positive(self, clean_df):
        assert (clean_df["revenue"] > 0).all()

    def test_quantity_always_positive(self, clean_df):
        assert (clean_df["quantity"] > 0).all()

    def test_valid_channels(self, clean_df):
        found = set(clean_df["channel"].unique())
        assert found.issubset(VALID_CHANNELS), f"Unexpected channels: {found - VALID_CHANNELS}"

    def test_valid_us_regions(self, clean_df):
        found = set(clean_df["us_region"].unique())
        assert found.issubset(VALID_US_REGIONS), f"Unexpected regions: {found - VALID_US_REGIONS}"

    def test_budget_null_for_non_2017(self, clean_df):
        non_2017 = clean_df[clean_df["order_date"].dt.year != 2017]
        assert non_2017["budget"].isna().all(), "Budget must be null for non-2017 orders"

    def test_budget_present_for_2017(self, clean_df):
        year_2017 = clean_df[clean_df["order_date"].dt.year == 2017]
        assert year_2017["budget"].notna().any(), "At least some 2017 orders should have a budget"

    def test_order_date_dtype(self, clean_df):
        assert clean_df["order_date"].dtype == "datetime64[ns]"

    def test_date_range(self, clean_df):
        assert clean_df["order_date"].dt.year.min() == 2014
        assert clean_df["order_date"].dt.year.max() == 2018
