import pandas as pd
from pathlib import Path

# ---------------------------
# PATH SETUP (FIXED)
# ---------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

RAW_TXT = DATA / "Netflix_txt.txt"
OUTPUT_CSV = ROOT / "netflix_data.csv"


def normalize():
    """Convert messy Netflix TXT into clean structured CSV."""

    if not RAW_TXT.exists():
        raise FileNotFoundError(f"Missing input file: {RAW_TXT}")

    print(f"Reading TXT file: {RAW_TXT}")

    records = []
    current_title_lines = []

    with open(RAW_TXT, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    # Skip header line
    for line in lines[1:]:
        parts = line.rsplit(" ", 1)

        # Detect date at end of line
        if len(parts) == 2 and "/" in parts[1]:
            current_title_lines.append(parts[0])

            title = " ".join(current_title_lines).strip()
            date = parts[1]

            records.append({
                "title": title,
                "date": date
            })

            current_title_lines = []
        else:
            current_title_lines.append(line)

    if not records:
        raise ValueError("No records parsed — check TXT format")

    df = pd.DataFrame(records)

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort newest first (optional but helpful)
    df = df.sort_values("date", ascending=False)

    # Save output
    df.to_csv(OUTPUT_CSV, index=False)

    print("Preview:")
    print(df.head())

    print(f"Saved cleaned data → {OUTPUT_CSV}")


def main():
    print("=== Netflix Auto Update Starting ===")
    print(f"ROOT: {ROOT}")
    print(f"DATA: {DATA}")

    normalize()

    print("=== Update Complete ===")


if __name__ == "__main__":
    main()
