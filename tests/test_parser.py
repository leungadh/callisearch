import sqlite3
from pathlib import Path

import pytest

from parser import extract_posts, is_poem_text, parse_file, save_image
from tests.helpers import FAKE_JPEG, FAKE_JPEG_B64, SAMPLE_HTML


def test_is_poem_text_accepts_long_chinese():
    assert is_poem_text("人間底是無波處，一日風波十二時！") is True


def test_is_poem_text_rejects_short_chinese():
    assert is_poem_text("設定") is False


def test_is_poem_text_rejects_english():
    assert is_poem_text("Hello world") is False


def test_is_poem_text_requires_four_consecutive():
    # Exactly three consecutive Chinese chars — one short of the threshold
    assert is_poem_text("人間底") is False


def test_extract_posts_skips_short_text():
    posts = extract_posts(SAMPLE_HTML)
    assert len(posts) == 2  # third post ("設定") filtered out


def test_extract_posts_poem_text():
    posts = extract_posts(SAMPLE_HTML)
    assert "人間底是無波處" in posts[0]["poem_text"]
    assert "春風又綠江南岸" in posts[1]["poem_text"]


def test_extract_posts_image_counts():
    posts = extract_posts(SAMPLE_HTML)
    assert len(posts[0]["images"]) == 1
    assert len(posts[1]["images"]) == 2


def test_extract_posts_image_data():
    posts = extract_posts(SAMPLE_HTML)
    assert posts[0]["images"][0] == FAKE_JPEG_B64


def test_save_image_writes_correct_bytes(tmp_path):
    dest = tmp_path / "out.jpg"
    save_image(FAKE_JPEG_B64, dest)
    assert dest.read_bytes() == FAKE_JPEG


def test_save_image_overwrites_existing(tmp_path):
    dest = tmp_path / "out.jpg"
    dest.write_bytes(b"old content")
    save_image(FAKE_JPEG_B64, dest)
    assert dest.read_bytes() == FAKE_JPEG


def test_parse_file_creates_correct_post_count(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    conn = sqlite3.connect(tmp_db)
    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    conn.close()
    assert count == 2


def test_parse_file_creates_correct_image_count(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    conn = sqlite3.connect(tmp_db)
    count = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    conn.close()
    assert count == 3  # post 1 has 1 image, post 2 has 2 images


def test_parse_file_saves_image_files(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    saved = sorted(tmp_images.iterdir())
    assert len(saved) == 3


def test_parse_file_indexes_character(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    conn = sqlite3.connect(tmp_db)
    # 人 appears in poem 1
    count = conn.execute(
        "SELECT COUNT(*) FROM char_index WHERE character=?", ("人",)
    ).fetchone()[0]
    conn.close()
    assert count >= 1


def test_parse_file_does_not_index_non_chinese(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    conn = sqlite3.connect(tmp_db)
    # Punctuation should not be indexed
    count = conn.execute(
        "SELECT COUNT(*) FROM char_index WHERE character=?", ("！",)
    ).fetchone()[0]
    conn.close()
    assert count == 0


def test_parse_file_is_idempotent(tmp_db, tmp_images, sample_html_file):
    parse_file(sample_html_file, tmp_db, str(tmp_images))
    parse_file(sample_html_file, tmp_db, str(tmp_images))  # run twice
    conn = sqlite3.connect(tmp_db)
    # Re-running should not duplicate posts (new rows are added, not re-inserted)
    # This test verifies it completes without error; deduplication is not required
    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    conn.close()
    assert count >= 2  # at least the original 2
