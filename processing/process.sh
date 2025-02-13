mkdir -p output

# Run scripts and capture output to both console and log file
python part1.py host/input.csv 2>&1 | tee output/log.txt
python part2.py 2>&1 | tee -a output/log.txt
python part3.py 2>&1 | tee -a output/log.txt

zip -r output.zip output
cp output.zip host/output.zip
