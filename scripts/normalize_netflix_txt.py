import pandas as pd
from pathlib import Path
import sys

# ---------------------------
# PATHS
# ---------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW_TXT = DATA / "Netflix_txt.txt"           # Input TXT
RAW_CSV = DATA / "NetflixViewingHistory.csv" # Optional input CSV if needed
OUTPUT_CSV = ROOT / "netflix_data.csv"       # Normalized output

# ---------------------------
# FUNCTIONS
# ---------------------------
def normalize_txt():
    """Normalize the Netflix TXT file into a clean CSV."""
    if not RAW_TXT.exists():
        print(f"❌ ERROR: Missing input file: {RAW_TXT}")
        print("Make sure the file exists in your repo at data/Netflix_txt.txt")
        sys.exit(1)

    print(f"Reading TXT file: {RAW_TXT}")

    try:
        df = pd.read_csv(RAW_TXT, sep="\t", header=0, encoding="utf-8")
    except Exception as e:
        print(f"❌ Failed to read {RAW_TXT}: {e}")
        sys.exit(1)

    # Standardize column names
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Convert 'date' column if it exists
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Save normalized CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved normalized CSV → {OUTPUT_CSV}")


def normalize_csv():
    """Optional: normalize NetflixViewingHistory.csv if it exists."""
    if RAW_CSV.exists():
        print(f"Reading CSV file: {RAW_CSV}")
        try:
            df = pd.read_csv(RAW_CSV, header=0, encoding="utf-8")
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"✅ Normalized CSV → {OUTPUT_CSV}")
        except Exception as e:
            print(f"❌ Failed to read {RAW_CSV}: {e}")
    else:
        print(f"⚠️ Optional CSV not found: {RAW_CSV} (skipping)")


# ---------------------------
# MAIN
# ---------------------------
def main():
    print("\n=== Auto Update Script Starting ===")
    print(f"ROOT: {ROOT}")
    print(f"DATA: {DATA}")

    # Normalize TXT (required)
    normalize_txt()

    # Normalize optional CSV (if needed)
    normalize_csv()

    print("\n=== Auto Update Complete ===")


# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    main()
