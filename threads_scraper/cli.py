import argparse
import asyncio
import random
import sys
import time

from threads_scraper.config import DELAY_MIN, DELAY_MAX, MIN_TEXT_LENGTH, OUTPUT_FILE, CHECKPOINT_FILE
from threads_scraper.scraper import (
    fetch_post_replies,
    parse_replies,
    _make_session,
    refresh_tokens_from_browser,
    _rebuild_session,
    shortcode_to_id,
)
from threads_scraper.searcher import search_post_ids_sync
from threads_scraper.cleaner import clean_text, is_valid
from threads_scraper.storage import save_to_csv, save_checkpoint, load_checkpoint, count_csv_rows

BANNER = "Credit: @galihkjaya | FOR EDUCATIONAL PURPOSE ONLY!"


def _load_keywords(args: argparse.Namespace) -> list[str]:
    keywords: list[str] = []

    if args.keywords:
        keywords += [k.strip() for k in args.keywords.split(",") if k.strip()]

    if args.keywords_file:
        with open(args.keywords_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    keywords.append(line)

    return keywords


def main():
    print(BANNER, flush=True)

    parser = argparse.ArgumentParser(
        prog="threads-scraper",
        description="Scrape comments and replies from Threads by keyword.",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        metavar="KEYWORD,...",
        help="Comma-separated list of search keywords.",
    )
    parser.add_argument(
        "--keywords-file",
        type=str,
        metavar="FILE",
        help="Path to a .txt file with one keyword per line (lines starting with # are ignored).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Maximum total comments to collect (default: unlimited).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=OUTPUT_FILE,
        metavar="FILE",
        help=f"Output CSV file path (default: {OUTPUT_FILE}).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=MIN_TEXT_LENGTH,
        metavar="N",
        help=f"Minimum character count per comment (default: {MIN_TEXT_LENGTH}).",
    )
    parser.add_argument(
        "--delay-min",
        type=float,
        default=DELAY_MIN,
        metavar="SEC",
        help=f"Minimum delay between requests in seconds (default: {DELAY_MIN}).",
    )
    parser.add_argument(
        "--delay-max",
        type=float,
        default=DELAY_MAX,
        metavar="SEC",
        help=f"Maximum delay between requests in seconds (default: {DELAY_MAX}).",
    )
    parser.add_argument(
        "--no-checkpoint",
        action="store_true",
        help="Disable checkpoint/resume behavior (start fresh every run).",
    )

    args = parser.parse_args()

    keywords = _load_keywords(args)
    if not keywords:
        parser.print_usage()
        print("error: provide --keywords or --keywords-file", file=sys.stderr)
        sys.exit(1)

    # Fetch fresh session tokens once at startup
    print("Fetching session tokens...", flush=True)
    tokens = asyncio.run(refresh_tokens_from_browser())
    if tokens.get("lsd") and tokens.get("csrftoken"):
        session_ref = [_rebuild_session(tokens)]
    else:
        session_ref = [_make_session()]
    print("Ready.", flush=True)

    output_file = args.output
    checkpoint_file = None if args.no_checkpoint else CHECKPOINT_FILE

    if args.no_checkpoint:
        scraped_posts: set = set()
        failed_posts: set = set()
        total = 0
    else:
        checkpoint = load_checkpoint(checkpoint_file)
        scraped_posts = set(checkpoint["scraped_posts"])
        failed_posts = set(checkpoint.get("failed_posts", []))
        total = count_csv_rows(output_file)

    target = args.limit

    for keyword in keywords:
        if target is not None and total >= target:
            break

        post_codes = search_post_ids_sync(keyword, max_posts=100)

        if not post_codes:
            continue

        for code in post_codes:
            if target is not None and total >= target:
                break

            if code in scraped_posts or code in failed_posts:
                continue

            print(f"\r[{total} comments] {keyword} -> {code}    ", end="", flush=True)
            time.sleep(random.uniform(args.delay_min, args.delay_max))

            raw = fetch_post_replies(code, session_ref[0], _session_ref=session_ref)

            if raw is None:
                failed_posts.add(code)
                if checkpoint_file:
                    save_checkpoint({
                        "scraped_posts": list(scraped_posts),
                        "total_comments": total,
                        "failed_posts": list(failed_posts),
                    }, checkpoint_file)
                continue

            rows = parse_replies(
                raw,
                post_code=code,
                post_id=shortcode_to_id(code),
                keyword=keyword,
            )

            if not rows:
                failed_posts.add(code)
                continue

            post_text = rows[0]["comment_text"] if rows else ""

            valid_rows = []
            for row in rows:
                row["post_text"] = post_text
                row["comment_text"] = clean_text(row["comment_text"])

                if not is_valid(row["comment_text"], min_length=args.min_length):
                    continue

                valid_rows.append(row)

            if len(valid_rows) < 2:
                failed_posts.add(code)
                continue

            save_to_csv(valid_rows, output_file)
            scraped_posts.add(code)
            total += len(valid_rows)

            if checkpoint_file:
                save_checkpoint({
                    "scraped_posts": list(scraped_posts),
                    "total_comments": total,
                    "failed_posts": list(failed_posts),
                }, checkpoint_file)

            print(f"\r[{total} comments] {keyword} -> {code}    ", end="", flush=True)

    print(f"\nDone. {total} comments saved to {output_file}", flush=True)
