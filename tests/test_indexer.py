"""Tests for inverted index construction."""

from __future__ import annotations

from src.crawler import CrawledPage
from src.indexer import InvertedIndexer


def test_tokenize_lowercases_and_extracts_words() -> None:
    tokens = InvertedIndexer.tokenize("Good friends, GOOD choices.")
    assert tokens == ["good", "friends", "good", "choices"]


def test_build_index_records_frequency_and_positions() -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/page/1/",
            title="Page 1",
            text="Good friends good books",
        )
    ]

    index_data = InvertedIndexer().build_index(pages)
    good_postings = index_data["index"]["good"]["https://quotes.toscrape.com/page/1/"]

    assert good_postings["frequency"] == 2
    assert good_postings["positions"] == [0, 2]
    assert index_data["pages"]["https://quotes.toscrape.com/page/1/"]["word_count"] == 4
    assert index_data["pages"]["https://quotes.toscrape.com/page/1/"]["unique_word_count"] == 3
    assert index_data["metadata"]["total_pages"] == 1
    assert index_data["metadata"]["total_terms"] == 3
    assert index_data["metadata"]["total_tokens"] == 4


def test_build_index_handles_empty_text() -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/page/empty/",
            title="Empty",
            text="",
        )
    ]

    index_data = InvertedIndexer().build_index(pages)

    assert index_data["pages"]["https://quotes.toscrape.com/page/empty/"]["word_count"] == 0
    assert index_data["index"] == {}


def test_save_and_load_index_round_trip(tmp_path) -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/page/1/",
            title="Page 1",
            text="Good friends good books",
        )
    ]
    indexer = InvertedIndexer()
    index_data = indexer.build_index(pages)
    output_path = tmp_path / "nested" / "index.json"

    indexer.save_index(index_data, output_path)
    loaded = indexer.load_index(output_path)

    assert output_path.exists()
    assert loaded == index_data
