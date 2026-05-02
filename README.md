# Quotes Search Tool

This project implements a command-line search tool for `https://quotes.toscrape.com/`.
It crawls the website, builds an inverted index, saves the index to disk, and supports
searching for single-word and multi-word queries.

## Project Structure

```text
src/
  crawler.py
  indexer.py
  search.py
  main.py
tests/
  test_crawler.py
  test_indexer.py
  test_search.py
data/
```

## Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`
- `pytest`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Build the index:

```bash
python -m src.main build
```

Load an existing index from disk:

```bash
python -m src.main load
```

Print the inverted index entry for a word:

```bash
python -m src.main print nonsense
```

Find pages containing all query terms:

```bash
python -m src.main find indifference
python -m src.main find good friends
```

## Testing

Run the test suite with:

```bash
pytest
```

## Generative AI (GenAI)

This module’s coursework requires a declaration and critical reflection on any GenAI use.
See **[GENAI_REFLECTION.md](./GENAI_REFLECTION.md)** for a written statement and reflection
you can align with your video (edit the bracketed placeholders to match your actual tools).

## Notes

- The crawler enforces a politeness delay of at least 6 seconds between requests.
- The crawler targets the canonical quote listing pages (`/` and `/page/<n>/`) so the
  searchable corpus contains each quote once without duplicating tag archive pages.
- Search is case-insensitive.
- The built index is saved to `data/index.json`.
