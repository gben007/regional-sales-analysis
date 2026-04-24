"""Tests for src.data.load — Excel ingestion."""
import pytest


EXPECTED_KEYS = {"sales", "customers", "products", "regions", "state_regions", "budgets"}

EXPECTED_SHAPES = {
    "sales":         (64104, 12),
    "customers":     (175,   2),
    "products":      (30,    2),
    "budgets":       (30,    2),
}


class TestLoadSheets:
    def test_returns_all_keys(self, sheets):
        assert set(sheets.keys()) == EXPECTED_KEYS

    def test_no_empty_sheets(self, sheets):
        for name, df in sheets.items():
            assert len(df) > 0, f"Sheet '{name}' is empty"

    @pytest.mark.parametrize("sheet,expected_shape", EXPECTED_SHAPES.items())
    def test_sheet_shape(self, sheets, sheet, expected_shape):
        assert sheets[sheet].shape == expected_shape, (
            f"'{sheet}' expected {expected_shape}, got {sheets[sheet].shape}"
        )

    def test_sales_order_date_parseable(self, sheets):
        """OrderDate column must be coercible to datetime without errors."""
        import pandas as pd
        dates = pd.to_datetime(sheets["sales"]["OrderDate"], errors="coerce")
        assert dates.isna().sum() == 0, "Some OrderDate values could not be parsed"
