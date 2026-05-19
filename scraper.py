import asyncio
import json
import time
import random
import requests
from urllib.parse import urlencode

from config import BASE_HEADERS, BASE_PAYLOAD, COOKIES, DELAY_MIN, DELAY_MAX

ENDPOINT = "https://www.threads.com/graphql/query"

BASE_VARIABLES = {
    "sort_order": "TOP",
    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasPostAuthorNotifControlsrelayprovider": True,
    "__relay_internal__pv__BarcelonaShouldShowFediverseM1Featuresrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasInlineReplyComposerrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasDearAlgoConsumptionrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasEventBadgerelayprovider": False,
    "__relay_internal__pv__BarcelonaGenAIRepliesEnabledrelayprovider": False,
    "__relay_internal__pv__BarcelonaIsSearchDiscoveryEnabledrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasCommunitiesrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasGameScoreSharerelayprovider": True,
    "__relay_internal__pv__BarcelonaHasPublicViewCountCardrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasCommunityEntityCardrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasScorecardCommunityrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasMusicrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasNewspaperLinkStylerelayprovider": False,
    "__relay_internal__pv__BarcelonaHasMessagingrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasGhostPostEmojiActivationrelayprovider": False,
    "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasDearAlgoWebProductionrelayprovider": False,
    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasCommunityTopContributorsrelayprovider": False,
    "__relay_internal__pv__BarcelonaCanSeeSponsoredContentrelayprovider": False,
    "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider": False,
    "__relay_internal__pv__BarcelonaIsInternalUserrelayprovider": False,
}

# Tracks consecutive 403 responses across calls
_consecutive_403s = 0
_MAX_403_BEFORE_REFRESH = 3


def _parse_cookie_header(cookie_str: str) -> dict:
    """Parse a raw 'cookie' header string into a {name: value} dict."""
    result = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result


async def _attempt_token_capture(page, context) -> dict:
    """
    Navigate to threads.com, click the first post to trigger a
    /graphql/query POST, and capture tokens from the intercepted request.
    Returns a dict with lsd, csrftoken, x-csrftoken, x-bloks-version-id, mid.
    """
    tokens: dict = {}
    captured = asyncio.Event()

    async def handle_request(request):
        # Only intercept POST requests to the graphql endpoint
        if "/graphql/query" not in request.url:
            return
        if request.method.upper() != "POST":
            return
        if captured.is_set():
            return

        headers = request.headers

        # Parse tokens from the cookie header string
        cookie_str = headers.get("cookie", "")
        cookie_map = _parse_cookie_header(cookie_str)

        # Also grab browser-level cookies as fallback
        try:
            browser_cookies = await context.cookies("https://www.threads.com")
            for c in browser_cookies:
                cookie_map.setdefault(c["name"], c["value"])
        except Exception:
            pass

        # Extract lsd from POST body
        lsd_value = ""
        try:
            body = request.post_data or ""
            for part in body.split("&"):
                if part.startswith("lsd="):
                    from urllib.parse import unquote_plus
                    lsd_value = unquote_plus(part.split("=", 1)[1])
                    break
        except Exception:
            pass

        tokens.update({
            "lsd": lsd_value or cookie_map.get("lsd", ""),
            "csrftoken": cookie_map.get("csrftoken", ""),
            "x-csrftoken": headers.get("x-csrftoken", cookie_map.get("csrftoken", "")),
            "x-bloks-version-id": headers.get("x-bloks-version-id", ""),
            "mid": cookie_map.get("mid", ""),
        })
        captured.set()

    page.on("request", handle_request)

    await page.goto("https://www.threads.com", wait_until="networkidle", timeout=30_000)

    # Click the first post element to trigger a /graphql/query call
    for selector in ["article", "[role='article']", "a[href*='/post/']"]:
        try:
            el = page.locator(selector).first
            if await el.count() > 0:
                await el.click(timeout=5_000)
                break
        except Exception:
            pass

    # Wait up to 8 s for a graphql/query request
    try:
        await asyncio.wait_for(captured.wait(), timeout=8)
    except asyncio.TimeoutError:
        pass

    return tokens


async def refresh_tokens_from_browser() -> dict:
    """
    Launch headless Chromium, navigate to threads.com, intercept the first
    POST /graphql/query request, and extract fresh auth tokens.

    Retries up to 3 times (with page scroll between retries) until
    lsd and csrftoken are both non-empty.

    Returns a dict with keys: lsd, csrftoken, x-csrftoken, x-bloks-version-id, mid
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        tokens: dict = {}
        for attempt in range(1, 4):
            try:
                tokens = await _attempt_token_capture(page, context)
            except Exception:
                tokens = {}

            if tokens.get("lsd") and tokens.get("csrftoken"):
                break

            try:
                await page.keyboard.press("End")
                await asyncio.sleep(3)
            except Exception:
                pass

        await browser.close()

    return tokens


def _rebuild_session(tokens: dict) -> requests.Session:
    """
    Build a brand-new requests.Session with the freshly captured tokens
    merged into the base headers and cookies.
    """
    new_headers = {**BASE_HEADERS}
    if tokens.get("x-csrftoken"):
        new_headers["x-csrftoken"] = tokens["x-csrftoken"]
    if tokens.get("x-bloks-version-id"):
        new_headers["x-bloks-version-id"] = tokens["x-bloks-version-id"]

    new_cookies = {**COOKIES}
    if tokens.get("csrftoken"):
        new_cookies["csrftoken"] = tokens["csrftoken"]
    if tokens.get("mid"):
        new_cookies["mid"] = tokens["mid"]

    session = requests.Session()
    session.headers.update(new_headers)
    session.cookies.update(new_cookies)

    if tokens.get("lsd"):
        session._refreshed_lsd = tokens["lsd"]

    return session


def _make_session() -> requests.Session:
    """Create a session with base headers and cookies."""
    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    session.cookies.update(COOKIES)
    return session


def _sleep():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def shortcode_to_id(shortcode: str) -> str:
    """
    Convert a Threads/Instagram post shortcode to its numeric media ID.
    Uses the same base64-like alphabet Instagram uses.
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    n = 0
    for char in shortcode:
        n = n * 64 + alphabet.index(char)
    return str(n)


