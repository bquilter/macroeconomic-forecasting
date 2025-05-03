from scripts.config.series_list import FRED_SERIES
from scripts.data.clean_fred_series import clean_and_save_series

def run_batch():
    print("📦 Starting batch CPI processing...\n")
    for country, series_id in FRED_SERIES.items():
        print(f"🔄 Processing: {country} ({series_id})")
        try:
            clean_and_save_series(series_id=series_id, country_name=country)
        except Exception as e:
            print(f"❌ Failed for {country}: {e}")

    print("\n✅ Batch CPI processing complete.")

if __name__ == "__main__":
    run_batch()
