import csv
from datetime import datetime
from pathlib import Path

RAW = Path("raw_netflix.csv")
OUT = Path("netflix.csv")

DATE_FORMATS = ["%m/%d/%y", "%m/%d/%Y"]

def is_date(s: str) -> bool:
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            pass
    return False

def normalize():
    if not RAW.exists():
        raise FileNotFoundError(f"Missing input file: {RAW}")

    with RAW.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    rows = []
    current_title = ""

    for line in lines:
        parts = [p.strip() for p in line.split(",")]

        # If line has a valid date → new record
        if len(parts) >= 2 and is_date(parts[-1]):
            date = parts[-1]
            title = ",".join(parts[:-1]).strip()

            # If previous title exists, flush it
            if current_title:
                rows.append((current_title, last_date))

            current_title = title
            last_date = date

        else:
            # Wrapped title line → append to previous title
            current_title = f"{current_title} {line}".strip()

    # Flush last row
    if current_title:
        rows.append((current_title, last_date))

    # Validation
    for idx, (title, date) in enumerate(rows, start=1):
        if not title:
            raise ValueError(f"Row {idx}: Empty title")
        if not is_date(date):
            raise ValueError(f"Row {idx}: Invalid date '{date}'")

    # Write clean CSV
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Date"])
        for t, d in rows:
            w.writerow([t, d])

    print(f"Normalized {len(rows)} rows → {OUT}")

if __name__ == "__main__":
    normalize()

