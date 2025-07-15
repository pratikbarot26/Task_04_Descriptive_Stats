import csv
import math
from collections import defaultdict, Counter
import sys
import ast
import time

OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pure_python_output_fb_ads.txt"

NUMERIC_COLS = [
    'estimated_audience_size', 'estimated_impressions', 'estimated_spend',
    'delivery_region_total_spend', 'delivery_region_total_impressions',
    'demo_dist_total_spend', 'demo_dist_total_impressions', 'mention_count'
]

DUMMY_SUFFIX = '_illuminating'
PLATFORM_LIST = ['facebook', 'instagram', 'messenger', 'audience_network']

class Tee:
    def __init__(self, *streams):
        self.streams = streams
        self.cleaner = None

    def write(self, message):
        for s in self.streams:
            s.write(message)

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

def safe_parse_dict(val):
    try:
        return ast.literal_eval(val)
    except:
        return {}

def safe_parse_list(val):
    try:
        return ast.literal_eval(val)
    except:
        return []

def preprocess_row(row):
    # Parse delivery_by_region
    delivery = safe_parse_dict(row.get("delivery_by_region", "{}"))
    row["delivery_region_total_spend"] = sum(v.get("spend", 0) for v in delivery.values())
    row["delivery_region_total_impressions"] = sum(v.get("impressions", 0) for v in delivery.values())

    # Parse demographic_distribution
    demo = safe_parse_dict(row.get("demographic_distribution", "{}"))
    row["demo_dist_total_spend"] = sum(v.get("spend", 0) for v in demo.values())
    row["demo_dist_total_impressions"] = sum(v.get("impressions", 0) for v in demo.values())

    # Parse estimated fields
    for col in ['estimated_audience_size', 'estimated_impressions', 'estimated_spend']:
        row[col] = str(row.get(col, "")).strip()

    # Parse publisher_platforms
    platforms = safe_parse_list(row.get("publisher_platforms", "[]"))
    for platform in PLATFORM_LIST:
        row[f"is_{platform}"] = "1" if platform in platforms else "0"

    # Parse illuminating_mentions
    mentions = safe_parse_list(row.get("illuminating_mentions", "[]"))
    row["mention_count"] = len(mentions)
    row["first_mention"] = mentions[0] if mentions else "None"

    return row

def load_csv(filepath):
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [preprocess_row(row) for row in reader]

def identify_types(rows):
    first_row = rows[0]
    types = {}
    for col in first_row:
        if col in NUMERIC_COLS:
            types[col] = "numeric"
        elif col.endswith(DUMMY_SUFFIX) or col.startswith("is_"):
            types[col] = "dummy"
        else:
            types[col] = "categorical"
    return types

def compute_stats(rows, types):
    stats = {}
    for col, typ in types.items():
        values = [str(row[col]).strip() for row in rows if str(row.get(col, "")).strip() not in ("", "-", "None", "nan")]
        if typ == "numeric":
            nums = [try_parse_float(v) for v in values if try_parse_float(v) is not None]
            if not nums:
                stats[col] = {"count": 0}
                continue
            count = len(nums)
            mean = sum(nums) / count
            std_dev = math.sqrt(sum((x - mean) ** 2 for x in nums) / count)
            stats[col] = {
                "count": count,
                "mean": round(mean, 2),
                "min": min(nums),
                "max": max(nums),
                "std_dev": round(std_dev, 2)
            }

        elif typ == "dummy":
            ones = sum(1 for v in values if v == "1")
            zeros = sum(1 for v in values if v == "0")
            stats[col] = {
                "count": len(values),
                "1s": ones,
                "0s": zeros,
                "percent_1s": round(100 * ones / len(values), 2) if values else 0.0
            }

        elif typ == "categorical":
            freq = Counter(values)
            most_common = freq.most_common(1)[0] if freq else ("N/A", 0)
            stats[col] = {
                "count": len(values),
                "unique_values": len(freq),
                "most_common_value": most_common[0],
                "most_common_count": most_common[1]
            }
    return stats

def group_by_stats(rows, types, keys):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(str(row.get(k, "")).strip() for k in keys)
        if all(k not in ("", "-", "None", "nan") for k in key):
            grouped[key].append(row)
    return {k: compute_stats(v, types) for k, v in grouped.items()}

def print_summary(title, summary):
    print(f"\n--- {title} ---")
    for col, val in summary.items():
        print(f"{col}: {val}")

if __name__ == "__main__":
    start_time = time.perf_counter()

    sys.stdout = Tee(sys.__stdout__, open(OUTPUT_FILE, "w", encoding="utf-8"))

    filepath = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_ads_president_scored_anon.csv"
    data = load_csv(filepath)
    col_types = identify_types(data)

    print_summary("Overall Summary", compute_stats(data, col_types))
    print_summary("Grouped by page_id", group_by_stats(data, col_types, ["page_id"]))
    print_summary("Grouped by page_id, bylines, and currency", group_by_stats(data, col_types, ["page_id", "bylines", "currency"]))

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
