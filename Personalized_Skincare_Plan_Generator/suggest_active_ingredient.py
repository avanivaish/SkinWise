"""
suggest_active_ingredient.py

This helper script provides a function to automatically suggest suitable skincare active ingredients for a user,
based on their selected skin type and main concern. It scans ingredient, benefit, and keyword columns in a cleaned
product dataset, and recommends actives most suitable for the user's needs. Can be run standalone for actives suggestion,
or imported into other scripts for integrated use.

Typical use: Called by a main skincare plan generator script, which then uses actives for product recommendations.
"""

import pandas as pd

def suggest_active_ingredients(df, skin_type, concern):
    # Robustly pick a usable column for actives search
    desc_col_candidates = [col for col in df.columns if any(x in col for x in ["Ingredient", "Key", "Benefit", "Keyword"])]
    desc_col = desc_col_candidates[0] if desc_col_candidates else df.columns[0]

    filtered = df.copy()
    if skin_type != "None":
        filtered = filtered[
            filtered.apply(lambda row: skin_type.lower() in str(row.get(desc_col, "")).lower() or skin_type.lower() in str(row.get("Name", "")).lower(), axis=1)
        ]
    if concern != "None":
        filtered = filtered[
            filtered.apply(lambda row: concern.lower() in str(row.get(desc_col, "")).lower() or concern.lower() in str(row.get("Name", "")).lower(), axis=1)
        ]

    popular_actives = ["niacinamide", "vitamin c", "aha", "bha", "retinol", "hyaluronic", "ceramide", "salicylic", "azelaic", "glycolic"]
    found_actives = set()
    for v in filtered[desc_col].dropna():
        for active in popular_actives:
            if active in v.lower():
                found_actives.add(active)
    return list(found_actives)

if __name__ == "__main__":
    DATA_PATH = r"..\Data\plumgoodness_products_cleaned.csv"
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ Could not find {DATA_PATH}. Please ensure the CSV file exists.")

    skin_types = ['Oily', 'Dry', 'Normal', 'Sensitive', 'None']
    concern_types = ['Acne', 'Spots', 'Pigmentation', 'Tan', 'Hydration', 'Blemish', 'Aging', 'Pores', 'None']

    print("Choose your skin type:")
    for i, s in enumerate(skin_types, 1):
        print(f"{i}. {s}")
    skin_type = skin_types[int(input("Enter number for skin type: ").strip()) - 1]

    print("\nChoose your main skin concern:")
    for i, c in enumerate(concern_types, 1):
        print(f"{i}. {c}")
    concern = concern_types[int(input("Enter number for concern: ").strip()) - 1]

    actives = suggest_active_ingredients(df, skin_type, concern)
    print(f"\n🌟 Recommended actives for {skin_type} skin & {concern}: {', '.join(actives) if actives else 'No specific actives found'}")
