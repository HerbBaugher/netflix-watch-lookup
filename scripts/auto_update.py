import pandas as pd
from datetime import datetime
import os
import sys

# Default data file path (adjust as needed)
FILE_PATH = 'your_data_file.csv'

def load_dataframe(path: str) -> pd.DataFrame:
    # Attempt to read, with a sensible set of fallbacks
    try:
        return pd.read_csv(path, sep=',', engine='python', on_bad_lines='skip')
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        # Fallback: try again with different tolerance
        return pd.read_csv(path, sep=',', engine='python', on_bad_lines='warn')
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty DataFrame with expected columns
        print(f"Data file not found: {path}. A new one will be created.")
        return pd.DataFrame(columns=['Title', 'Date'])

def ensure_columns(df: pd.DataFrame):
    # Ensure the expected columns exist
    for col in ['Title', 'Date']:
        if col not in df.columns:
            df[col] = pd.NA

def append_heartbeat(df: pd.DataFrame) -> pd.DataFrame:
    new_row = {
        'Title': 'Auto-update heartbeat',
        'Date': datetime.now().strftime('%m/%d/%y')
    }
    # Append as a new row
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

def save_dataframe(df: pd.DataFrame, path: str):
    # Save with a consistent newline terminator
    df.to_csv(path, index=False, lineterminator='\n')
    print(f"Updated data saved to {path}")

def main():
    # Allow overriding path via CLI or environment
    data_path = os.environ.get('DATA_FILE', FILE_PATH)
    if len(sys.argv) > 1:
        data_path = sys.argv<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[1]</a>

    df = load_dataframe(data_path)

    # If the DataFrame is empty (new file), ensure expected columns exist
    if df.empty:
        ensure_columns(df)

    # If there was a parsing issue, you might still want to append the heartbeat.
    # We'll always append a heartbeat for consistency in this script.
    df = append_heartbeat(df)

    # Ensure columns exist before saving (defensive)
    ensure_columns(df)

    save_dataframe(df, data_path)

if __name__ == '__main__':
    main()
