"""Command-line entry point for the coursework search tool."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from src.crawler import WebsiteCrawler
from src.indexer import InvertedIndexer
from src.search import SearchEngine

# Fixed path under repo root -> markers and `load` always hit the same artefact without extra CLI flags.
INDEX_PATH = Path("data/index.json")


def build_command() -> None:
    crawler = WebsiteCrawler()
    indexer = InvertedIndexer()

    start_time = time.time()
    # Crawl then index in one process -> index always matches the exact corpus we just fetched.
    report = crawler.crawl_with_report()
    index_data = indexer.build_index(report.pages)
    indexer.save_index(index_data, INDEX_PATH)
    elapsed_seconds = time.time() - start_time

    print(f"Build complete. Crawled {len(report.pages)} pages.")
    print(f"Visited URLs: {len(report.visited_urls)}.")
    print(f"Failed URLs: {len(report.failed_urls)}.")
    print(f"Skipped non-HTML/invalid URLs: {len(report.skipped_urls)}.")
    print(f"Elapsed time: {elapsed_seconds:.2f} seconds.")
    print(f"Index saved to {INDEX_PATH}.")


def load_command() -> None:
    index_data = _load_index_or_exit()
    metadata = index_data.get("metadata", {})
    page_count = metadata.get("total_pages", len(index_data.get("pages", {})))
    term_count = metadata.get("total_terms", len(index_data.get("index", {})))
    token_count = metadata.get("total_tokens")
    print(f"Loaded index from {INDEX_PATH}.")
    print(f"Pages: {page_count}, unique terms: {term_count}.")
    if token_count is not None:
        print(f"Total tokens indexed: {token_count}.")


def print_command(word: str) -> None:
    index_data = _load_index_or_exit()
    engine = SearchEngine(index_data)
    # First-token normalisation -> rejects punctuation-only input before we hit the index.
    normalized_word = engine._normalize_single_word(word)
    if not normalized_word:
        print("Please provide at least one searchable word.")
        return

    # Pass raw `word` into engine -> same lowercasing/token rules as indexing, so CLI matches stored keys.
    postings = engine.get_word_postings(word)

    if not postings:
        print(f"No index entry found for '{normalized_word}'.")
        return

    print(f"Inverted index entry for '{normalized_word}':")
    # Sort by descending frequency, then URL -> strongest evidence first, deterministic tie-break.
    for url, stats in sorted(
        postings.items(),
        key=lambda item: (-item[1]["frequency"], item[0]),
    ):
        print(
            f"- {url} | frequency={stats['frequency']} | "
            f"positions={stats['positions']}"
        )


def find_command(query_terms: list[str]) -> None:
    # `nargs="*"` gives a list -> join so `find good friends` and `find "good friends"` both become one query string.
    query = " ".join(query_terms).strip()
    normalised_terms = SearchEngine.normalise_query_terms(query)
    if not normalised_terms:
        print("Please provide at least one search term.")
        return

    index_data = _load_index_or_exit()
    engine = SearchEngine(index_data)

    try:
        results = engine.find_pages(query)
    except ValueError as error:
        print(str(error))
        return

    if not results:
        print(f"No pages contain all terms in query: '{' '.join(normalised_terms)}'.")
        return

    print(f"Pages containing all terms in '{' '.join(normalised_terms)}':")
    for result in results:
        print(
            f"- {result['title']} | {result['url']} | "
            f"score={result['score']} | best_span={result['best_span']}"
        )


def _load_index_or_exit() -> dict:
    # Hard fail fast -> clearer UX than a traceback when students skip `build`.
    if not INDEX_PATH.exists():
        raise SystemExit(
            "Index file not found. Run 'python -m src.main build' first."
        )
    return InvertedIndexer.load_index(INDEX_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quotes search coursework tool")
    # Subcommands mirror brief (`build`, `load`, `print`, `find`) -> one entrypoint, four behaviours.
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build")
    subparsers.add_parser("load")

    print_parser = subparsers.add_parser("print")
    print_parser.add_argument("word")

    find_parser = subparsers.add_parser("find")
    find_parser.add_argument("terms", nargs="*")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "build":
        build_command()
    elif args.command == "load":
        load_command()
    elif args.command == "print":
        print_command(args.word)
    elif args.command == "find":
        find_command(args.terms)


if __name__ == "__main__":
    main()
