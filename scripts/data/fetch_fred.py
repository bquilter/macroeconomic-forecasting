import pandas as pd
from pathlib import Path
from fredapi import Fred
from dotenv import load_dotenv
import os

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