def fetch_post_replies(
    post_code: str,
    session: requests.Session = None,
    _session_ref: list = None,
) -> dict | None:
    """
    Fetch replies for a given post shortcode.

    Args:
        post_code:    Threads post shortcode (e.g. 'DYeZUeiElWy').
        session:      Active requests.Session (mutated on token refresh).
        _session_ref: Single-element list holding the session so main.py can
                      receive the rebuilt session after a token refresh.
    """
    global _consecutive_403s

    if session is None:
        session = _make_session()

    # Convert shortcode to numeric media ID required by the GraphQL API
    numeric_id = shortcode_to_id(post_code)

    # Allow a refreshed lsd to override the config value
    lsd_override = getattr(session, "_refreshed_lsd", None)
    payload_base = {**BASE_PAYLOAD}
    if lsd_override:
        payload_base["lsd"] = lsd_override

    variables = {**BASE_VARIABLES, "postID": numeric_id}
    payload = {
        **payload_base,
        "variables": json.dumps(variables, separators=(",", ":")),
    }

    try:
        resp = session.post(ENDPOINT, data=urlencode(payload), timeout=15)

        if resp.status_code == 200:
            _consecutive_403s = 0
            return resp.json()

        elif resp.status_code == 429:
            time.sleep(30)
            return None

        elif resp.status_code == 403:
            _consecutive_403s += 1

            if _consecutive_403s >= _MAX_403_BEFORE_REFRESH:
                print("[token refresh] Fetching fresh tokens...", flush=True)
                tokens = asyncio.run(refresh_tokens_from_browser())

                if tokens.get("lsd") and tokens.get("csrftoken"):
                    new_session = _rebuild_session(tokens)
                    if _session_ref is not None:
                        _session_ref[0] = new_session
                    session.headers.update(new_session.headers)
                    session.cookies.update(new_session.cookies)
                    if hasattr(new_session, "_refreshed_lsd"):
                        session._refreshed_lsd = new_session._refreshed_lsd

                    _consecutive_403s = 0

                    lsd_override2 = getattr(new_session, "_refreshed_lsd", None)
                    payload_base2 = {**BASE_PAYLOAD}
                    if lsd_override2:
                        payload_base2["lsd"] = lsd_override2
                    payload2 = {
                        **payload_base2,
                        "variables": json.dumps(variables, separators=(",", ":")),
                    }

                    try:
                        resp2 = new_session.post(ENDPOINT, data=urlencode(payload2), timeout=15)
                        if resp2.status_code == 200:
                            return resp2.json()
                    except Exception:
                        pass

            return None

        else:
            return None

    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None


def parse_replies(raw: dict, post_code: str, post_id: str, keyword: str) -> list[dict]:

    if raw is None or "data" not in raw:
        return []

    if "errors" in raw:
        return []

    rows = []

    try:
        # Use (x or {}) at every level so a None value never crashes .get()
        outer_data = (raw.get("data") or {})
        inner_data = (outer_data.get("data") or {})
        edges = inner_data.get("edges") or []

        for edge in (edges or []):
            if not isinstance(edge, dict):
                continue
            node = (edge.get("node") or {})
            thread_items = (node.get("thread_items") or [])

            for i, item in enumerate(thread_items or []):
                if not isinstance(item, dict):
                    continue
                post = (item.get("post") or {})
                if not post:
                    continue

                caption = (post.get("caption") or {})
                text = caption.get("text", "") if isinstance(caption, dict) else ""

                if not text:
                    tpa_raw = (post.get("text_post_app_info") or {})
                    tf_raw  = (tpa_raw.get("text_fragments") or {})
                    fragments = (tf_raw.get("fragments") or [])
                    text = " ".join(
                        f.get("plaintext", "") for f in (fragments or [])
                        if isinstance(f, dict) and f.get("plaintext")
                    )

                user     = (post.get("user") or {})
                tpa_info = (post.get("text_post_app_info") or {})

                row = {
                    "post_code":    post_code,  # original shortcode (e.g. DYeZUeiElWy)
                    "post_id":      post_id,    # numeric media ID
                    "post_text":    "",        # filled in main.py
                    "comment_id":   post.get("pk", ""),
                    "comment_text": text,
                    "username":     (user.get("username") or ""),
                    "like_count":   (post.get("like_count") or 0),
                    "reply_count":  (tpa_info.get("direct_reply_count") or 0),
                    "timestamp":    (post.get("taken_at") or ""),
                    "keyword":      keyword,
                    "type":         "reply" if i > 0 else "comment",
                }
                rows.append(row)

    except Exception:
        pass

    return rows


def get_post_reply_count(raw: dict) -> int:
    """Count total replies from a response payload."""
    try:
        outer = (raw.get("data") or {})
        inner = (outer.get("data") or {})
        edges = (inner.get("edges") or [])
        total = 0
        for edge in edges:
            node  = (edge.get("node") or {})
            items = (node.get("thread_items") or [])
            for item in items:
                post = (item.get("post") or {})
                tpa  = (post.get("text_post_app_info") or {})
                total += (tpa.get("direct_reply_count") or 0)
        return total
    except Exception:
        return 0