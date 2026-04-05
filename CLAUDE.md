# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Parse a data file (run once per new HTML dump)
python parser.py data/<file>.html

# Start the web server
python server.py          # → http://localhost:8000

# Run all tests
pytest

# Run a single test
pytest tests/test_parser.py::test_extract_posts_poem_text -v
```

## Architecture

Two-phase system: a one-time parser builds a SQLite database, then a FastAPI server handles all queries.

**Phase 1 — Parse**

`parser.py` reads a Facebook page HTML dump from `data/`, finds each post via `data-ad-preview=message`, extracts poem text from `<span dir=auto>` elements, and extracts calligraphy images from `<img data-imgperflogname=feedImage>` tags. Images are siblings of the text container in the DOM (not children), so the extractor walks up the ancestor chain to find the enclosing unit. Images are saved as `images/post{id:03d}_img{pos:02d}.jpg` and every Chinese character (U+4E00–U+9FFF) in each poem is indexed in `char_index`.

**Phase 2 — Serve**

`server.py` uses a `create_app(db_path, images_dir, static_dir)` factory (enables test injection). The `/search?char=X` endpoint queries `char_index → images → posts` and returns all matching results. Only the first Unicode code point of `char` is used.

**Database** (`calligraphy.db`)

```
posts      — poem text per Facebook post
images     — one JPEG filename per image, linked to a post
char_index — (character, image_id) pairs; PRIMARY KEY prevents duplicates
```

Foreign key enforcement is enabled (`PRAGMA foreign_keys = ON`) in `db.init_db`.

**Tests**

Tests use `SAMPLE_HTML` (in `tests/helpers.py`) as a minimal fixture — never the real 174 MB HTML file. The `create_app` factory lets `tests/test_server.py` pass a temp DB path without monkeypatching.

Re-running `parser.py` on the same file accumulates rows (no deduplication for `posts`/`images`); `char_index` deduplicates via `INSERT OR IGNORE`. Posts with no images are stored but not indexed.
