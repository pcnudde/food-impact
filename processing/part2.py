# PART 2
# Input file: impacts1done_lbs.csv Output file: impacts2done_lbs.csv'
# This PART 2 categorizes each ingredient, drawing from the ingredient/category combinations found in foodcategories.json
# If it is an ingredient not already found in that .json file, it uses a prompt to AI to identify the appropriate category for the ingredient
# and then adds that ingredient/category combo at the end of the foodcategories.json file... Optionally, you could review and edit that at some point.
# You can select below, in this cell, between models of AI. The current default is
# The great majority of the time and expense of OpenAI was accomplished in PART 1 identifying ingredients and their relative weight... 
# And for experimentation/testing, one might quickly and cheaply start in this cell with the menu option "Run Selected Cell and All Below"

import pandas as pd
from openai import OpenAI,RateLimitError
import json
import concurrent.futures
import backoff
import os
import re

# Function to remove parentheses and their contents
def remove_parentheses(text):
    return re.sub(r'\(.*?\)', '', text).strip()

# Initialize OpenAI client
client = OpenAI()

@backoff.on_exception(backoff.expo, RateLimitError)

def get_category(ingredient):
    prompt = (
        "You are a food scientist with expertise in identifying food categories. "
        f"I have a list of food ingredients. One ingredient is '{ingredient}'. "
        "Your task is to identify the category that this ingredient most likely belongs to from the following list: "
        "fish (finfish), water, dairy milk, animal fats, beef, chicken, duck, eggs, goat, almond milk, seaweed (dried), seaweed (fresh), "
        "lamb/mutton, pork, turkey, unidentified meat, veal, butter, buttermilk, dairy cheese, non-dairy cheese or yogurt, "
        "apples, bananas, barley (beer), beans and pulses (dried), berries, cabbages and other brassicas (broccoli), "
        "concentrated milk, cream, flavoring, ghee, ice cream, cassava and other roots, citrus fruit, cocoa, coffee, "
        "lactose powder, low fat yogurt, milk powder, skim milk, corn (maize), fruits, grains/cereals (except rice), "
        "whey powder, yogurt, legumes, oat milk, oats (oatmeal), olives (oil), onions and leeks, other vegetables, "
        "palm (oil), peanuts/groundnuts, peas, potatoes, rapeseed/canola (oil), rice, rice milk, root vegetables, "
        "roots and tubers, soy milk, soybeans (oil), soybeans/tofu, stimulants & spices, sugars and sweeteners, sunflower (oil), "
        "tomatoes, tree nuts and seeds, vegetable oils, wheat/rye (bread/pasta/baked goods), wine grapes (wine), additive, unknown, "
        "bivalves, catfish, milkfish, carp, salmon, shrimp, silver or bighead carp, tilapia, trout, anchovies, bass, "
        "billfish, bivalves, bluefin tuna, bonitos, cod, congers, flounder, haddock, hake, halibut, herring, jacks, lobster, mullets, "
        "redfish, sardines, sauries,tuna, smelt, sole, trout, squid or cuttlefish or octopus, crab, lobster. "

        "Important: For ingredients like herbs, chili peppers, and garlic, please categorize them as 'other vegetables' "
        "rather than 'stimulants & spices'. Select only one category from the list that matches the ingredient exactly. "
        "Do not ever provide a response that is not in this list or that includes multiple categories. Be sure to include any parenthetical expression. "
        "When multiple options are correct, choose the most exact category match, rather than a more generic category. "
        "Except if the ingredient is a baked good, like a cake, pie, cookie or brownie "
        "then choose 'wheat/rye (bread/pasta/baked goods)' rather than an ingredient like cocoa or berries. "
        "Return the result in JSON format with the schema: {{'category': 'your_selected_category'}}. "
        "Ensure the selected category matches exactly one item from the list."
    )

    completion = client.chat.completions.create(
#            model="gpt-4o",  # Adjust model name as needed do not use o1 versions due to json formatting issues
        model="gpt-4o-mini",
#        model="o3-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    gptresult = completion.choices[0].message
    try:
        result = json.loads(gptresult.content)['category']
    except Exception as e:
        print(f"Error decoding JSON: {e}")
        print(gptresult.content)
        return "Unknown"
    
    return result

# Read the CSV file
df = pd.read_csv("output/impacts1done_lbs.csv", skiprows=0)

# use only if one does not want the foodcategories.json file updated with ingredients that are a small fraction of products (5% or less)
df = df[df['percent'] >= 6]

# Preprocess the ingredients: strip, lower case, remove parentheses
ingredients = df['ingredient'].str.strip().str.lower().apply(remove_parentheses).to_list()

# Load existing categories from the JSON file if it exists
categories_dict = {}

if os.path.exists('foodcategories.json'):
    with open('foodcategories.json', 'r', encoding='utf-8') as file:
        categories_dict = json.load(file)

# Filter out ingredients already categorized
ingredients = list(set(ingredients) - set(categories_dict.keys()))

print(f"Categorizing {len(ingredients)} elements")
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    categories = list(executor.map(get_category, ingredients))

# Update the categories_dict with the new categories
for ingredient, category in zip(ingredients, categories):
    categories_dict[ingredient] = category

# Save the updated categories_dict to the JSON file
with open('foodcategories.json', 'w') as file:
    json.dump(categories_dict, file)

# Part 2 for categorizing ingredients in the new CSV file
with open('output/impacts2done_lbs.csv', 'w', encoding='utf-8') as f:
    f.write("index,product,ingredient,category,product_weight,unit,percent,weight_ingredient,qty,lbs\n")
    for index, row in df.iterrows():
        index = row['index']
        product = row['product']
        ingredient = row['ingredient']
        product_weight = row['product_weight']
        unit = row['unit']
        percent = row['percent']
        weight_ingredient = row['weight_ingredient']
        qty = row['qty']
        lbs = row['lbs']
        
        # Preprocess the ingredient to remove parenthetic info
        cleaned_ingredient = remove_parentheses(ingredient.strip().lower())
        
        # Use cleaned_ingredient to lookup category
        category = categories_dict.get(cleaned_ingredient, 'Unknown')

        if pd.isna(qty):
            qty = ''

        f.write(f"{index},{product},{ingredient},{category.replace(',','')},{product_weight},{unit},{percent},{weight_ingredient},{qty},{lbs}\n")

print("PART 2 complete: note output/impacts2done_lbs.csv")

