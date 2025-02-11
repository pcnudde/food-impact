import sys
import pandas as pd


def process_csv(input_file):
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Do some simple processing (example: add a column with row numbers)
    df['row_number'] = range(1, len(df) + 1)
    
    # Save the processed file
    df.to_csv('output.csv', index=False)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_csv.py <input_file>")
        sys.exit(1)
        
    process_csv(sys.argv[1])