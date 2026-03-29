import pandas as pd
from datetime import datetime
import os
import sys

# Default data file path (override via env or CLI)
FILE_PATH = 'your_data_file.csv'


def load_dataframe(path: str) -> pd.DataFrame:
    """Load CSV with fallbacks for malformed lines or missing file."""
    try:
        return pd.read_csv(path, sep=',', engine='python', on_bad_lines='skip')
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        return pd.read_csv(path, sep=',', engine='python', on_bad_lines='warn')
    except FileNotFoundError:
        print(f"Data file not found: {path}. Creating a new one.")
        return pd.DataFrame(columns=['Title', 'Date'])


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

