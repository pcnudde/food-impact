# PART 3
# Input file: impacts2done_lbs.csv   Output files: 3_impacts_lbs.csv and 3_impacts_metric.csv
# This section does not use OpenAI at all but, instead loads a factors.csv files to convert weights of foods to impacts. The factors.csv file
# has a first column for food category and other columns for caloric value, co2 equivalent emissions, carbon opportunity cost, direct animal lives, 
# total lives, freshwater withdrwawl (liters/kg and gallons/lb), land use (sq meters and acres), eutrophication
# Please note the final 3_impacts_lbs.csv and 3_impacts_metric.csv output files this process should save on your device

import pandas as pd

# Load all conversion factors from a single file
def load_conversion_factors(filename):
    df = pd.read_csv(filename)
    
    columns_to_numeric = ['co2', 'land_acres', 'land_metric', 'carbon_opp', 'kcal', 'd_lives', 't_lives', 'water', 'eutro']
    df[columns_to_numeric] = df[columns_to_numeric].apply(pd.to_numeric, errors='coerce')
    
    # Fill NaN values with 0 or another sensible default
    df[columns_to_numeric] = df[columns_to_numeric].fillna(0)
    
    factors = {
        'CO2': df.set_index('category')['co2'].to_dict(),
        'land_acres': df.set_index('category')['land_acres'].to_dict(),
        'land_metric': {k: v / 2.2046 for k, v in df.set_index('category')['land_metric'].to_dict().items()},
        'carbon_opp': df.set_index('category')['carbon_opp'].to_dict(),
        'kcal': df.set_index('category')['kcal'].to_dict(),
        'd_lives': df.set_index('category')['d_lives'].to_dict(),
        't_lives': df.set_index('category')['t_lives'].to_dict(),
        'water': df.set_index('category')['water'].to_dict(),
        'eutro': df.set_index('category')['eutro'].to_dict()
    }
    return factors

# Load the factors from factors.csv
factors = load_conversion_factors("factors.csv")
CO2_FACTORS = factors['CO2']
LAND_USE_ACRES = factors['land_acres']
LAND_USE_METERS = factors['land_metric']
CARBON_OPP_FACTORS = factors['carbon_opp']
KCAL_FACTORS = factors['kcal']
D_LIVES_FACTORS = factors['d_lives']
LIVES_FACTORS = factors['t_lives']
WATER_FACTORS = factors['water']
EUTRO_FACTORS = factors['eutro']

def calculate_impact(df, factor_dict, column_name):
    return df.apply(lambda row: row['lbs'] * factor_dict.get(row['category'], 0), axis=1)

