
import pandas as pd
from datetime import datetime

FILE_PATH = 'data/Netflix_txt.txt'

def main():
    # Load existing file
    df = pd.read_csv(FILE_PATH)

    # Create new row
    new_row = {
        'Title': 'Auto-update heartbeat',
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Append row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save back to file
    df.to_csv(FILE_PATH, index=False)

    print('Auto-update completed.')

if __name__ == '__main__':
    main()
