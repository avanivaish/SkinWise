# This script reads a list of products from an the product basic information excel, scrapes detailed information from each product page,
# and saves the enriched data back to a new Excel file. 
# 
# Specifically, for each product link, it extracts:
# - Description: Text under the "What Makes It Potent?" toggle
# - Skin Type and Concerns: Information under the "Ideal For" toggle
# - Instructions: Text under the "How to Use" toggle
# - Ingredients: Each ingredient's heading and description from the FAQ section
#
# The script uses:
# - requests + BeautifulSoup for HTML parsing
# - pandas for Excel reading and writing
# - Lists to collect each data column before adding them to the DataFrame


import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ----------------- Paths -----------------
cwd = os.getcwd()  # Current working directory: Web_Scrapying
input_excel = os.path.join(cwd, "..", "Data", "beminimalist_products.xlsx")
output_excel = os.path.join(cwd, "..", "Data", "beminimalist_products_detailed.xlsx")

# ----------------- Read Excel -----------------
df = pd.read_excel(input_excel)  # Expecting columns: Product Name, Link, Price, MRP

# ----------------- Prepare lists for new columns -----------------
descriptions = []
skin_types = []
concerns_list = []
instructions = []
ingredients_list = []

# ----------------- Scrape each product -----------------
for link in df['Link']:
    print(f"Scraping: {link}")
    try:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Failed to fetch {link}: {e}")
        descriptions.append("")
        skin_types.append("")
        concerns_list.append("")
        instructions.append("")
        ingredients_list.append("")
        continue

    # ------------- Description: "What makes it Potent?" -------------
    toggle_tabs = soup.find_all("toggle-tab", class_="toggle")

    description_text = ""
    for tab in toggle_tabs:
        title_span = tab.find("span", class_="toggle__title")
        if title_span and "what makes it potent?" in title_span.get_text(strip=True).lower():
            content_div = tab.find("div", class_="toggle__content")
            if content_div:
                ul = content_div.find("ul")
                if ul:
                    li_texts = [li.get_text(strip=True) for li in ul.find_all("li")]
                    description_text = " | ".join(li_texts)
            break
    descriptions.append(description_text)

    # ------------- Skin Type & Concerns: "Ideal For" -------------
    skin_type = ""
    concerns = ""

    for tab in toggle_tabs:
        title_span = tab.find("span", class_="toggle__title")
        if title_span and "Ideal For" in title_span.get_text(strip=True):
            content_div = tab.find("div", class_="toggle__content")
            if content_div:
                for p in content_div.find_all("p"):
                    strong_tag = p.find("strong")
                    if strong_tag:
                        label = strong_tag.get_text(strip=True).lower()  # lowercase for case-insensitive
                        value = strong_tag.next_sibling
                        if value:
                            value = value.strip(" :\u00a0")  # remove extra spaces, colon, non-breaking space
                            if "skin type" in label:
                                skin_type = value  # may stay empty if not present
                            elif "concerns" in label:
                                concerns = value
            break

    skin_types.append(skin_type)      # will be "" if missing
    concerns_list.append(concerns)    # will contain value if present


    # ------------- Instructions: "How to Use" -------------
    instruction_text = ""
    for tab in toggle_tabs:
        title_span = tab.find("span", class_="toggle__title")
        if title_span and "How to Use" in title_span.get_text(strip=True):
            content_div = tab.find("div", class_="toggle__content")
            if content_div:
                instruction_text = content_div.get_text(separator=" ", strip=True)
            break
    instructions.append(instruction_text)

    # ------------- Ingredients -------------
    ingredient_data = []
    faq_items = soup.find("div", class_="faq-items")
    if faq_items:
        faq_tabs = faq_items.find_all("toggle-tab")
        for faq in faq_tabs:
            heading = faq.find("span", class_="text-weight--bold")
            desc_span = faq.find("span", class_="metafield-multi_line_text_field")
            if heading and desc_span:
                ingredient_data.append(f"{heading.get_text(strip=True)}: {desc_span.get_text(strip=True)}")
    ingredients_list.append(" | ".join(ingredient_data))

# ----------------- Add scraped data to DataFrame -----------------
df['Description'] = descriptions
df['Skin Type'] = skin_types
df['Concerns'] = concerns_list
df['Instructions'] = instructions
df['Ingredients'] = ingredients_list

# ----------------- Save to Excel -----------------
df.to_excel(output_excel, index=False)
print(f"✅ Scraping completed and saved to {output_excel}")
