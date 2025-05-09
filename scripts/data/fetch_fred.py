import pandas as pd
from pathlib import Path
from fredapi import Fred
from dotenv import load_dotenv
import os

# Load CPI and GDP series from external config
from scripts.config.series_list import FRED_SERIES

# --- Core FRED access functions ---
def get_fred_series(series_id: str) -> pd.Series:
    load_dotenv()
    fred = Fred(api_key=os.getenv("FRED_API_KEY"))
    return fred.get_series(series_id)

def save_series_to_csv(series: pd.Series, series_id: str, folder: str = "data/raw"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    df = series.to_frame(name="value")
    df.index.name = "date"
    filepath = Path(folder) / f"{series_id}.csv"
    df.to_csv(filepath)
    print(f"✅ Saved: {filepath}")

def load_series_from_csv(series_id: str, folder: str = "data/raw") -> pd.Series:
    filepath = Path(folder) / f"{series_id}.csv"
    df = pd.read_csv(filepath, parse_dates=["date"], index_col="date")
    return df["value"]

def get_or_fetch_series(series_id: str, folder: str = "data/raw") -> pd.Series:
    filepath = Path(folder) / f"{series_id}.csv"
    if filepath.exists():
        print(f"📂 Loaded from cache: {filepath}")
        return load_series_from_csv(series_id, folder)
    else:
        print(f"🌐 Fetching from FRED: {series_id}")
        series = get_fred_series(series_id)
        save_series_to_csv(series, series_id, folder)
        return series

# --- Fetch and combine CPI and GDP series ---
def fetch_all_macro_data():
    rows = []

    for series_type, country_map in FRED_SERIES.items():
        for country, series_id in country_map.items():
            series = get_or_fetch_series(series_id)
            df = series.to_frame(name="value").reset_index()
            df["country"] = country
            df["series_type"] = series_type
            rows.append(df)

    macro_df = pd.concat(rows)
    macro_df = macro_df.rename(columns={"date": "date"})
    macro_df = macro_df.sort_values(["series_type", "country", "date"])

    out_path = Path("data/processed/merged/core_macro_long.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    macro_df.to_csv(out_path, index=False)
    print(f"✅ Saved merged macro data to {out_path}")

# --- Entry point ---
if __name__ == "__main__":
    fetch_all_macro_data()
