"""Session-scoped fixtures — data is loaded once for the entire test run."""
import pytest
from src.data.load import load_sheets
from src.data.clean import build_master
from src.features.engineer import add_features


@pytest.fixture(scope="session")
def sheets():
    return load_sheets()


@pytest.fixture(scope="session")
def clean_df(sheets):
    return build_master(sheets)


@pytest.fixture(scope="session")
def featured_df(clean_df):
    return add_features(clean_df)
