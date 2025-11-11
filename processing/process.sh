mkdir -p output
mkdir -p input
cp host/input.csv output/input.csv
cp host/input.csv input.csv

# Run notebook
papermill FoodImpacts.ipynb output/FoodImpactsOut.ipynb 

zip -r output.zip output
cp output.zip host/output.zip
