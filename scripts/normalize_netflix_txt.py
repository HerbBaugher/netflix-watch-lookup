import csv
from datetime import datetime
from pathlib import Path

RAW = Path("raw_netflix.txt")
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

def extract_date(line: str):
    parts = line.rsplit(" ", 1)
    if len(parts) == 2 and is_date(parts[1]):
        return parts[0].strip(), parts[1].strip()
    return None, None

def normalize():
    if not RAW.exists():
        raise FileNotFoundError(f"Missing input file: {RAW}")

    with RAW.open("r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    rows = []
    current_title = ""

    for line in lines:
        title_part, date = extract_date(line)

        if date:
            full_title = (current_title + " " + title_part).strip()
            rows.append((full_title, date))
            current_title = ""
        else:
            current_title = (current_title + " " + line).strip()

    # Validation
    for idx, (title, date) in enumerate(rows, start=1):
        if not title:
            raise ValueError(f"Row {idx}: Empty title")
        if not is_date(date):
            raise ValueError(f"Row {idx}: Invalid date '{date}'")

    # Write CSV with QUOTED titles
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Title", "Date"])
        for title, date in rows:
            writer.writerow([title, date])

    print(f"Normalized {len(rows)} rows → {OUT}")

if __name__ == "__main__":
    normalize()

