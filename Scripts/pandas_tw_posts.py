import pandas as pd
import numpy as np
from collections import Counter
import time

# File paths
INPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_tw_posts_president_scored_anon.csv"
OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pandas_output_tw_posts.txt"

# Columns
NUMERIC_COLS = [
    'retweetCount', 'replyCount', 'likeCount', 'quoteCount',
    'viewCount', 'bookmarkCount', 'z'
]

CATEGORICAL_COLS = [
    'id', 'url', 'source', 'createdAt', 'lang', 'quoteId',
    'inReplyToId', 'month_year', 'illuminating_scored_message'
]

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

GROUP_BY = ['source', 'lang']

def summarize_numeric(df):
    df = df[[col for col in NUMERIC_COLS if col in df.columns]]
    df = df.apply(pd.to_numeric, errors='coerce')
    stats = df.describe(percentiles=[0.25, 0.5, 0.75]).T
    stats['null_count'] = df.isnull().sum()
    stats = stats[['count', 'null_count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    stats = stats.round(2)
    return stats.T  # transpose the output

def summarize_categorical(df):
    output = {}
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue
        vc = df[col].value_counts(dropna=True)
        top_val = vc.index[0] if not vc.empty else None
        output[col] = {
            "unique": df[col].nunique(dropna=True),
            "top": top_val,
            "top_count": vc.iloc[0] if not vc.empty else 0,
            "top_5": vc.head(5).to_dict()
        }
    return output

def summarize_binary(df):
    output = {}
    for col in BINARY_COLS:
        if col not in df.columns:
            continue
        ones = df[col].fillna(0).astype(int).sum()
        zeros = (df[col].fillna(0) == 0).astype(int).sum()
        output[col] = {'1s': int(ones), '0s': int(zeros)}
    return output

def print_summary(title, df, f):
    print(f"\n--- {title} ---")
    f.write(f"\n--- {title} ---\n")

    # Numeric Summary
    print("\n Numeric Summary:\n")
    f.write("\n Numeric Summary:\n\n")
    num_summary = summarize_numeric(df)
    print(num_summary.to_string())
    f.write(num_summary.to_string() + "\n")

    # Categorical Summary
    print()
    f.write("\n")
    for col, stat in summarize_categorical(df).items():
        header = f"{col} - Unique: {stat['unique']}, Top: {stat['top']} ({stat['top_count']})"
        print(header)
        f.write(header + "\n")
        print("Top 5 values:")
        f.write("Top 5 values:\n")
        for k, v in stat['top_5'].items():
            line = f"{k} - {v}"
            print(line)
            f.write(line + "\n")
        print()
        f.write("\n")

    # Binary Flag Summary
    print("Binary Flag Summary:\n")
    f.write("Binary Flag Summary:\n\n")
    for col, counts in summarize_binary(df).items():
        line = f"{col}: 1s = {counts['1s']}, 0s = {counts['0s']}"
        print(line)
        f.write(line + "\n")

# Main execution
if __name__ == "__main__":
    start_time = time.perf_counter()

    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    df = pd.read_csv(INPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        print_summary("Overall Summary", df, f)
        for name, group in df.groupby(GROUP_BY):
            title = f"Group: {GROUP_BY[0]} = {name[0]}, {GROUP_BY[1]} = {name[1]}"
            print_summary(title, group, f)

        end_time = time.perf_counter()
        f.write(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds\n")
        
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
