import csv
import math
from collections import defaultdict, Counter
import sys
import time

OUTPUT_FILE = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Outputs/pure_python_output_fb_posts.txt"
NUMERIC_COLS = [
    'Total Interactions', 'Likes', 'Comments', 'Shares',
    'Love', 'Wow', 'Haha', 'Sad', 'Angry'
]

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for s in self.streams:
            s.write(message)

    def flush(self):
        for s in self.streams:
            s.flush()

def load_csv(filepath):
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def try_parse_float(val):
    try:
        return float(val.replace(",", "").replace("-", "").strip())
    except:
        return None

def identify_types(rows):
    types = {}
    for col in rows[0]:
        types[col] = "numeric" if col in NUMERIC_COLS else "categorical"
    return types

def compute_stats(rows, types):
    stats = {}
    for col in types:
        values = [row[col].strip() for row in rows if row.get(col, "").strip() not in ("", "-", "None", "nan")]
        if types[col] == "numeric":
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
        else:
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
        key = tuple(row.get(k, "").strip() for k in keys)
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

    filepath = "C:/Users/Pratik/Desktop/Syracuse_Research/Task_04/Datasets/2024_fb_posts_president_scored_anon.csv"
    data = load_csv(filepath)
    col_types = identify_types(data)

    print_summary("Overall Summary", compute_stats(data, col_types))
    print_summary("Grouped by Facebook_Id", group_by_stats(data, col_types, ["Facebook_Id"]))
    print_summary("Grouped by Facebook_Id and Page Category", group_by_stats(data, col_types, ["Facebook_Id", "Page Category"]))

    end_time = time.perf_counter()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
