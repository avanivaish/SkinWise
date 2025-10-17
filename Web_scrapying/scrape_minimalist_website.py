# -----------------------------------------------------------------------------------
# This script scrapes product data from the first page of the "Skin & Body" collection
# on the beminimalist.co website. It extracts the following details for each product:
# - Product Name
# - Product Link
# - Current Price
# - MRP (Original Price)
# 
# The scraped data is then saved to an Excel file located in the relative folder ..\Data
# ---------------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# -----------------------------
# URL and headers
# -----------------------------
URL = "https://beminimalist.co/collections/skin-body-1?sort_by=title-ascending&filter.p.m.my_fields.category=Skin"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -----------------------------
# Send request and parse
# -----------------------------
response = requests.get(URL, headers=HEADERS)
print(f"Response Status Code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

# Find the main product grid
product_grid = soup.find("div", id="main-collection-product-grid")
if not product_grid:
    print("❌ Could not find product grid")
    exit()

# Find all product items
products = product_grid.find_all("div", class_="product-item")

product_data = []

for product in products:
    # --- Product Name & Link ---
    name_tag = product.find("a", class_="product-item__title")
    name = name_tag.get_text(strip=True) if name_tag else None
    link = f"https://beminimalist.co{name_tag['href']}" if name_tag and name_tag.has_attr("href") else None

    # --- Price ---
    price_section = product.find("div", class_="product-item__price text-size--small equalize-white-space")
    current_price, mrp = None, None
    if price_section:
        price_div = price_section.find("div", class_="product-price")
        if price_div:
            spans = price_div.find_all("span")
            if spans:
                current_price = spans[0].get_text(strip=True)
            del_tag = price_div.find("del")
            if del_tag:
                mrp = del_tag.get_text(strip=True)

    product_data.append({
        "Product Name": name,
        "Link": link,
        "Current Price": current_price,
        "MRP": mrp
    })

# -----------------------------
# Save to ..\Data
# -----------------------------
output_folder = r"..\Data"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "beminimalist_products_page_1.xlsx")

df = pd.DataFrame(product_data)
df.to_excel(output_file, index=False)

print(f"\n✅ Scraping Complete! Total {len(df)} products saved to {os.path.abspath(output_file)}")