def main():
    df = pd.read_csv("output/impacts2done_lbs.csv", encoding='ISO-8859-1')
    
    # Convert the 'lbs' column to numeric, coercing errors to NaN
    df['lbs'] = pd.to_numeric(df['lbs'], errors='coerce')
    
    # Fill NaN values in 'lbs' with 0 by assigning the modified column back to the DataFrame
    df['lbs'] = df['lbs'].fillna(0)

    # Calculate impacts including d_lives and eutrophication
    df['CO2'] = calculate_impact(df, CO2_FACTORS, 'CO2')
    df['landuse'] = calculate_impact(df, LAND_USE_ACRES, 'landuse')
    df['landuse_meters'] = calculate_impact(df, LAND_USE_METERS, 'landuse_meters')
    df['carbonopp'] = calculate_impact(df, CARBON_OPP_FACTORS, 'carbonopp')
    df['kcal'] = calculate_impact(df, KCAL_FACTORS, 'kcal')
    df['d_lives'] = calculate_impact(df, D_LIVES_FACTORS, 'd_lives')
    df['lives'] = calculate_impact(df, LIVES_FACTORS, 'lives')
    df['water'] = calculate_impact(df, WATER_FACTORS, 'water')
    df['eutro'] = calculate_impact(df, EUTRO_FACTORS, 'eutro')

    # Group and sum the data
    grouped = df.groupby('category').agg({
        'lbs': 'sum',
        'CO2': 'sum',
        'landuse': 'sum',
        'landuse_meters': 'sum',
        'carbonopp': 'sum',
        'kcal': 'sum',
        'd_lives': 'sum',
        'lives': 'sum',
        'water': 'sum',
        'eutro': 'sum'
    }).reset_index()

    total_row = grouped[['lbs', 'CO2', 'landuse', 'landuse_meters', 'carbonopp', 'kcal', 'd_lives', 'lives', 'water', 'eutro']].fillna(0).astype(float).sum()
    total_row['category'] = 'Total'
    grouped = pd.concat([grouped, pd.DataFrame([total_row])], ignore_index=True)
   
    # Define specific categories for additional totals calculation
    specific_categories = ['butter', 'cheese', 'cream', 'dairy milk', 'buttermilk', 'ice cream', 'low fat yogurt', 'milk powder', 'yogurt', 'concentrated milk', 'ghee', 'lactose powder', 'skim milk', 'whey powder']
    specific_grouped = grouped.loc[grouped['category'].str.strip().str.lower().isin(specific_categories)].copy()
    specific_grouped[['lbs', 'CO2', 'landuse', 'carbonopp', 'kcal', 'd_lives', 'lives', 'water', 'eutro']] = specific_grouped[['lbs', 'CO2', 'landuse', 'carbonopp', 'kcal', 'd_lives', 'lives', 'water', 'eutro']].fillna(0).astype(float)
    specific_total_row = specific_grouped[['lbs', 'CO2', 'landuse', 'landuse_meters', 'carbonopp', 'kcal', 'd_lives', 'lives', 'water', 'eutro']].sum()
    specific_total_row['category'] = 'Subtotal for dairy'

    grouped = pd.concat([grouped, pd.DataFrame([specific_total_row])], ignore_index=True)

    # Format the output for the first file (3_impacts_lbs.csv)
    formatted_df_lbs = pd.DataFrame({
        'CATEGORY': grouped['category'],
        '(weight/lbs)': grouped['lbs'].map('{:.1f}'.format),
        '(calories)': grouped['kcal'].div(2.20462).map('{:.0f}'.format),         
        '(lbs CO2e)': grouped['CO2'].map('{:.0f}'.format),       
        '(lbs carbon opp costs)': grouped['carbonopp'].map('{:.0f}'.format),
        '(direct animal lives)': grouped['d_lives'].map('{:.1f}'.format),
        '(total animal lives)': grouped['lives'].map('{:.1f}'.format),
        '(water gallons)': grouped['water'].mul(.119826427).map('{:.0f}'.format),        
        '(land use acres)': grouped['landuse'].map('{:.3f}'.format),
        '(lbs PO4-eq eutrophication)': grouped['eutro'].div(1000).map('{:.5f}'.format)
    })

    # Save the first formatted DataFrame to a CSV
    formatted_df_lbs.to_csv('output/impacts3_lbs.csv', index=False, encoding='utf-8')

    # Format the output for the second file (3_impacts_metric.csv)
    formatted_df_metric = pd.DataFrame({
        'CATEGORY': grouped['category'],
        '(weight/kg)': grouped['lbs'].div(2.2046).map('{:.1f}'.format),
        '(calories)': grouped['kcal'].div(2.20462).map('{:.0f}'.format),
        '(kg CO2e)': grouped['CO2'].div(2.2046).map('{:.0f}'.format),
        '(kg carbon opp costs)': grouped['carbonopp'].div(2.2046).map('{:.0f}'.format),
        '(direct animal lives)': grouped['d_lives'].map('{:.1f}'.format),
        '(total animal lives)': grouped['lives'].map('{:.1f}'.format),        
        '(water liters)': grouped['water'].div(2.2046).map('{:.2f}'.format),
        '(land use sq meters)': grouped['landuse_meters'].map('{:.0f}'.format),        
        '(grams PO4-eq eutrophication)': grouped['eutro'].div(2.2046).map('{:.2f}'.format)
    })

    # Save the second formatted DataFrame to a CSV
    formatted_df_metric.to_csv('output/impacts3_metric.csv', index=False, encoding='utf-8')

main()

print("PLEASE REVIEW THE output/impacts3_lbs.csv AND output/impacts3_metric.csv FILES TO SEE RESULTS")
