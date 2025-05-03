from scripts.config.series_list import FRED_SERIES
from fredapi import Fred
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import os

# Load API key and init FRED client
load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

# Ensure output folder exists
Path("data/metadata").mkdir(parents=True, exist_ok=True)

# Loop through series and collect metadata
records = []
for country, series_id in FRED_SERIES.items():
    try:
        print(f"📡 Fetching metadata for {country} ({series_id})")
        info = fred.get_series_info(series_id)
        record = info.to_dict()
        record["country"] = country
        record["series_id"] = series_id
        records.append(record)
    except Exception as e:
        print(f"❌ Failed to fetch {series_id} for {country}: {e}")

# Save as DataFrame
df_meta = pd.DataFrame(records)
df_meta.to_csv("data/metadata/fred_series_metadata.csv", index=False)
print("✅ Metadata saved to data/metadata/fred_series_metadata.csv")
