"""Web crawler for the quotes.toscrape.com coursework website."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_BASE_URL = "https://quotes.toscrape.com/"
REQUEST_TIMEOUT = 10
POLITENESS_DELAY_SECONDS = 6
DEFAULT_USER_AGENT = "quotes-search-coursework-bot/1.0"
QUOTE_PAGE_PATTERN = re.compile(r"^/page/\d+/$")


@dataclass
class CrawledPage:
    """Represents the extracted content for a crawled page."""

    url: str
    title: str
    text: str


@dataclass
class CrawlReport:
    """Stores crawl results and diagnostics for build-time reporting."""

    pages: list[CrawledPage]
    visited_urls: list[str]
    skipped_urls: list[str]
    failed_urls: list[str]


class WebsiteCrawler:
    """Crawls internal pages while respecting a politeness delay."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        delay_seconds: int = POLITENESS_DELAY_SECONDS,
        timeout: int = REQUEST_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.session = session or requests.Session()
        self._last_request_time: float | None = None
        self._base_domain = urlparse(self.base_url).netloc
        self.session.headers.setdefault("User-Agent", DEFAULT_USER_AGENT)

    def crawl(self) -> list[CrawledPage]:
        """Backwards-compatible helper returning only crawled pages."""
        return self.crawl_with_report().pages

    def crawl_with_report(self) -> CrawlReport:
        """Breadth-first crawl across quote listing pages for the searchable corpus."""
        queue: deque[str] = deque([self.base_url])
        visited: set[str] = set()
        queued: set[str] = {self.base_url}
        pages: list[CrawledPage] = []
        skipped_urls: list[str] = []
        failed_urls: list[str] = []

        while queue:
            url = queue.popleft()
            if url in visited:
                continue

            visited.add(url)
            html = self.fetch_page(url)
            if html is None:
                failed_urls.append(url)
                continue

            soup = BeautifulSoup(html, "html.parser")
            text = self.extract_text(soup)
            title = self.extract_title(soup)
            pages.append(CrawledPage(url=url, title=title, text=text))

            for link in self.extract_links(soup, current_url=url):
                if link in visited or link in queued:
                    continue
                if not self.is_crawlable_url(link):
                    skipped_urls.append(link)
                    continue
                queued.add(link)
                queue.append(link)

        return CrawlReport(
            pages=pages,
            visited_urls=sorted(visited),
            skipped_urls=sorted(set(skipped_urls)),
            failed_urls=sorted(set(failed_urls)),
        )

    def fetch_page(self, url: str) -> str | None:
        """Fetch a page while respecting the minimum delay between requests."""
        self._wait_if_needed()
        try:
            response = self.session.get(url, timeout=self.timeout)
            self._last_request_time = time.time()
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
                return None
        except requests.RequestException:
            return None
        return response.text

    def _wait_if_needed(self) -> None:
        if self._last_request_time is None:
            return

        elapsed = time.time() - self._last_request_time
        remaining = self.delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> Iterable[str]:
        """Return normalised internal links for later crawling."""
        discovered: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href or href.startswith("#"):
                continue
            if href.startswith(("mailto:", "javascript:", "tel:")):
                continue

            absolute_url = urljoin(current_url, href)
            normalised_url = self.normalise_url(absolute_url)
            if normalised_url is None:
                continue
            discovered.add(normalised_url)

        return sorted(discovered)

    def normalise_url(self, url: str) -> str | None:
        """Canonicalise a URL so duplicate links collapse to one entry."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None
        if parsed.netloc != self._base_domain:
            return None

        cleaned = parsed._replace(fragment="", query="")
        path = cleaned.path or "/"
        if path != "/" and not path.endswith("/"):
            path = f"{path}/"
        cleaned = cleaned._replace(path=path)
        return cleaned.geturl()

    def is_crawlable_url(self, url: str) -> bool:
        """Restrict crawling to the canonical quote-listing pages."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        if parsed.netloc != self._base_domain:
            return False
        return path == "/" or bool(QUOTE_PAGE_PATTERN.fullmatch(path))

    @staticmethod
    def extract_title(soup: BeautifulSoup) -> str:
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        return title or "Untitled page"

    @staticmethod
    def extract_text(soup: BeautifulSoup) -> str:
        """Extract visible quote-centric page text for indexing."""
        text_parts: list[str] = []

        quote_blocks = soup.select(".quote")
        for block in quote_blocks:
            quote_text = block.select_one(".text")
            author = block.select_one(".author")
            tags = [tag.get_text(" ", strip=True) for tag in block.select(".tags .tag")]

            if quote_text:
                text_parts.append(quote_text.get_text(" ", strip=True))
            if author:
                text_parts.append(author.get_text(" ", strip=True))
            if tags:
                text_parts.append(" ".join(tags))

        author_details = soup.select_one(".author-details")
        if author_details:
            text_parts.append(author_details.get_text(" ", strip=True))

        if not text_parts:
            text_parts.append(soup.get_text(" ", strip=True))

        return " ".join(part for part in text_parts if part).strip()
