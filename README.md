# threadscraper

> A keyword-based CLI scraper for Threads comments and replies — no account required.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![PyPI](https://img.shields.io/pypi/v/threads-scraper)

---

## Features

- **Keyword search** — search Threads by any keyword and collect all matching comments and replies
- **No account required** — session tokens are fetched automatically via headless browser on first run
- **Auto token refresh** — detects expired tokens after 3 consecutive 403s and silently refreshes via headless Chromium
- **Text cleaning** — removes URLs, @mentions, #hashtags, emoji, and normalizes whitespace
- **Deduplication** — skips posts already scraped, tracked across restarts via checkpoint file
- **Resume support** — interrupted scrapes continue from where they left off
- **Configurable via CLI** — limit, output file, delay range, minimum comment length, checkpoint toggle
- **CSV output** with columns: `post_code`, `post_id`, `post_text`, `comment_id`, `comment_text`, `username`, `like_count`, `reply_count`, `timestamp`, `keyword`, `type`

---

## Installation

```bash
pip install threads-scraper
playwright install chromium
```

---

## Usage

```bash
# Scrape by inline keywords
threads-scraper --keywords "politik indonesia,pilkada"

# Use a keywords file
threads-scraper --keywords-file keywords.txt

# With all options
threads-scraper --keywords-file keywords.txt \
  --output data.csv \
  --limit 5000 \
  --delay-min 2 \
  --delay-max 5 \
  --min-length 15
```

---

## keywords.txt format

Lines starting with `#` are treated as comments and ignored.

```
# Politik
politik indonesia
pilkada

# Ekonomi
ekonomi indonesia
bbm naik
```

---

## CLI reference

| Argument | Default | Description |
|---|---|---|
| `--keywords` | — | Comma-separated keyword string |
| `--keywords-file` | — | Path to `.txt` file, one keyword per line |
| `--limit` | unlimited | Maximum total comments to collect |
| `--output` | `output.csv` | Output CSV file path |
| `--min-length` | `10` | Minimum character count per comment |
| `--delay-min` | `2.0` | Minimum seconds between requests |
| `--delay-max` | `5.0` | Maximum seconds between requests |
| `--no-checkpoint` | off | Disable resume behavior (start fresh) |

---

## Output CSV columns

| Column | Description |
|---|---|
| `post_code` | Original post shortcode from the URL (e.g. `DYeZUeiElWy`) |
| `post_id` | Numeric media ID used by the GraphQL API |
| `post_text` | Text of the top-level post being replied to |
| `comment_id` | Numeric ID of the comment or reply |
| `comment_text` | Cleaned comment/reply text |
| `username` | Poster's Threads username |
| `like_count` | Number of likes on the comment |
| `reply_count` | Number of direct replies to the comment |
| `timestamp` | Unix timestamp of the comment |
| `keyword` | The search keyword that found this post |
| `type` | `comment` (top-level) or `reply` |

---

## Notes

- For **educational and research purposes only**
- Respect Threads' [Terms of Service](https://help.instagram.com/581066165581870)
- Use reasonable delays (`--delay-min`, `--delay-max`) to avoid overloading servers
- The first run launches a headless browser to capture fresh session tokens — this is normal and takes ~10 seconds

---

## Credit

Made by [@galihkjaya](https://github.com/galihkjaya)
