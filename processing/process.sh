mkdir -p output
cp host/input.csv output/input.csv

# Run scripts and capture output to both console and log file
python -u part1.py host/input.csv 2>&1 | tee output/log.txt
python -u part2.py 2>&1 | tee -a output/log.txt
python -u part3.py 2>&1 | tee -a output/log.txt

zip -r output.zip output
cp output.zip host/output.zip
