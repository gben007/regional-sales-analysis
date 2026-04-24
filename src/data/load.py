from pathlib import Path
import pandas as pd

_RAW = Path(__file__).parents[2] / "data" / "raw" / "Regional Sales Dataset.xlsx"


def load_sheets(path: Path = _RAW) -> dict[str, pd.DataFrame]:
    """Read every sheet from the Excel workbook and return a named dict."""
    sheets = pd.read_excel(path, sheet_name=None)
    return {
        "sales":         sheets["Sales Orders"],
        "customers":     sheets["Customers"],
        "products":      sheets["Products"],
        "regions":       sheets["Regions"],
        "state_regions": sheets["State Regions"],
        "budgets":       sheets["2017 Budgets"],
    }
