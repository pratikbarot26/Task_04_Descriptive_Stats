import pandas as pd
import numpy as np
import ast
import sys
import warnings
import time

# ---- CONFIG ----
INPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_ads_president_scored_anon.csv"
OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pandas_output_fb_ads.txt"
pd.set_option('display.float_format', '{:,.0f}'.format)
warnings.simplefilter(action='ignore', category=FutureWarning)

# ---- BASE NUMERIC COLUMNS ----
ALL_POTENTIAL_NUMERIC = [
    "estimated_audience_size", "estimated_impressions", "estimated_spend",
    "delivery_region_total_impressions", "demo_dist_total_spend",
    "demo_dist_total_impressions", "mention_count"
]

# ---- TEE OUTPUT ----
class Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, msg): [s.write(msg) for s in self.streams]
    def flush(self): [s.flush() for s in self.streams]

# ---- PARSE HELPERS ----
def parse_nested_dict_column(col_data):
    try:
        return ast.literal_eval(col_data) if pd.notna(col_data) and col_data.strip().startswith("{") else {}
    except:
        return {}

def parse_nested_list_column(col_data):
    try:
        return ast.literal_eval(col_data) if pd.notna(col_data) and col_data.strip().startswith("[") else []
    except:
        return []

# ---- CLEANING FUNCTION ----
def clean(df):
    for col in ["estimated_audience_size", "estimated_impressions", "estimated_spend"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["delivery_region_total_impressions"] = df["delivery_by_region"].apply(
        lambda x: sum(v.get("impressions", 0) for v in parse_nested_dict_column(x).values())
    )
    df["demo_dist_total_spend"] = df["demographic_distribution"].apply(
        lambda x: sum(v.get("spend", 0) for v in parse_nested_dict_column(x).values())
    )
    df["demo_dist_total_impressions"] = df["demographic_distribution"].apply(
        lambda x: sum(v.get("impressions", 0) for v in parse_nested_dict_column(x).values())
    )
    df["mention_count"] = df["illuminating_mentions"].apply(
        lambda x: len(parse_nested_list_column(x))
    )
    return df

# ---- DESCRIPTIVE SUMMARY ----
def describe(df, title):
    print(f"\n--- {title} ---")

    # NUMERIC SUMMARY (Transposed)
    excluded = [col for col in df.columns if col.endswith("_illuminating")]
    numeric_cols = [col for col in ALL_POTENTIAL_NUMERIC if col in df.columns and col not in excluded]

    if numeric_cols:
        print("📊 Numeric Summary:")
        summary = df[numeric_cols].describe(percentiles=[.25, .5, .75])
        summary.loc["null_count"] = df[numeric_cols].isnull().sum()
        summary = summary.T  # Transpose
        print(summary.applymap(lambda x: f"{x:,.0f}" if pd.notnull(x) else "NaN"))

    # CATEGORICAL SUMMARY
    categorical_cols = df.select_dtypes(include="object").columns
    for col in categorical_cols:
        if col in excluded:
            continue
        non_null = df[col].dropna().astype(str)
        if non_null.empty:
            continue
        vc = non_null.value_counts()
        top_val = vc.index[0]
        top_count = vc.iloc[0]
        print(f"\n{col} - Unique: {non_null.nunique()}")
        print(f"Top: {top_val} ({top_count})")
        print(vc.head(5).to_string(name="count"))

# ---- MAIN EXECUTION ----
if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    df = pd.read_csv(INPUT_FILE, dtype=str, low_memory=False)
    df = clean(df)

    describe(df, "Overall Summary")

    for pid, group_df in df.groupby("page_id"):
        describe(group_df, f"Group: page_id = {pid}")

    for keys, group_df in df.groupby(["page_id", "bylines", "currency"]):
        pid, bylines, currency = keys
        describe(group_df, f"Group: page_id = {pid}, bylines = {bylines}, currency = {currency}")

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")