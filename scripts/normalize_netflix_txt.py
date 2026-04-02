import pandas as pd
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Correct input file
RAW = DATA / "Netflix_txt.txt"

# Output file (same as auto_update.py)
OUTPUT = ROOT / "netflix_data.csv"


def normalize():
    """Normalize the Netflix TXT file into a clean CSV."""
    if not RAW.exists():
        raise FileNotFoundError(f"Missing input file: {RAW}")

    print(f"Reading TXT file: {RAW}")

    # Read the Netflix TXT file (tab-separated)
    df = pd.read_csv(RAW, sep="\t", header=0, encoding="utf-8")

    # Standardize column names
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Convert date column if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Save normalized CSV
    df.to_csv(OUTPUT, index=False)
    print(f"Saved normalized CSV → {OUTPUT}")


def main():
    print("=== Normalize Netflix TXT Starting ===")
    print(f"ROOT: {ROOT}")
    print(f"DATA: {DATA}")

    normalize()

    print("=== Normalize Netflix TXT Complete ===")


if __name__ == "__main__":
    main()
