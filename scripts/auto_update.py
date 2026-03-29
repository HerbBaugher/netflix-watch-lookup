import pandas as pd
from datetime import datetime

FILE_PATH = 'data/Netflix_txt.txt'

def main():
    # Load existing file with proper delimiter
    df = pd.read_csv(FILE_PATH, sep=',')  # Specify comma as delimiter
    
    # Create new row
    new_row = {
        'Title': 'Auto-update heartbeat',
        'Date': datetime.now().strftime('%m/%d/%y')  # Match your date format
    }
    
    # Append row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save back to file with proper CSV format
    df.to_csv(FILE_PATH, index=False, lineterminator='\n')
    
    print('Auto-update completed.')

if __name__ == '__main__':
    main()
