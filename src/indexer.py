"""Inverted index construction and storage."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.crawler import CrawledPage


TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


class InvertedIndexer:
    """Builds an inverted index with word frequency and positions."""

    def build_index(self, pages: list[CrawledPage]) -> dict[str, Any]:
        index: dict[str, dict[str, dict[str, list[int] | int]]] = {}
        page_metadata: dict[str, dict[str, str | int]] = {}
        total_tokens = 0

        for page in pages:
            tokens = self.tokenize(page.text)
            total_tokens += len(tokens)
            page_metadata[page.url] = {
                "title": page.title,
                "word_count": len(tokens),
                "unique_word_count": len(set(tokens)),
            }

            for position, token in enumerate(tokens):
                postings = index.setdefault(token, {})
                page_entry = postings.setdefault(
                    page.url,
                    {"frequency": 0, "positions": []},
                )
                page_entry["frequency"] += 1
                page_entry["positions"].append(position)

        return {
            "metadata": {
                "indexed_at_utc": datetime.now(timezone.utc).isoformat(),
                "total_pages": len(page_metadata),
                "total_terms": len(index),
                "total_tokens": total_tokens,
            },
            "pages": page_metadata,
            "index": index,
        }

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())

    @staticmethod
    def save_index(index_data: dict[str, Any], output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(index_data, handle, indent=2)

    @staticmethod
    def load_index(input_path: str | Path) -> dict[str, Any]:
        path = Path(input_path)
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
