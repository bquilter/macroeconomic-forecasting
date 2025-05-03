from pathlib import Path
import pandas as pd

def merge_series_long(series_dict: dict, input_folder: str = "data/processed/individual") -> pd.DataFrame:
    """
    Merge multiple cleaned CPI series into long format.
    Each input file should be named: <country>_core_cpi.csv
    Output DataFrame has columns: date, country, cpi
    """
    records = []

    for country in series_dict:
        filename = f"{country.replace(' ', '_').lower()}_core_cpi.csv"
        path = Path(input_folder) / filename

        if not path.exists():
            print(f"⚠️ Skipping {country} — file not found at {path}")
            continue

        df = pd.read_csv(path, parse_dates=["date"])
        df["country"] = country
        df = df[["date", "country", "cpi"]]
        records.append(df)

    merged_df = pd.concat(records, ignore_index=True)
    merged_df = merged_df.sort_values(["date", "country"])
    return merged_df
