import pandas as pd
from pathlib import Path
from scripts.data.fetch_fred import get_or_fetch_series
import argparse

def clean_and_save_series(series_id: str, country_name: str = None, output_folder: str = "data/processed") -> pd.DataFrame:
    """
    Fetches a FRED series (from cache or API), cleans it, and saves to processed folder.
    """
    from scripts.data.fetch_fred import get_or_fetch_series
    from pathlib import Path
    import pandas as pd

    # Fetch series
    series = get_or_fetch_series(series_id)

    # Clean
    df = series.to_frame(name="value")
    df = df[~df.index.duplicated(keep='first')].dropna()
    df = df.rename(columns={"value": "cpi"})

    # Save
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    filename = f"{country_name.replace(' ', '_').lower()}_core_cpi.csv" if country_name else f"{series_id}.csv"
    df.to_csv(Path(output_folder) / filename)

    print(f"✅ Saved: {filename}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch, clean, and save a FRED series.")
    parser.add_argument("series_id", help="FRED series ID (e.g., NZLCPIALLQINMEI)")
    parser.add_argument("--output", default="data/processed", help="Output folder path (default: data/processed)")

    args = parser.parse_args()

    clean_and_save_series(series_id=args.series_id, output_folder=args.output)
