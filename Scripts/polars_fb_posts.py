import polars as pl
import sys
import re
import time

OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/polars_output_fb_posts.txt"

NUMERIC_COLS = [
    'Total Interactions', 'Likes', 'Comments', 'Shares',
    'Love', 'Wow', 'Haha', 'Sad', 'Angry'
]

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

def clean(df: pl.DataFrame) -> pl.DataFrame:
    # Clean string columns
    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            df = df.with_columns([
                pl.col(col)
                .str.replace_all(",", "")
                .str.replace_all("-", "")
                .str.strip_chars()
                .alias(col)
            ])
    
    # Only cast numeric columns to Float64
    for col in NUMERIC_COLS:
        if col in df.columns:
            try:
                df = df.with_columns(pl.col(col).cast(pl.Float64).alias(col))
            except:
                pass

    # Drop nulls only in numeric columns
    df = df.drop_nulls(subset=NUMERIC_COLS)

    return df

def describe(df: pl.DataFrame, title: str):
    print(f"\n--- {title} ---")

    numeric_cols = [col for col in NUMERIC_COLS if col in df.columns]
    if numeric_cols:
        try:
            print("📊 Numeric Summary:")
            print(df.select(numeric_cols).drop_nulls().describe())
        except Exception as e:
            print(f"Numeric summary failed: {e}")
    else:
        print("No numeric columns found.")

    string_cols = [col for col in df.columns if df[col].dtype == pl.Utf8]
    for col in string_cols:
        try:
            # Clean column values
            col_df = df.select(
                pl.col(col)
                .cast(pl.Utf8)
                .str.strip_chars()
                .str.replace_all(",", "")
                .str.replace_all("-", "")
                .alias(col)
            ).drop_nulls()

            col_df = col_df.filter(pl.col(col).str.len_chars() > 0)

            if col_df.is_empty():
                continue  # ⛳ skip analysis for empty column

            nunique = col_df[col].n_unique()
            mode_series = col_df[col].mode()
            topval = mode_series[0] if mode_series.shape[0] > 0 else "N/A"
            topcount = col_df[col].value_counts().sort("count", descending=True).row(0)[1] if mode_series.shape[0] > 0 else 0

            print(f"\n{col} - Unique: {nunique}, Top: {topval} ({topcount})")

            freq = (
                col_df[col]
                .value_counts()
                .sort(by=["count", col], descending=[True, False])
                .head(5)
            )

            print("Top 5 values:")
            for val, count in freq.rows():
                print(f"{val} - {count}")

        except Exception as e:
            print(f"Failed to summarize {col}: {e}")

if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    df = pl.read_csv("C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_posts_president_scored_anon.csv")
    df = clean(df)

    describe(df, "Overall Dataset Summary")

    if "Facebook_Id" in df.columns:
        for fid in df["Facebook_Id"].unique().drop_nulls().to_list():
            group_df = df.filter(pl.col("Facebook_Id") == fid)
            describe(group_df, f"Group: Facebook_Id = {fid}")

    if all(col in df.columns for col in ["Facebook_Id", "Page Category"]):
        pairs = df.select(["Facebook_Id", "Page Category"]).drop_nulls().unique()
        for row in pairs.iter_rows(named=True):
            group_df = df.filter(
                (pl.col("Facebook_Id") == row["Facebook_Id"]) &
                (pl.col("Page Category") == row["Page Category"])
            )
            describe(group_df, f"Group: Facebook_Id = {row['Facebook_Id']}, Page Category = {row['Page Category']}")

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
