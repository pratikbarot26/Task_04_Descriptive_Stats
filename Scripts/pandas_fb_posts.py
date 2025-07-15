import pandas as pd
import sys
import time

OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pandas_output_fb_posts.txt"

NUMERIC_COLS = [
    'Total Interactions', 'Likes', 'Comments', 'Shares',
    'Love', 'Wow', 'Haha', 'Sad', 'Angry'
]

CATEGORICAL_COLS = [
    'Facebook_Id', 'Page Category', 'Page Admin Top Country',
    'Post Created', 'Post Created Time', 'Type', 'Video Share Status',
    'Is Video Owner?', 'Video Length'
]

class Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, msg): [s.write(msg) for s in self.streams]
    def flush(self): [s.flush() for s in self.streams]

def clean(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(",", "").str.replace("-", "").str.strip()
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass
    df.replace(["-", "None", "nan", ""], pd.NA, inplace=True)
    df.dropna(how="all", inplace=True)
    return df

def describe_categorical(df, col):
    df_col = df[col].dropna()
    print(f"\n{col} - Unique: {df_col.nunique()}")
    if not df_col.mode().empty:
        top_val = df_col.mode().iloc[0]
        top_count = df_col.value_counts().iloc[0]
        print(f"Top: {top_val} ({top_count})")
        print(df_col.value_counts().head(5))
    else:
        print("No values found.")

def describe(df, title):
    print(f"\n--- {title} ---")

    available_numeric = [col for col in NUMERIC_COLS if col in df.columns]
    if available_numeric:
        print("📊 Numeric Summary:")
        print(df[available_numeric].dropna().describe())
    else:
        print("No numeric columns found.")

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            describe_categorical(df, col)

if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    df = pd.read_csv("C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_posts_president_scored_anon.csv")
    df = clean(df)

    describe(df, "Overall Dataset Summary")

    if "Facebook_Id" in df.columns:
        for fid, group_df in df[df["Facebook_Id"].notna()].groupby("Facebook_Id"):
            describe(group_df, f"Group: Facebook_Id = {fid}")

    if all(col in df.columns for col in ["Facebook_Id", "Page Category"]):
        grouped = df.dropna(subset=["Facebook_Id", "Page Category"]).groupby(["Facebook_Id", "Page Category"])
        for (fid, cat), group_df in grouped:
            describe(group_df, f"Group: Facebook_Id = {fid}, Page Category = {cat}")

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
