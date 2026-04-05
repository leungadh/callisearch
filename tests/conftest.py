import pytest
from pathlib import Path
from tests.helpers import SAMPLE_HTML


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def tmp_images(tmp_path):
    d = tmp_path / "images"
    d.mkdir()
    return d


@pytest.fixture
def sample_html_file(tmp_path):
    f = tmp_path / "sample.html"
    f.write_text(SAMPLE_HTML, encoding="utf-8")
    return str(f)
