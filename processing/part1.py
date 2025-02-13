# PART 1
# This is Part 1 of three parts, each in a separate Jupyter Notebook cell.
# For this Part 1: input file: worksheet_in.csv   output file: impacts1done_lbs.csv
# It uses weights in worksheet_in.csv after pre-processing (if needed) by 0_Prep_vx.ipynb
# Can be used without pre-processing if worksheet_in is ensured as having: 
# one column labeled "product" (the column that identifies the product, e.g., "pineapple pizza") 
# a column labeled "product weight (e.g., "2164"),
# and a column named qty if there is a column for number of items, such as cases
# and a column labeled "unit" for the unit of weight (e.g. 'lbs', kilos, gallons...) 
# PART ONE uses AI to identify ingredients of each product and converts the weight to lbs if need be 
# If all units are pounds, but not specified as such, one can add an otherwise empty column labeled 'unit' (case sensitive) 
# and it will be populated with 'lbs' via the code df['unit'] = df['unit'].fillna('lbs') about a dozen lines below.
# This Notebook can process a worksheet combining units of lbs, kilos, grams, gallons, liters etc.
# The final output will be two .csv files written to disk, one with units lbs/gallons/acres: 3_impacts_lbs.csv; 
# the other with units in kilograms/liters/sq meters/: 3_impacts_metric.csv

import pandas as pd
import json
import concurrent.futures
import re
import sys
import backoff
from openai import OpenAI,RateLimitError


if len(sys.argv) != 2:
    print("Usage: python part1.py <input_file>")
    sys.exit(1)
        
input_file = sys.argv[1]

client = OpenAI()

# List of prioritized ingredients
prioritized_ingredients = {
    "animal fats", "beef", "chicken", "duck", "eggs", "goat", "lamb/mutton",
    "pork", "turkey", "unidentified meat", "veal", "dairy milk", "butter",
    "buttermilk", "dairy cheese", "concentrated milk", "cream", "ghee",
    "ice cream", "lactose powder", "low fat yogurt", "milk powder", "skim milk",
    "whey powder", "yogurt", "almond milk", "apples", "bananas", "barley (beer)",
    "beans and pulses (dried)", "berries", "cabbages and other brassicas (broccoli)",
    "cassava and other roots", "citrus fruit", "cocoa", "coffee", "corn (maize)",
    "fruits", "grains/cereals (except rice)", "legumes", "oat milk", "oats (oatmeal)",
    "olives (oil)", "onions and leeks", "other vegetables", "palm (oil)", "peanuts/groundnuts",
    "peas", "potatoes", "rapeseed/canola (oil)", "rice", "rice milk", "root vegetables",
    "roots and tubers", "soy milk", "soybeans (oil)", "soybeans/tofu", "stimulants & spices",
    "sugars and sweeteners", "sunflower (oil)", "tomatoes", "tree nuts and seeds",
    "vegetable oils", "wheat/rye (bread/pasta/baked goods)", "wine grapes (wine)",
    "non-dairy cheese or yogurt", "water", "unknown", "flavoring", "additive", "seaweed (dried)",
    "seaweed (fresh)", "bivalves", "catfish", "milkfish", "carp", "shrimp",
    "silver or bighead carp", "tilapia", "trout", "anchovies", "bass",
    "billfish", "bluefin tuna", "bonitos", "cod", "congers", "flounder", "haddock",
    "hake", "halibut", "herring", "jacks", "lobster", "mullets", "redfish",
    "sardines", "sauries", "tuna", "smelt", "sole", "squid or cuttlefish or octopus",
    "crab", "fish (finfish)", "salmon"
}

# Load and preprocess dataframe
df = pd.read_csv(input_file, skiprows=0)
df = df[df['product'].notna() & (df['product'] != '')]
num_missing_units = df['unit'].isna().sum()
if num_missing_units > (len(df) / 2):
    df['unit'] = df['unit'].fillna('lbs')
df['product'] = df['product'].str.replace(',', '', regex=False)
df['product_weight'] = pd.to_numeric(df['product_weight'], errors='coerce')
df['unit'] = df['unit'].fillna('lbs')
if 'qty' not in df.columns:
    df['qty'] = 1

