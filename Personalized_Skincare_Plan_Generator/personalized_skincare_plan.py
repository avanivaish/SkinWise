"""
personalized_skincare_plan.py

This main application script generates a personalized AM/PM skincare routine for the user,
using Plum Goodness product data. The user is prompted to select skin type, skin concern,
and desired routine (morning, night, both) from options. It uses the suggest_active_ingredients
helper to recommend actives (ingredients), which then filter product recommendations to be most suitable
for the user. All column selections are robust and support "None" inputs (no filtering for that criteria).

Typical use: Run as main script after data preprocessing and cleaning.
"""

import pandas as pd
from suggest_active_ingredient import suggest_active_ingredients

DATA_PATH = r"..\Data\plumgoodness_products_cleaned.csv"

def load_product_data(path=DATA_PATH):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ Could not find {path}. Please ensure the CSV file exists in the directory.")
    if "Is_Combo" in df.columns:
        df = df[df["Is_Combo"] != True]
    return df

def match_text(text, keyword):
    if not keyword or keyword == "None":
        return True
    if pd.isna(text):
        return False
    return keyword.lower() in str(text).lower()

def categorize_product(name: str):
    name = name.lower()
    if "toner" in name:
        return "Toner"
    elif "cleanser" in name or "face wash" in name:
        return "Cleanser"
    elif "serum" in name:
        return "Serum"
    elif any(x in name for x in ["moisturizer", "cream", "gel"]):
        return "Moisturizer"
    elif "sunscreen" in name or "spf" in name:
        return "Sunscreen"
    else:
        return None

def generate_skincare_plan(df, skin_type, concern, routine="Both"):
    # Robust column selection
    desc_col_candidates = [col for col in df.columns if any(x in col for x in ["Ingredient", "Key", "Benefit", "Keyword"])]
    desc_col = desc_col_candidates[0] if desc_col_candidates else df.columns[0]

    actives = suggest_active_ingredients(df, skin_type, concern)
    print(f"\n🌟 Recommended actives for your skin (type: {skin_type}, concern: {concern}): {', '.join(actives) if actives else 'No specific actives found'}\n")

    # Filter for skin type if not None
    if skin_type != "None":
        filtered = df[
            df.apply(lambda row: match_text(row.get(desc_col, ""), skin_type) or match_text(row.get("Name", ""), skin_type), axis=1)
        ]
    else:
        filtered = df.copy()

    # Further filter for concern if not None
    if concern != "None":
        filtered = filtered[
            filtered.apply(lambda row: match_text(row.get(desc_col, ""), concern) or match_text(row.get("Name", ""), concern), axis=1)
        ]

    # Active ingredient filter if provided by suggestion
    if actives:
        filtered = filtered[
            filtered.apply(
                lambda row: any(active in str(row.get(desc_col, "")).lower() or active in str(row.get("Name", "")).lower() for active in actives), axis=1)
        ]

    if filtered.empty:
        return "😔 Sorry, no matching products found for your selection."

    filtered["Step"] = filtered["Name"].apply(categorize_product)
    filtered = filtered[filtered["Step"].notnull()]

    step_order = ["Toner", "Cleanser", "Serum", "Moisturizer", "Sunscreen"]
    filtered["Step"] = pd.Categorical(filtered["Step"], categories=step_order, ordered=True)
    filtered = filtered.sort_values("Step")

    steps_emoji = {"Toner": "🌸", "Cleanser": "💧", "Serum": "✨", "Moisturizer": "🪄", "Sunscreen": "🧴"}

    morning, night = [], []
    for _, row in filtered.iterrows():
        step = row["Step"]
        name = row["Name"]
        link = row.get("Link", "")
        desc = row.get(desc_col, "")
        short_desc = desc[:100].strip() + "..." if len(desc) > 100 else desc
        emoji = steps_emoji.get(step, "🔹")
        if step == "Sunscreen":
            morning.append(f"{emoji} **{step}:** [{name}]({link}) — {short_desc}")
        else:
            morning.append(f"{emoji} **{step}:** [{name}]({link}) — {short_desc}")
            night.append(f"{emoji} **{step}:** [{name}]({link}) — {short_desc}")

    output = ""
    if routine in ["Morning", "Both"]:
        output += "🌞 **Morning Routine**\n" + "\n".join(morning[:5]) + "\n\n"
    if routine in ["Night", "Both"]:
        output += "🌙 **Night Routine**\n" + "\n".join(night[:4]) + "\n\n"
    return output if output.strip() else "No matching products found for your inputs."

if __name__ == "__main__":
    skin_types = ['Oily', 'Dry', 'Normal', 'Sensitive', 'None']
    concern_types = ['Acne', 'Spots', 'Pigmentation', 'Tan', 'Hydration', 'Blemish', 'Aging', 'Pores', 'None']
    routines = ['Morning', 'Night', 'Both']

    print("Choose your skin type:")
    for i, s in enumerate(skin_types, 1):
        print(f"{i}. {s}")
    skin_type = skin_types[int(input("Enter number for skin type: ").strip()) - 1]

    print("\nChoose your main skin concern:")
    for i, c in enumerate(concern_types, 1):
        print(f"{i}. {c}")
    concern = concern_types[int(input("Enter number for concern: ").strip()) - 1]

    print("\nChoose your skincare routine:")
    for i, r in enumerate(routines, 1):
        print(f"{i}. {r}")
    routine = routines[int(input("Enter number for routine: ").strip()) - 1]

    print("🧠 Loading product data and generating your skincare plan...\n")
    df = load_product_data()
    plan = generate_skincare_plan(df=df, skin_type=skin_type, concern=concern, routine=routine)
    print("💆 Personalized Skincare Plan\n---------------------------")
    print(plan)
