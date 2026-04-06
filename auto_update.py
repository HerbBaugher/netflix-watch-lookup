import pandas as pd
from pathlib import Path
import sys

# ---------------------------
# PATHS
# ---------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW_TXT = DATA / "Netflix_txt.txt"           # Required input TXT
RAW_CSV = DATA / "NetflixViewingHistory.csv" # Optional CSV input
OUTPUT_CSV = ROOT / "netflix_data.csv"       # Normalized output

# ---------------------------
# FUNCTIONS
# ---------------------------
def clean_netflix_txt():
    """Clean and normalize Netflix TXT into a proper CSV."""
    if not RAW_TXT.exists():
        print(f"❌ Missing input file: {RAW_TXT}")
        sys.exit(1)

    print(f"Reading TXT file: {RAW_TXT}")

    titles = []
    dates = []

    current_title = ""
    current_date = None

    with open(RAW_TXT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Check if line contains a date (very simple heuristic: contains / and digits)
            if "/" in line and any(c.isdigit() for c in line):
                current_date = line
                titles.append(current_title.strip())
                dates.append(current_date.strip())
                current_title = ""
                current_date = None
            else:
                # Line is part of the title
                if current_title:
                    current_title += " " + line
                else:
                    current_title = line

    # Handle last title without date
    if current_title:
        titles.append(current_title.strip())
        dates.append("")

    df = pd.DataFrame({"title": titles, "date": dates})

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Clean CSV saved → {OUTPUT_CSV}")


def normalize_optional_csv():
    """Optional: normalize NetflixViewingHistory.csv if it exists."""
    if RAW_CSV.exists():
        print(f"Reading optional CSV: {RAW_CSV}")
        try:
            df = pd.read_csv(RAW_CSV, header=0, encoding="utf-8")
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"✅ Normalized optional CSV → {OUTPUT_CSV}")
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

    # Always clean TXT first
    clean_netflix_txt()

    # Optionally normalize CSV if it exists
    normalize_optional_csv()

    print("\n=== Auto Update Complete ===")


# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    main()
