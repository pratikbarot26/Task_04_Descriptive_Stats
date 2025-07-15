import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File paths
FILE_PATH = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_tw_posts_president_scored_anon.csv"
OUTPUT_DIR = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/plots_tw_posts"

# Define column categories
NUMERIC_COLS = [
    'retweetCount', 'replyCount', 'likeCount', 'quoteCount',
    'viewCount', 'bookmarkCount', 'z', 'illuminating_scored_message'
]

# These are the known binary dummy columns
BINARY_COLS = [
    'election_integrity_Truth_illuminating', 'advocacy_msg_type_illuminating',
    'issue_msg_type_illuminating', 'attack_msg_type_illuminating',
    'image_msg_type_illuminating', 'cta_msg_type_illuminating',
    'engagement_cta_subtype_illuminating', 'fundraising_cta_subtype_illuminating',
    'voting_cta_subtype_illuminating', 'covid_topic_illuminating',
    'economy_topic_illuminating', 'education_topic_illuminating',
    'environment_topic_illuminating', 'foreign_policy_topic_illuminating',
    'governance_topic_illuminating', 'health_topic_illuminating',
    'immigration_topic_illuminating', 'lgbtq_issues_topic_illuminating',
    'military_topic_illuminating', 'race_and_ethnicity_topic_illuminating',
    'safety_topic_illuminating', 'social_and_cultural_topic_illuminating',
    'technology_and_privacy_topic_illuminating', 'womens_issue_topic_illuminating',
    'incivility_illuminating', 'scam_illuminating', 'freefair_illuminating',
    'fraud_illuminating', 'isRetweet', 'isQuote', 'isConversationControlled', 'z'
]

def clean_dataframe(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(",", "", regex=False).str.replace("-", "", regex=False).str.strip()
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception:
            continue
    return df

def plot_numeric(df):
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].dropna().notna().any():
            plt.figure(figsize=(6, 4))
            sns.histplot(df[col].dropna(), kde=True, bins=30)
            plt.title(f"Distribution of {col}")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/hist_{col}.png")
            plt.clf()

            plt.figure(figsize=(6, 4))
            sns.boxplot(x=df[col].dropna())
            plt.title(f"Boxplot of {col}")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/box_{col}.png")
            plt.clf()

def plot_binary_flags(df):
    valid_flags = [col for col in BINARY_COLS if col in df.columns and df[col].dropna().isin([0, 1]).all()]
    if valid_flags:
        flag_sums = df[valid_flags].sum().sort_values(ascending=False).head(10)
        plt.figure(figsize=(8, 5))
        sns.barplot(x=flag_sums.values, y=flag_sums.index)
        plt.title("Top 10 Binary Flags (Sum=1's)")
        plt.xlabel("Count of 1's")
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/binary_flags_summary.png")
        plt.clf()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(FILE_PATH)
    df = clean_dataframe(df)

    plot_numeric(df)
    plot_binary_flags(df)

    print(f"✅ Twitter post visualizations saved to {OUTPUT_DIR}")
