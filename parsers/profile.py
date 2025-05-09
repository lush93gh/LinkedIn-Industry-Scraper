"""Playwright‑based discovery + profile extraction."""

from __future__ import annotations
import asyncio
import json
import logging
import random
import re
from pathlib import Path
from typing import AsyncGenerator, List

from pydantic import ValidationError
from playwright.async_api import async_playwright, Browser, Page

from config import settings
from models import ProfileData

logger = logging.getLogger(__name__)

PROFILE_URL_RE = re.compile(r"https://[a-z]{2,3}\.linkedin\.com/in/[A-Za-z0-9\-_%]+/?")

USER_AGENTS = [
    # Minimal embedded list; can be extended via settings.USER_AGENTS_FILE
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

if settings.USER_AGENTS_FILE and Path(settings.USER_AGENTS_FILE).exists():
    with open(settings.USER_AGENTS_FILE, "r", encoding="utf-8") as ua:
        USER_AGENTS.extend([l.strip() for l in ua if l.strip()])


class LinkedInScraper:
    def __init__(
        self,
        industry: str,
        max_profiles: int = 100,
        concurrency: int = 3,
        proxy: str | None = None,
        login_cookie: str | None = None,
        headless: bool = True,
    ) -> None:
        self.industry = industry
        self.max_profiles = max_profiles
        self.concurrency = concurrency
        self.proxy = proxy
        self.login_cookie = login_cookie
        self.headless = headless

        self._browser: Browser | None = None
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._visited: set[str] = set()

    async def _init_browser(self):
        pw = await async_playwright().start()
        launch_args = {
            "headless": self.headless,
        }
        if self.proxy:
            launch_args["proxy"] = {"server": self.proxy}
        self._browser = await pw.chromium.launch(**launch_args)

    async def _new_page(self) -> Page:
        assert self._browser, "Browser not initialised"
        ua = random.choice(USER_AGENTS)
        context = await self._browser.new_context(user_agent=ua)
        if self.login_cookie:
            context.add_cookies([json.loads(self.login_cookie)])
        page = await context.new_page()
        page.set_default_timeout(settings.PLAYWRIGHT_TIMEOUT)
        return page

    async def _discover_profiles(self):
        """Use LinkedIn public search to enqueue profile URLs."""
        page = await self._new_page()
        search_url = (
            "https://www.linkedin.com/search/results/people/?"
            f"industryCompanyVertical=({self.industry})"
        )
        await page.goto(search_url)
        last_height = 0
        while len(self._visited) < self.max_profiles:
            await page.wait_for_timeout(random.randint(1000, 3000))
            html = await page.content()
            for match in PROFILE_URL_RE.finditer(html):
                url = match.group(0).split("?")[0]
                if url not in self._visited:
                    self._visited.add(url)
                    await self._queue.put(url)
                    if len(self._visited) >= self.max_profiles:
                        break
            # scroll
            current_height = await page.evaluate("document.body.scrollHeight")
            if current_height == last_height:
                break
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            last_height = current_height
        await page.context.close()

    async def _worker(self) -> AsyncGenerator[ProfileData, None]:
        while True:
            url = await self._queue.get()
            if url is None:
                break
            try:
                profile = await self._parse_profile(url)
                if profile:
                    yield profile
            except Exception as exc:
                logger.exception("Error parsing %s: %s", url, exc)
            finally:
                self._queue.task_done()

    async def _parse_profile(self, url: str) -> ProfileData | None:
        page = await self._new_page()
        backoff = 1
        while True:
            try:
                await page.goto(url)
                await page.wait_for_selector("main")
                break
            except Exception as exc:
                logger.warning("Retrying %s due to %s", url, exc)
                await page.wait_for_timeout(backoff * 1000)
                backoff = min(backoff * 2, 32)
        html = await page.content()
        await page.context.close()
        # minimal JSON extraction using regex; in production use BeautifulSoup or DOM traversal
        data = {
            "id": url.rstrip("/").split("/")[-1],
            "Custom public profile URL": url,
            "Headline": _text_between(html, 'class="text-body-medium" >', "<"),
            "Pronouns": _text_between(html, "pronouns-text", "<"),
            "Industry": self.industry,
            "About (Summary)": _text_between(
                html, 'section class="artdeco-card p4"', "<"
            ),
            "Connections / Follower count": _int_between(
                html, "connections-and-followers-count", "<"
            ),
        }
        try:
            return ProfileData.parse_obj(data)
        except ValidationError as e:
            logger.debug("Validation failed for %s: %s", url, e)
            return None

    async def run(self) -> AsyncGenerator[ProfileData, None]:
        await self._init_browser()
        discover_task = asyncio.create_task(self._discover_profiles())
        workers = [self._worker() for _ in range(self.concurrency)]
        for coro in asyncio.as_completed(workers):
            async for profile in coro:
                yield profile
        await discover_task

    async def close(self):
        if self._browser:
            await self._browser.close()


def _text_between(haystack: str, left: str, right: str) -> str | None:
    try:
        return haystack.split(left, 1)[1].split(right, 1)[0].strip()
    except IndexError:
        return None


def _int_between(haystack: str, left: str, right: str) -> int | None:
    txt = _text_between(haystack, left, right)
    if txt and txt.isdigit():
        return int(txt)
    return None
