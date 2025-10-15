"""
Script: scrape_plum_product_details.py

Author: Avani

Description:
-------------
This script scrapes detailed product information from PlumGoodness skincare products using a previously scraped list of product links (from 'Data/plumgoodness_products.xlsx').

Features:
---------
1. Loads all products from the existing Excel file containing:
   - Product Name
   - Link
   - Price
   - MRP
   - Rating
   - Reviews
   - Keywords

2. For each product link, it scrapes:
   - Complete Ingredient List:
       Found in the div with class 'full-ingredint-list' inside the product page.
   - Highlighted Key Ingredients & Benefits:
       Found in the div with class 'goodness-inside'.
       Traverses each 'image__block_inner-blg' to extract:
         - Title (h4.text) = main ingredient
         - Goodness description (div.goodness_description) = short description
       Combines all main ingredients and their descriptions with " | " separator.

3. Detects combo products:
   - Products with no full ingredients AND no main ingredients are flagged as combos (Is_Combo = True)
   - Combo products are **included** in the final Excel with Is_Combo = True.

4. Saves the final detailed Excel:
   - File: plumgoodness_products_detailed.xlsx
   - Columns:
       Name, Link, Price, MRP, Rating, Reviews, Keywords,
       Complete Ingredient List,
       Highlighted Key Ingredients & Benefits,
       Is_Combo

Usage:
------
1. Make sure 'plumgoodness_products.xlsx' exists with product Name and Link.
2. Run this script:
       python scrape_plum_product_details.py
3. Wait for the scraping to finish. All products, including combos, will be saved.
4. The enriched Excel will be saved in the same folder.

Note:
-----
- Time delay of 1 second is used between requests to avoid overloading the server.
- Errors during requests are caught and printed without stopping the script.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Load your previously scraped product list (with Name, Link, Price, etc.)
df = pd.read_excel("../Data/plumgoodness_products.xlsx")

details_data = []

for idx, row in df.iterrows():
    product_url = row["Link"]
    print(f"\n🔍 Scraping details for: {row['Name']} -> {product_url}")

    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # ---- FULL INGREDIENTS ----
        full_ingredients_div = soup.find("div", class_="full-ingredint-list")
        full_ingredients = full_ingredients_div.get_text(strip=True) if full_ingredients_div else None

        # ---- MAIN INGREDIENTS ----
        main_ingredients_section = soup.find("div", class_="goodness-inside")
        main_ingredients = []

        if main_ingredients_section:
            ingredient_blocks = main_ingredients_section.find_all("div", class_="image__block_inner-blg")
            for block in ingredient_blocks:
                title_tag = block.find("h4", class_="text")
                desc_tag = block.find("div", class_="goodness_description")
                title = title_tag.get_text(strip=True) if title_tag else None
                desc = desc_tag.get_text(strip=True) if desc_tag else None
                if title:
                    main_ingredients.append(f"{title}: {desc}")

        main_ingredients_text = " | ".join(main_ingredients) if main_ingredients else None

        # ---- Detect combo products ----
        is_combo = False
        if not full_ingredients and not main_ingredients_text:
            is_combo = True
            print(f"⚠️ Marking combo product: {row['Name']}")

        # ---- Append single product details ----
        details_data.append({
            "Name": row["Name"],
            "Link": product_url,
            "Price": row["Price"],
            "MRP": row["MRP"],
            "Rating": row["Rating"],
            "Reviews": row["Reviews"],
            "Keywords": row["Keywords"],
            "Complete Ingredient List": full_ingredients,
            "Highlighted Key Ingredients & Benefits": main_ingredients_text,
            "Is_Combo": is_combo
        })

        time.sleep(1)  # polite scraping

    except Exception as e:
        print(f"❌ Error scraping {product_url}: {e}")
        continue

# ---- Save final Excel ----
details_df = pd.DataFrame(details_data)
details_df.to_excel("../Data/plumgoodness_products_detailed.xlsx", index=False)
print("\n✅ Detailed product data saved to ../Data/plumgoodness_products_detailed.xlsx")