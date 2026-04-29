"""Tests for crawler behaviour."""

from __future__ import annotations

from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from src.crawler import WebsiteCrawler


def test_extract_text_collects_quote_author_and_tags() -> None:
    html = """
    <html>
      <body>
        <div class="quote">
          <span class="text">"A quote"</span>
          <small class="author">Author Name</small>
          <div class="tags">
            <a class="tag">life</a>
            <a class="tag">truth</a>
          </div>
        </div>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    text = WebsiteCrawler.extract_text(soup)

    assert "A quote" in text
    assert "Author Name" in text
    assert "life truth" in text


def test_extract_links_only_returns_internal_normalised_links() -> None:
    html = """
    <html>
      <body>
        <a href="/page/2/">Page 2</a>
        <a href="https://quotes.toscrape.com/author/Albert-Einstein">Author</a>
        <a href="https://example.com/">External</a>
        <a href="#fragment">Fragment</a>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    crawler = WebsiteCrawler()

    links = list(crawler.extract_links(soup, "https://quotes.toscrape.com/"))

    assert links == [
        "https://quotes.toscrape.com/author/Albert-Einstein/",
        "https://quotes.toscrape.com/page/2/",
    ]


def test_extract_links_filters_non_http_and_query_variants() -> None:
    html = """
    <html>
      <body>
        <a href="mailto:test@example.com">Mail</a>
        <a href="javascript:void(0)">JS</a>
        <a href="/tag/life?page=2#top">Tag</a>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    crawler = WebsiteCrawler()

    links = list(crawler.extract_links(soup, "https://quotes.toscrape.com/"))

    assert links == ["https://quotes.toscrape.com/tag/life/"]


@patch("src.crawler.time.sleep")
@patch("src.crawler.time.time")
def test_fetch_page_respects_politeness_window(
    mock_time: Mock,
    mock_sleep: Mock,
) -> None:
    response = Mock()
    response.text = "<html></html>"
    response.headers = {"Content-Type": "text/html; charset=utf-8"}
    response.raise_for_status.return_value = None

    session = Mock()
    session.get.return_value = response

    crawler = WebsiteCrawler(session=session, delay_seconds=6)
    crawler._last_request_time = 100.0
    mock_time.return_value = 103.0

    crawler.fetch_page("https://quotes.toscrape.com/")

    mock_sleep.assert_called_once_with(3.0)
    session.get.assert_called_once()


def test_fetch_page_returns_none_on_request_failure() -> None:
    session = Mock()
    session.get.side_effect = requests.RequestException("boom")
    crawler = WebsiteCrawler(session=session)

    result = crawler.fetch_page("https://quotes.toscrape.com/")

    assert result is None


def test_fetch_page_returns_none_for_non_html_response() -> None:
    response = Mock()
    response.text = "binary"
    response.headers = {"Content-Type": "image/png"}
    response.raise_for_status.return_value = None

    session = Mock()
    session.get.return_value = response

    crawler = WebsiteCrawler(session=session)

    assert crawler.fetch_page("https://quotes.toscrape.com/image.png") is None


def test_is_crawlable_url_only_accepts_quote_listing_pages() -> None:
    crawler = WebsiteCrawler()

    assert crawler.is_crawlable_url("https://quotes.toscrape.com/")
    assert crawler.is_crawlable_url("https://quotes.toscrape.com/page/2/")
    assert not crawler.is_crawlable_url("https://quotes.toscrape.com/tag/love/")
    assert not crawler.is_crawlable_url(
        "https://quotes.toscrape.com/author/Albert-Einstein/"
    )
