import csv
import json
import os

FIELDNAMES = [
    "post_code",   # original shortcode (e.g. DYeZUeiElWy)
    "post_id",     # numeric media ID
    "post_text",
    "comment_id",
    "comment_text",
    "username",
    "like_count",
    "reply_count",
    "timestamp",
    "keyword",
    "type",        # "comment" or "reply"
]


def save_to_csv(rows: list, filename: str):
    if not rows:
        return
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def save_checkpoint(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_checkpoint(filename: str) -> dict:
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "scraped_posts": [],
        "total_comments": 0,
        "failed_posts": [],
    }


def count_csv_rows(filename: str) -> int:
    """Return the number of data rows already saved in the CSV."""
    if not os.path.exists(filename):
        return 0
    with open(filename, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1