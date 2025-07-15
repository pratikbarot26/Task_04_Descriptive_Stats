import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Constants
FILE_PATH = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_posts_president_scored_anon.csv"
NUMERIC_COLS = [
    'Total Interactions', 'Likes', 'Comments', 'Shares',
    'Love', 'Wow', 'Haha', 'Sad', 'Angry'
]
CATEGORICAL_COLS = ['Page Category', 'Type']
OUTPUT_DIR = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/plots_fb_posts"

def clean_dataframe(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(",", "", regex=False)
            df[col] = df[col].str.replace("-", "", regex=False)
            df[col] = df[col].str.strip()
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

def create_numeric_visuals(df):
    for col in NUMERIC_COLS:
        if col in df.columns:
            plt.figure(figsize=(6, 4))
            sns.histplot(df[col].dropna(), kde=True, bins=30)
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/hist_{col}.png")
            plt.close()

            plt.figure(figsize=(6, 4))
            sns.boxplot(x=df[col].dropna())
            plt.title(f"Boxplot of {col}")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/box_{col}.png")
            plt.close()

def create_categorical_visuals(df):
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            plt.figure(figsize=(8, 4))
            sns.countplot(data=df, x=col, order=df[col].value_counts().iloc[:10].index)
            plt.title(f"Top 10 Most Frequent in {col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/bar_{col}.png")
            plt.close()

if __name__ == "__main__":
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load and clean data
    df = pd.read_csv(FILE_PATH)
    df = clean_dataframe(df)

    # Generate plots
    create_numeric_visuals(df)
    create_categorical_visuals(df)

    print(f"✅ All visualizations saved to ./{OUTPUT_DIR}/")
