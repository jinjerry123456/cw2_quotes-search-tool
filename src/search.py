"""Search operations over the inverted index."""

from __future__ import annotations

from typing import Any

from src.indexer import InvertedIndexer


class SearchEngine:
    """Provides print and find commands over the saved index."""

    def __init__(self, index_data: dict[str, Any]) -> None:
        self.index_data = index_data
        self.page_data = index_data.get("pages", {})
        self.index = index_data.get("index", {})

    def get_word_postings(self, word: str) -> dict[str, Any]:
        normalized = self._normalize_single_word(word)
        return self.index.get(normalized, {})

    def find_pages(self, query: str) -> list[dict[str, Any]]:
        terms = InvertedIndexer.tokenize(query)
        if not terms:
            raise ValueError("Query must contain at least one searchable word.")

        candidate_sets = []
        for term in terms:
            postings = self.index.get(term, {})
            candidate_sets.append(set(postings.keys()))

        if not candidate_sets:
            return []

        matching_urls = set.intersection(*candidate_sets) if candidate_sets else set()
        ranked_results = []

        for url in matching_urls:
            total_frequency = sum(self.index[term][url]["frequency"] for term in terms)
            ranked_results.append(
                {
                    "url": url,
                    "title": self.page_data.get(url, {}).get("title", "Untitled page"),
                    "score": total_frequency,
                }
            )

        ranked_results.sort(key=lambda item: (-item["score"], item["url"]))
        return ranked_results

    @staticmethod
    def _normalize_single_word(word: str) -> str:
        tokens = InvertedIndexer.tokenize(word)
        return tokens[0] if tokens else ""
