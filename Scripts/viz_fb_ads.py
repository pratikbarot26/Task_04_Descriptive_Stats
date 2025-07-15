import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

FILE_PATH = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_ads_president_scored_anon.csv"
OUTPUT_DIR = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/plots_fb_ads"

NUMERIC_COLS = [
    'estimated_audience_size',
    'estimated_impressions',
    'estimated_spend'
]

def clean(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(",", "").str.replace("-", "").str.strip()
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df

def plot_numeric(df):
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].dropna().notna().any():
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f"Distribution of {col}")
            plt.savefig(f"{OUTPUT_DIR}/hist_{col}.png")
            plt.clf()

            sns.boxplot(x=df[col].dropna())
            plt.title(f"Boxplot of {col}")
            plt.savefig(f"{OUTPUT_DIR}/box_{col}.png")
            plt.clf()

def plot_top_binary_flags(df):
    binary_flags = [col for col in df.columns if df[col].dropna().isin([0, 1]).all() and col not in NUMERIC_COLS]
    if binary_flags:
        flag_sums = df[binary_flags].sum().sort_values(ascending=False).head(10)
        sns.barplot(x=flag_sums.values, y=flag_sums.index)
        plt.title("Top 10 Binary Flags (Sum=1's)")
        plt.xlabel("Count of 1's")
        plt.savefig(f"{OUTPUT_DIR}/binary_flag_summary.png")
        plt.clf()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(FILE_PATH)
    df = clean(df)

    plot_numeric(df)
    plot_top_binary_flags(df)

    print(f"✅ Visualizations saved to ./{OUTPUT_DIR}/")