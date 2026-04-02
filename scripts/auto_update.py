import pandas as pd
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Correct input files
RAW_TXT = DATA / "Netflix_txt.txt"
RAW_CSV = DATA / "NetflixViewingHistory.csv"  # optional if needed

# Output file
OUTPUT_CSV = ROOT / "netflix_data.csv"


def normalize():
    """Normalize the Netflix TXT file into a clean CSV."""
    if not RAW_TXT.exists():
        raise FileNotFoundError(f"Missing input file: {RAW_TXT}")

    print(f"Reading TXT file: {RAW_TXT}")

    # Read the Netflix TXT file (tab-separated)
    df = pd.read_csv(RAW_TXT, sep="\t", header=0, encoding="utf-8")

    # Standardize column names
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Convert date column if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Save normalized CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved normalized CSV → {OUTPUT_CSV}")


def main():
    print("=== Auto Update Script Starting ===")
    print(f"ROOT: {ROOT}")
    print(f"DATA: {DATA}")

    normalize()

    print("=== Auto Update Complete ===")


if __name__ == "__main__":
    main()
