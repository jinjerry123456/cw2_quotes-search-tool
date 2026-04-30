"""Integration-style tests for CLI command handlers."""

from __future__ import annotations

import json

from src.crawler import CrawlReport, CrawledPage
from src.indexer import InvertedIndexer
from src.main import build_command, find_command, load_command, print_command


def test_build_command_generates_index_file(tmp_path, monkeypatch, capsys) -> None:
    output_path = tmp_path / "index.json"
    report = CrawlReport(
        pages=[
            CrawledPage(
                url="https://quotes.toscrape.com/page/1/",
                title="Page 1",
                text="Good friends good books",
            )
        ],
        visited_urls=["https://quotes.toscrape.com/page/1/"],
        skipped_urls=[],
        failed_urls=[],
    )

    monkeypatch.setattr("src.main.INDEX_PATH", output_path)
    monkeypatch.setattr(
        "src.main.WebsiteCrawler.crawl_with_report",
        lambda self: report,
    )

    build_command()
    stdout = capsys.readouterr().out

    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["metadata"]["total_pages"] == 1
    assert "Build complete. Crawled 1 pages." in stdout


def test_load_command_reads_existing_index_file(tmp_path, monkeypatch, capsys) -> None:
    output_path = tmp_path / "index.json"
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/page/1/",
            title="Page 1",
            text="Good friends",
        )
    ]
    index_data = InvertedIndexer().build_index(pages)
    InvertedIndexer.save_index(index_data, output_path)
    monkeypatch.setattr("src.main.INDEX_PATH", output_path)

    load_command()
    stdout = capsys.readouterr().out

    assert f"Loaded index from {output_path}." in stdout
    assert "Pages: 1, unique terms: 2." in stdout


def test_print_command_reports_missing_word(tmp_path, monkeypatch, capsys) -> None:
    output_path = tmp_path / "index.json"
    index_data = {
        "metadata": {"total_pages": 1, "total_terms": 1, "total_tokens": 1},
        "pages": {"url1": {"title": "Page One", "word_count": 1}},
        "index": {"good": {"url1": {"frequency": 1, "positions": [0]}}},
    }
    InvertedIndexer.save_index(index_data, output_path)
    monkeypatch.setattr("src.main.INDEX_PATH", output_path)

    print_command("missing")
    stdout = capsys.readouterr().out

    assert "No index entry found for 'missing'." in stdout


def test_find_command_returns_intersection_pages(tmp_path, monkeypatch, capsys) -> None:
    output_path = tmp_path / "index.json"
    index_data = {
        "metadata": {"total_pages": 2, "total_terms": 2, "total_tokens": 5},
        "pages": {
            "url1": {"title": "Page One", "word_count": 3},
            "url2": {"title": "Page Two", "word_count": 2},
        },
        "index": {
            "good": {
                "url1": {"frequency": 1, "positions": [0]},
                "url2": {"frequency": 1, "positions": [0]},
            },
            "friends": {
                "url1": {"frequency": 1, "positions": [1]},
            },
        },
    }
    InvertedIndexer.save_index(index_data, output_path)
    monkeypatch.setattr("src.main.INDEX_PATH", output_path)

    find_command(["good", "friends"])
    stdout = capsys.readouterr().out

    assert "Pages containing all terms in 'good friends':" in stdout
    assert "- Page One | url1 | score=2 | best_span=1" in stdout
    assert "url2" not in stdout


def test_find_command_handles_empty_input(tmp_path, monkeypatch, capsys) -> None:
    output_path = tmp_path / "index.json"
    InvertedIndexer.save_index({"metadata": {}, "pages": {}, "index": {}}, output_path)
    monkeypatch.setattr("src.main.INDEX_PATH", output_path)

    find_command([])
    stdout = capsys.readouterr().out

    assert "Please provide at least one search term." in stdout