indexes = df.index.tolist()
items = df['product'].str.strip().tolist()
weights = df['product_weight'].tolist()
units = df['unit'].tolist()
qty = df['qty'].tolist()  # Ensure 'qty' is read from the input file

@backoff.on_exception(backoff.expo, RateLimitError)
def get_ingredients(item):
    # First, prioritize known ingredients
    known_ingredients = {ing: 100 for ing in prioritized_ingredients if re.search(rf"\b{re.escape(ing)}\b", item, re.IGNORECASE)}
    
    if known_ingredients:
        return known_ingredients  # Return directly if any known ingredient matches 100%

    # Use AI if no known ingredient is identified
    prompt = (f"I have list of food purchases from a University in a large excel file. One item is listed as '{item}'"
              " I would like you to very concisely list the major ingredients of this item and the relative percentages."
              " List only the major ingredients and the sum of the percentages should be 100%."
              " Do not list water as an ingredient of a dairy product."
              " If the item is dairy milk, butter, cheese, or ice cream, do not separate the product into separate ingredients"
              " Just specify that the only ingredient is 100% dairy milk, butter or cheese or ice cream."
              " If a product is vegan, do not specify any animal products as ingredients."
              " For example if the item is labeled as vegan yogurt, specify non-dairy milk or non-dairy yogurt as an ingredient, not yogurt."
              " Please give your answer in json. Output the JSON only. Json schema {'ingredient name': Percentage}")

    completion = client.chat.completions.create(
        model="gpt-4o",
        #        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a food scientist and you know the formulation of common products"},
            {"role": "user", "content": prompt}
        ]
    )
    
    gptresult = completion.choices[0].message
    return json.loads(gptresult.content)

def sanitize_ingredient(ingredient_name):
    return ingredient_name.replace(',', '')

# Process item function for parallel execution
def process_item(index, item, weight, unit, qty):
    ingredient_data = get_ingredients(item)
    sanitized_rows = []
    for ingredient, percent_str in ingredient_data.items():
        sanitized_ingredient = sanitize_ingredient(ingredient)
        try:
            percent = float(percent_str)
        except (ValueError, TypeError):
            continue
        weight_ingredient = round(weight * (percent / 100.0), 4)
        sanitized_rows.append((index + 2, item, sanitized_ingredient, weight, unit, percent, weight_ingredient, qty))
    return sanitized_rows

# Use ThreadPoolExecutor for parallel processing
results = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_item = {
        executor.submit(process_item, index, item, weight, unit, qty): (index, item)
        for index, item, weight, unit, qty in zip(indexes, items, weights, units, qty)
    }
    for future in concurrent.futures.as_completed(future_to_item):
        try:
            results.extend(future.result())
        except Exception as exc:
            index_item_pair = future_to_item[future]
            print(f"Item {index_item_pair} generated an exception: {exc}")

# Prepare dataframe from results
columns = ["index", "product", "ingredient", "product_weight", "unit", "percent", "weight_ingredient", "qty"]
df2 = pd.DataFrame(results, columns=columns)

lookup_dict = {
    "ounce,ounces,oz": .0625,
    "pound,pounds,lb,lbs": 1,
    "g,gr,gram,grams": .002205,
    "k,kg,kilo,kilos,kilogram,kilograms": 2.20462,
    "liter,liters,ltr,lt,l": 2.20462,
    "pt,pint,pints": 1.04,
    "quarts,qt": 2.085,
    "gal,gl,gall,gallon,gallons": 8.34,
}
lookup_dict = dict(sum([[(u, lookup_dict[k]) for u in k.split(',')] for k in lookup_dict], []))

def convert_weight_to_lbs(weight, unit):
    if unit not in lookup_dict:
        print(f"Unit '{unit}' not found. Please use a valid unit.")
        return 0.0  # Return 0.0 for unrecognized units
    lbs = weight * lookup_dict.get(unit, 0.0)
    return round(lbs, 2)

df2['lbs'] = df2.apply(
    lambda row: convert_weight_to_lbs(row['weight_ingredient'], row['unit']) if pd.notnull(row['weight_ingredient']) else 0.0,
    axis=1
)

# Sort the DataFrame by the "index" field
df2 = df2.sort_values(by='index')

df2.to_csv('output/impacts1done_lbs.csv', index=False, encoding='utf-8')

print("PART 1 complete: see output/impacts1done_lbs.csv")