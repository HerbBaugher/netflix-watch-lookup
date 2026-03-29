import pandas as pd

# Add error handling and flexible parsing
try:
    df = pd.read_csv('your_data_file.csv', sep=',', engine='python', on_bad_lines='skip')
except pd.errors.ParserError as e:
    print(f"CSV parsing error: {e}")
    # Try alternative parsing with different parameters
    df = pd.read_csv('your_data_file.csv', sep=',', engine='python', on_bad_lines='warn')
    
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
