# ---------------------------------------------------------------------------
# Static configuration — all token values are fetched at runtime
# ---------------------------------------------------------------------------

DELAY_MIN = 2.0
DELAY_MAX = 5.0
OUTPUT_FILE = "output.csv"
CHECKPOINT_FILE = "checkpoint.json"
MIN_TEXT_LENGTH = 10  # minimum characters per comment

# HTTP headers — only values that never change between sessions
BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.5",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.threads.com",
    "referer": "https://www.threads.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "x-asbd-id": "359341",
    "x-fb-friendly-name": "BarcelonaPostPageDirectQuery",
    "x-ig-app-id": "238260118697367",
    "x-logged-out-threads-migrated-request": "true",
    "x-root-field-name": "xdt_api__v1__text_feed__media_id__replies__connection",
    # x-bloks-version-id and x-csrftoken are injected at runtime after token refresh
}

# GraphQL payload — only static fields (lsd and dynamic spin values injected at runtime)
BASE_PAYLOAD = {
    "av": "0",
    "__user": "0",
    "__a": "1",
    "dpr": "1",
    "__ccg": "EXCELLENT",
    "__spin_b": "trunk",
    "hl": "en",
    "fb_api_caller_class": "RelayModern",
    "fb_api_req_friendly_name": "BarcelonaPostPageDirectQuery",
    "server_timestamps": "true",
    "doc_id": "26739870295663957",
}

# Base cookies — csrftoken and mid are injected at runtime after token refresh
COOKIES: dict = {}
