# -----------------------------------------------------------------------------------
# This script scrapes product data from the "Skin & Body" collection on the 
# beminimalist.co website. It automatically traverses all available pages in the
# collection and extracts the following details for each product:
# - Product Name
# - Product Link
# - Current Price
# - MRP (Original Price)
#
# Notes:
# - Ratings and reviews are skipped because they are dynamically loaded (Yotpo widget)
# - A polite delay of 1 second is added between page requests to avoid overloading the server
# - The scraped data is saved to an Excel file at the relative path ..\Data\beminimalist_products.xlsx
# -----------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# -----------------------------
# Configuration
# -----------------------------
BASE_URL = "https://beminimalist.co/collections/skin-body-1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
PARAMS = {
    "filter.p.m.my_fields.category": "Skin",
    "sort_by": "title-ascending"
}

OUTPUT_FOLDER = r"..\Data"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "beminimalist_products.xlsx")

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# Function to extract products from a page
# -----------------------------
def extract_products_from_page(soup):
    product_grid = soup.find("div", id="main-collection-product-grid")
    if not product_grid:
        return []

    products = product_grid.find_all("div", class_="product-item")
    page_data = []

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

        # --- Ratings skipped ---
        page_data.append({
            "Product Name": name,
            "Link": link,
            "Current Price": current_price,
            "MRP": mrp
        })

    return page_data

# -----------------------------
# Main Scraper Loop
# -----------------------------
all_products = []
page = 1

while True:
    print(f"🔄 Scraping page {page}...")
    PARAMS["page"] = page
    response = requests.get(BASE_URL, headers=HEADERS, params=PARAMS)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page {page}, status code: {response.status_code}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    products_on_page = extract_products_from_page(soup)

    if not products_on_page:
        print("✅ No more products found. Finished scraping.")
        break

    all_products.extend(products_on_page)
    print(f"✅ Page {page}: {len(products_on_page)} products scraped.")
    page += 1
    time.sleep(1)  # polite delay

# -----------------------------
# Save to Excel
# -----------------------------
df = pd.DataFrame(all_products)
df.to_excel(OUTPUT_FILE, index=False)
print(f"\n🎉 Scraping Complete! Total {len(df)} products saved to {OUTPUT_FILE}")
