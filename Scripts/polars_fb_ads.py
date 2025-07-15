import polars as pl
import ast
import sys
import re
import time

OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/polars_output_fb_ads.txt"

NUMERIC_COLS = [
    'estimated_audience_size', 'estimated_impressions', 'estimated_spend',
    'delivery_region_total_spend', 'delivery_region_total_impressions',
    'demo_dist_total_spend', 'demo_dist_total_impressions', 'mention_count'
]

PLATFORMS = ['facebook', 'instagram', 'messenger', 'audience_network']

class Tee:
    def __init__(self, *streams):
        self.streams = streams
        self.cleaner = re.compile(r"[^\x00-\x7F]")

    def write(self, msg):
        clean_msg = self.cleaner.sub("", msg)
        for s in self.streams:
            s.write(clean_msg)

    def flush(self):
        for s in self.streams:
            s.flush()

def try_parse_float(val):
    try:
        if isinstance(val, (int, float)):
            return float(val)
        if "-" in val:
            parts = list(map(float, val.split("-")))
            return sum(parts) / len(parts)
        return float(val.replace(",", "").replace("-", "").strip())
    except:
        return None

def parse_dict(col):
    return col.cast(str).map_elements(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith("{") else {},
        return_dtype=pl.Object
    )

def parse_list(col):
    return col.cast(str).map_elements(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith("[") else [],
        return_dtype=pl.Object
    )

def preprocess(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        pl.col("estimated_audience_size").cast(str).map_elements(try_parse_float, return_dtype=pl.Float64),
        pl.col("estimated_impressions").cast(str).map_elements(try_parse_float, return_dtype=pl.Float64),
        pl.col("estimated_spend").cast(str).map_elements(try_parse_float, return_dtype=pl.Float64)
    ])

    df = df.with_columns([
        parse_dict(pl.col("delivery_by_region")).alias("delivery_dict"),
        parse_dict(pl.col("demographic_distribution")).alias("demo_dict"),
        parse_list(pl.col("publisher_platforms")).alias("platforms"),
        parse_list(pl.col("illuminating_mentions")).alias("mentions")
    ])

    df = df.with_columns([
        pl.col("delivery_dict").map_elements(lambda d: sum(v.get("spend", 0) for v in d.values()), return_dtype=pl.Float64).alias("delivery_region_total_spend"),
        pl.col("delivery_dict").map_elements(lambda d: sum(v.get("impressions", 0) for v in d.values()), return_dtype=pl.Float64).alias("delivery_region_total_impressions"),
        pl.col("demo_dict").map_elements(lambda d: sum(v.get("spend", 0) for v in d.values()), return_dtype=pl.Float64).alias("demo_dist_total_spend"),
        pl.col("demo_dict").map_elements(lambda d: sum(v.get("impressions", 0) for v in d.values()), return_dtype=pl.Float64).alias("demo_dist_total_impressions"),
        pl.col("mentions").map_elements(lambda x: len(x) if isinstance(x, list) else 0, return_dtype=pl.Int64).alias("mention_count"),
        pl.col("mentions").map_elements(lambda x: x[0] if isinstance(x, list) and x else "None", return_dtype=pl.Utf8).alias("first_mention")
    ])

    for platform in PLATFORMS:
        df = df.with_columns(
            (pl.col("platforms").map_elements(lambda x: platform in x if isinstance(x, list) else False, return_dtype=pl.Boolean)).cast(pl.Utf8).alias(f"is_{platform}")
        )

    return df

def describe(df: pl.DataFrame, title: str):
    print(f"\n--- {title} ---")

    numeric_cols = [col for col in NUMERIC_COLS if col in df.columns]
    if numeric_cols:
        print("📊 Numeric Summary:")
        print(df.select(numeric_cols).drop_nulls().describe())

    string_cols = [col for col in df.columns if df[col].dtype == pl.Utf8]
    for col in string_cols:
        col_df = df.select(col).drop_nulls()
        if col_df.is_empty():
            print(f"\n{col} - No non-null values.")
            continue
        nunique = col_df[col].n_unique()
        mode = col_df[col].mode()
        top = mode[0] if mode.shape[0] > 0 else "N/A"
        topcount = col_df[col].value_counts().sort("count", descending=True).row(0)[1] if mode.shape[0] > 0 else 0
        print(f"\n{col} - Unique: {nunique}, Top: {top} ({topcount})")
        freq = (
            col_df[col]
            .value_counts()
            .sort(by=["count", col], descending=[True, False])
            .head(5)
        )
        print("Top 5 values:")
        for row in freq.rows():
            print(f"{row[0]} - {row[1]}")

if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    df = pl.read_csv("C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_ads_president_scored_anon.csv")
    df = preprocess(df)

    describe(df, "Overall Summary")

    if "page_id" in df.columns:
        for pid in df["page_id"].unique().drop_nulls().to_list():
            group_df = df.filter(pl.col("page_id") == pid)
            describe(group_df, f"Group: page_id = {pid}")

    if all(col in df.columns for col in ["page_id", "bylines", "currency"]):
        pairs = df.select(["page_id", "bylines", "currency"]).drop_nulls().unique()
        for row in pairs.rows(named=True):
            group_df = df.filter(
                (pl.col("page_id") == row["page_id"]) &
                (pl.col("bylines") == row["bylines"]) &
                (pl.col("currency") == row["currency"])
            )
            describe(group_df, f"Group: page_id = {row['page_id']}, bylines = {row['bylines']}, currency = {row['currency']}")

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
