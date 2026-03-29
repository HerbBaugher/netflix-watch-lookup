import pandas as pd
import re

def load_netflix_file(text: str) -> pd.DataFrame:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = []

    date_pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{2})$')

    for line in lines:
        # Skip header if present
        if line.lower().startswith("title,date"):
            continue

        match = date_pattern.search(line)
        if not match:
            # Skip malformed lines
            continue

        date = match.group(1)
        title = line[:match.start()].strip()

        rows.append({"Title": title, "Date": date})

    return pd.DataFrame(rows)


def ensure_columns(df: pd.DataFrame):
    """Ensure required columns exist."""
    for col in ['Title', 'Date']:
        if col not in df.columns:
            df[col] = pd.NA


def append_heartbeat(df: pd.DataFrame) -> pd.DataFrame:
    """Append a heartbeat row with today's date."""
    new_row = {
        'Title': 'Auto-update heartbeat',
        'Date': datetime.now().strftime('%m/%d/%y')
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


def save_dataframe(df: pd.DataFrame, path: str):
    """Save CSV with consistent formatting."""
    df.to_csv(path, index=False, lineterminator='\n')
    print(f"Updated data saved to {path}")


def main():
    # Allow overriding path via environment or CLI
    data_path = os.environ.get('DATA_FILE', FILE_PATH)

    if len(sys.argv) > 1:
        data_path = sys.argv[1]   # ← FIXED (removed HTML garbage)

    df = load_dataframe(data_path)

    if df.empty:
        ensure_columns(df)

    df = append_heartbeat(df)
    ensure_columns(df)

    save_dataframe(df, data_path)


if __name__ == '__main__':
    main()

