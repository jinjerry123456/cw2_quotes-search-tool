"""Tests for search operations."""

from __future__ import annotations

import pytest

from src.search import SearchEngine


@pytest.fixture
def sample_index() -> dict:
    return {
        "pages": {
            "url1": {"title": "Page One", "word_count": 4},
            "url2": {"title": "Page Two", "word_count": 3},
        },
        "index": {
            "good": {
                "url1": {"frequency": 2, "positions": [0, 2]},
                "url2": {"frequency": 1, "positions": [1]},
            },
            "friends": {
                "url1": {"frequency": 1, "positions": [1]},
            },
        },
    }


def test_get_word_postings_returns_empty_for_missing_word(sample_index: dict) -> None:
    engine = SearchEngine(sample_index)
    assert engine.get_word_postings("missing") == {}


def test_find_pages_single_term_ranks_by_frequency(sample_index: dict) -> None:
    engine = SearchEngine(sample_index)

    results = engine.find_pages("good")

    assert [result["url"] for result in results] == ["url1", "url2"]


def test_find_pages_multi_term_uses_intersection(sample_index: dict) -> None:
    engine = SearchEngine(sample_index)

    results = engine.find_pages("good friends")

    assert len(results) == 1
    assert results[0]["url"] == "url1"


def test_find_pages_rejects_empty_query(sample_index: dict) -> None:
    engine = SearchEngine(sample_index)

    with pytest.raises(ValueError):
        engine.find_pages("   ")
