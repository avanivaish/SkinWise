import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://plumgoodness.com/collections/skincare?page={}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

data = []
page = 1

while True:
    url = BASE_URL.format(page)
    print(f"Scraping page {page} -> {url}")
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    products = soup.find_all("li", class_="js-pagination-result")
    if not products:
        print("No products found — stopping.")
        break

    for product in products:
        card = product.find("product-card", class_="card card--product h-full card--product-contained relative flex")
        if not card:
            continue

        rating_div = card.find("div", class_="rating inline-block align-middle")
        rating = rating_div.get("aria-label", "").strip() if rating_div else "N/A"

        reviews_div = card.find("div", class_="rating__count")
        reviews = reviews_div.get_text(strip=True) if reviews_div else "N/A"

        name_tag = card.find("p", class_="card__title")
        product_name = name_tag.get_text(strip=True) if name_tag else "N/A"

        link_tag = name_tag.find("a") if name_tag else None
        product_link = "https://plumgoodness.com" + link_tag.get("href") if link_tag else "N/A"

        desc_tag = card.find("p", class_="text-sm text-current mb-1")
        keywords = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        skin_type_div = card.find("div", class_="product-type")
        skin_type = (
            skin_type_div.find("span").get_text(strip=True)
            if skin_type_div and skin_type_div.find("span")
            else "N/A"
        )

        price_tag = card.find("strong", class_="price__current")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        mrp_tag = card.find("s", class_="price__was")
        mrp = mrp_tag.get_text(strip=True) if mrp_tag else "N/A"

        data.append({
            "Name": product_name,
            "Link": product_link,
            "Rating": rating,
            "Reviews": reviews,
            "Keywords": keywords,
            "Skin Type": skin_type,
            "Price": price,
            "MRP": mrp
        })

    print(f"✅ Page {page}: {len(products)} products scraped.")
    page += 1
    time.sleep(1)

print(f"\nTotal scraped: {len(data)}")

df = pd.DataFrame(data)
df.to_excel("plumgoodness_products.xlsx", index=False)
print("💾 Data saved to plumgoodness_products.xlsx")
