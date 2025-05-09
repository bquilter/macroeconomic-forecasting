from pathlib import Path
import sys

# Add project root to PYTHONPATH so absolute imports work
sys.path.append(str(Path(__file__).resolve().parents[1]))

from data.fetch_fred import fetch_all_macro_data

if __name__ == "__main__":
    print("🚀 Running FRED data fetch...")
    fetch_all_macro_data()
    print("✅ FRED data fetch completed.")
