import pandas as pd

df = pd.read_csv("data/raw/neo_2025.csv", parse_dates=["approach_date"])
# parse_dates tells pandas to treat that column as actual dates, not plain text —
# that matters because you can't do "group by month" math on text.

df["avg_diameter_km"] = (df["est_diameter_min_km"] + df["est_diameter_max_km"]) / 2
df["approach_month"] = df["approach_date"].dt.to_period("M").astype(str)

def size_bucket(diameter):
    if diameter < 0.05:
        return "small"
    elif diameter < 0.2:
        return "medium"
    return "large"

df["size_category"] = df["avg_diameter_km"].apply(size_bucket)
df = df.drop_duplicates(subset=["id", "approach_date"])

df.to_csv("data/processed/neo_clean.csv", index=False)
print(f"Cleaned dataset: {len(df)} rows.")