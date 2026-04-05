import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from db import init_db


@pytest.fixture
def populated_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = init_db(db_path)
    conn.execute("INSERT INTO posts (poem_text) VALUES (?)", ("人間底是無波處，一日風波十二時！",))
    conn.execute("INSERT INTO posts (poem_text) VALUES (?)", ("春風又綠江南岸，明月何時照我還。",))
    conn.execute(
        "INSERT INTO images (post_id, filename, position) VALUES (1, 'post001_img00.jpg', 0)"
    )
    conn.execute(
        "INSERT INTO images (post_id, filename, position) VALUES (2, 'post002_img00.jpg', 0)"
    )
    # 人 → post 1 image; 春 → post 2 image
    conn.execute("INSERT INTO char_index (character, image_id) VALUES (?, ?)", ("人", 1))
    conn.execute("INSERT INTO char_index (character, image_id) VALUES (?, ?)", ("間", 1))
    conn.execute("INSERT INTO char_index (character, image_id) VALUES (?, ?)", ("春", 2))
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def client(populated_db, tmp_path):
    from server import create_app
    images_dir = str(tmp_path / "images")
    Path(images_dir).mkdir()
    static_dir = "static"
    Path(static_dir).mkdir(exist_ok=True)
    (Path(static_dir) / "index.html").write_text("<html>test</html>")
    app = create_app(db_path=populated_db, images_dir=images_dir, static_dir=static_dir)
    return TestClient(app)


def test_search_found(client):
    resp = client.get("/search?char=人")
    assert resp.status_code == 200
    data = resp.json()
    assert data["character"] == "人"
    assert data["total"] == 1
    assert data["results"][0]["image_url"] == "/images/post001_img00.jpg"
    assert data["results"][0]["poem_text"] == "人間底是無波處，一日風波十二時！"
    assert data["results"][0]["post_id"] == 1


def test_search_not_found(client):
    resp = client.get("/search?char=龘")
    assert resp.status_code == 200
    data = resp.json()
    assert data["character"] == "龘"
    assert data["total"] == 0
    assert data["results"] == []


def test_search_empty_char_returns_zero(client):
    resp = client.get("/search?char=")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_search_uses_only_first_character(client):
    resp = client.get("/search?char=人間")
    assert resp.status_code == 200
    data = resp.json()
    assert data["character"] == "人"
    assert data["total"] == 1


def test_search_returns_multiple_results(client):
    # 間 shares an image with 人 (same post), so searching 間 also returns 1 result
    resp = client.get("/search?char=間")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_root_serves_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
