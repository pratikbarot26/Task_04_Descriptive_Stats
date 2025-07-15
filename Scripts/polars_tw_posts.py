import polars as pl
import sys
import re
import time

# File paths
INPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_tw_posts_president_scored_anon.csv"
OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/polars_output_tw_posts.txt"

# Column classifications
NUMERIC_COLS = [
    'retweetCount', 'replyCount', 'likeCount', 'quoteCount',
    'viewCount', 'bookmarkCount', 'z'
]

CATEGORICAL_COLS = [
    'id', 'url', 'source', 'createdAt', 'lang',
    'quoteId', 'inReplyToId', 'month_year', 'illuminating_scored_message'
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
    'fraud_illuminating', 'isRetweet', 'isQuote', 'isConversationControlled'
]

GROUP_BY = ['source', 'lang']

# Tee class for clean dual output
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

# Summary functions
def summarize_numeric(df):
    numeric_df = df.select([pl.col(c).cast(pl.Float64) for c in NUMERIC_COLS if c in df.columns])
    stats = numeric_df.describe()
    print(" Numeric Summary:")
    print(stats)

def summarize_categorical(df):
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue
        try:
            vc = df.select(pl.col(col)).drop_nulls().to_series().value_counts().sort("count", descending=True)
            unique = vc.shape[0]
            top_val = vc[0, 0]
            top_count = vc[0, 1]
            print(f"{col} - Unique: {unique}, Top: {top_val} ({top_count})")
            print("Top 5 values:")
            for i in range(min(5, unique)):
                print(f"{vc[i, 0]} - {vc[i, 1]}")
            print("")
        except Exception as e:
            print(f"⚠️ Failed to summarize {col}: {e}")

def print_summary(title, df):
    print(f"\n--- {title} ---")
    summarize_numeric(df)
    print("")
    summarize_categorical(df)

# Main
if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    df = pl.read_csv(INPUT_FILE)

    # Overall summary
    print_summary("Overall Summary", df)

    # Get group keys using .agg()
    group_keys = df.group_by(GROUP_BY).agg(pl.count()).select(GROUP_BY).rows()

    for source_val, lang_val in group_keys:
        group_df = df.filter(
            (pl.col(GROUP_BY[0]) == source_val) & (pl.col(GROUP_BY[1]) == lang_val)
        )
        label = f"Group: {GROUP_BY[0]} = {source_val}, {GROUP_BY[1]} = {lang_val}"
        print_summary(label, group_df)

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
