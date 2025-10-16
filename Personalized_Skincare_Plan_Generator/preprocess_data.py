import pandas as pd
import numpy as np
import re

df = pd.read_excel(r'..\Data\plumgoodness_products_detailed.xlsx')

# Clean price columns
df['Price'] = df['Price'].replace('[₹,]', '', regex=True).astype(float)
df['MRP'] = df['MRP'].replace('[₹,]', '', regex=True).astype(float)

# Extract rating as float
df['Rating'] = df['Rating'].str.extract(r'([0-9.]+)').astype(float)

# Extract review count
df['Reviews'] = df['Reviews'].str.extract(r'([0-9,]+)').replace(',', '', regex=True).astype(float)

# Standardize boolean column
df['Is_Combo'] = df['Is_Combo'].astype(bool)

# Clean ingredient and key benefits columns
df['Complete Ingredient List'] = df['Complete Ingredient List'].replace('_x000D_|\\n', ' ', regex=True)
df['Highlighted Key Ingredients & Benefits'] = df['Highlighted Key Ingredients & Benefits'].replace('_x000D_|\\n', ' ', regex=True)

# Fill missing values for text columns
text_cols = ['Name', 'Link', 'Keywords', 'Complete Ingredient List', 'Highlighted Key Ingredients & Benefits']
df[text_cols] = df[text_cols].fillna('')

# Fill missing values for numeric columns
num_cols = ['Price', 'MRP', 'Rating', 'Reviews']
df[num_cols] = df[num_cols].fillna(0.0)

#save cleaned version
df.to_csv(r'..\Data\plumgoodness_products_cleaned.csv', index=False)
