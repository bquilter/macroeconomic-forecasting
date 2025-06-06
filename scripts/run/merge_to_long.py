from pathlib import Path
import pandas as pd
from scripts.config.series_list import FRED_SERIES
from scripts.data.merge_fred_series import merge_series_long

def run_merge():
    print("🔗 Merging cleaned CPI series into long format...")
    df_long = merge_series_long(FRED_SERIES)

    # Year-on-Year % change
    df_long["cpi_yoy"] = (
        df_long.sort_values(["country", "date"])
        .groupby("country")["cpi"]
        .transform(lambda x: x.pct_change(periods=4) * 100)
    )

    # Ensure output folder exists
    output_path = Path("data/processed/merged")
    output_path.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    out_file = output_path / "core_cpi_long.csv"
    df_long.to_csv(out_file, index=False)
    print(f"✅ Saved merged long-format CPI with YoY change: {out_file}")

if __name__ == "__main__":
    run_merge()
