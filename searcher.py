import asyncio
import json
import random
import re

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from config import DELAY_MIN, DELAY_MAX


def _extract_codes_from_json(body: str) -> list[str]:
    """
    Pull post shortcodes out of a raw JSON response body that contains
    'thread_items' or 'edges'.  Looks for 'code' fields on post objects.
    """
    codes = []
    try:
        data = json.loads(body)
    except Exception:
        return codes

    def walk(obj):
        if isinstance(obj, dict):
            # A post object typically has both 'pk' (numeric) and 'code' (shortcode)
            if "code" in obj and isinstance(obj["code"], str) and len(obj["code"]) > 5:
                code = obj["code"]
                if code not in codes:
                    codes.append(code)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return codes


async def search_post_ids(keyword: str, max_posts: int = 100) -> list[str]:

    if not PLAYWRIGHT_AVAILABLE:
        return []

    post_ids: list[str] = []
    api_codes: list[str] = []  # codes captured from intercepted GraphQL responses

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
            locale="id-ID",
        )
        page = await context.new_page()

        # Intercept GraphQL search responses to extract codes directly from API
        async def handle_response(response):
            try:
                if "graphql" not in response.url:
                    return
                if response.status != 200:
                    return
                body = await response.text()
                if "thread_items" not in body and "edges" not in body:
                    return
                for code in _extract_codes_from_json(body):
                    if code not in api_codes:
                        api_codes.append(code)
            except Exception:
                pass

        page.on("response", handle_response)

        search_url = (
            f"https://www.threads.com/search"
            f"?q={keyword.replace(' ', '+')}&serp_type=default"
        )

        try:
            await page.goto(search_url, wait_until="networkidle", timeout=30_000)

            # Aggressive scroll loop: up to 10 passes, stop early if count stalls
            prev_count = 0
            stall_streak = 0
            for _ in range(10):
                if len(post_ids) >= max_posts:
                    break

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(1.5, 2.5))

                hrefs = await page.eval_on_selector_all(
                    "a[href*='/post/']",
                    "els => els.map(e => e.href)"
                )
                for href in hrefs:
                    match = re.search(r"/post/([A-Za-z0-9_-]+)", href)
                    if match:
                        code = match.group(1)
                        if code not in post_ids:
                            post_ids.append(code)
                    if len(post_ids) >= max_posts:
                        break

                if len(post_ids) == prev_count:
                    stall_streak += 1
                    if stall_streak >= 3:
                        break  # no new results loading
                else:
                    stall_streak = 0
                prev_count = len(post_ids)

        except Exception:
            pass

        finally:
            await browser.close()

    # Merge API-intercepted codes as fallback when DOM scraping yields < 5
    if len(post_ids) < 5:
        for code in api_codes:
            if code not in post_ids:
                post_ids.append(code)
            if len(post_ids) >= max_posts:
                break

    return post_ids[:max_posts]


def search_post_ids_sync(keyword: str, max_posts: int = 100) -> list[str]:
    return asyncio.run(search_post_ids(keyword, max_posts))