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
    if "date" in
