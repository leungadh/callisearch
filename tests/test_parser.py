import pytest
from tests.helpers import FAKE_JPEG_B64, SAMPLE_HTML
from parser import is_poem_text, extract_posts


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
