"""Command-line entry point for the coursework search tool."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from src.crawler import WebsiteCrawler
from src.indexer import InvertedIndexer
from src.search import SearchEngine


INDEX_PATH = Path("data/index.json")


def build_command() -> None:
    crawler = WebsiteCrawler()
    indexer = InvertedIndexer()

    start_time = time.time()
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
    page_count = len(index_data.get("pages", {}))
    term_count = len(index_data.get("index", {}))
    print(f"Loaded index from {INDEX_PATH}.")
    print(f"Pages: {page_count}, unique terms: {term_count}.")


def print_command(word: str) -> None:
    index_data = _load_index_or_exit()
    engine = SearchEngine(index_data)
    postings = engine.get_word_postings(word)

    if not postings:
        print(f"No index entry found for '{word}'.")
        return

    print(f"Inverted index entry for '{word}':")
    for url, stats in postings.items():
        print(
            f"- {url} | frequency={stats['frequency']} | "
            f"positions={stats['positions']}"
        )


def find_command(query_terms: list[str]) -> None:
    query = " ".join(query_terms).strip()
    if not query:
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
        print(f"No pages contain all terms in query: '{query}'.")
        return

    print(f"Pages containing all terms in '{query}':")
    for result in results:
        print(f"- {result['title']} | {result['url']} | score={result['score']}")


def _load_index_or_exit() -> dict:
    if not INDEX_PATH.exists():
        raise SystemExit(
            "Index file not found. Run 'python -m src.main build' first."
        )
    return InvertedIndexer.load_index(INDEX_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quotes search coursework tool")
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
