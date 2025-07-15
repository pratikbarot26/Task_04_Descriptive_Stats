import csv
import math
from collections import defaultdict, Counter
import sys
import re
import time

INPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_tw_posts_president_scored_anon.csv"
OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pure_python_output_tw_posts.txt"

NUMERIC_COLS = [
    'retweetCount', 'replyCount', 'likeCount', 'quoteCount',
    'viewCount', 'bookmarkCount', 'illuminating_scored_message'
]

CATEGORICAL_COLS = [
    'id', 'url', 'source', 'createdAt', 'lang',
    'quoteId', 'inReplyToId', 'month_year'
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

GROUP_BY_1 = "source"
GROUP_BY_2 = ("source", "lang")


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


def load_csv(filepath):
    with open(filepath, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def try_parse_float(val):
    try:
        return float(val.replace(",", "").replace("-", "").strip())
    except:
        return None


def summarize_column(colname, values):
    summary = {
        'count': len(values),
        'unique_values': len(set(values))
    }

    if colname in NUMERIC_COLS:
        nums = [try_parse_float(v) for v in values if try_parse_float(v) is not None]
        if nums:
            mean = sum(nums) / len(nums)
            std = math.sqrt(sum((x - mean) ** 2 for x in nums) / len(nums)) if len(nums) > 1 else 0
            summary.update({
                'min': min(nums),
                'max': max(nums),
                'mean': round(mean, 2),
                'std_dev': round(std, 2)
            })

    elif colname in BINARY_COLS:
        ones = values.count('1') + values.count('True') + values.count('true')
        zeros = values.count('0') + values.count('False') + values.count('false')
        summary.update({'1s': ones, '0s': zeros})

    elif colname in CATEGORICAL_COLS:
        counter = Counter(values)
        if counter:
            top_val, top_count = counter.most_common(1)[0]
            summary.update({
                'most_common_value': top_val,
                'most_common_count': top_count
            })

    return summary


def compute_overall_summary(data):
    all_cols = NUMERIC_COLS + CATEGORICAL_COLS + BINARY_COLS
    summary = {}
    for col in all_cols:
        col_values = [row.get(col, "").strip() for row in data if row.get(col) and row[col].strip().lower() not in ("", "nan", "none")]
        if col_values:
            summary[col] = summarize_column(col, col_values)
    return summary


def group_by_stats(rows, keys):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row.get(k, "").strip() for k in keys)
        if all(k not in ("", "nan", "-", None) for k in key):
            grouped[key].append(row)

    grouped_summaries = {}
    for k, group_rows in grouped.items():
        grouped_summaries[k] = compute_overall_summary(group_rows)
    return grouped_summaries


def print_summary(title, summary_dict):
    print(f"\n--- {title} ---")
    for col, stats in summary_dict.items():
        print(f"{col}: {stats}")


if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    data = load_csv(INPUT_FILE)

    overall = compute_overall_summary(data)
    print_summary("Overall Summary", overall)

    for key, group_stats in group_by_stats(data, [GROUP_BY_1]).items():
        print_summary(f"Group: {GROUP_BY_1} = {key[0]}", group_stats)

    for key, group_stats in group_by_stats(data, list(GROUP_BY_2)).items():
        print_summary(f"Group: {GROUP_BY_2[0]} = {key[0]}, {GROUP_BY_2[1]} = {key[1]}", group_stats)

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
