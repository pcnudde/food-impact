import sys

def process_csv(input_file):
    # Copy the input file to output.csv line by line
    with open(input_file, 'r') as infile, open('output.csv', 'w') as outfile:
        for line in infile:
            outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_csv.py <input_file>")
        sys.exit(1)
        
    process_csv(sys.argv[1])