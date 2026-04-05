import sqlite3
import pytest
from db import init_db


def test_init_db_creates_tables(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    }
    assert tables == {"posts", "images", "char_index"}
    conn.close()


def test_init_db_creates_index(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    indexes = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ).fetchall()
    }
    assert "idx_char" in indexes
    conn.close()


def test_init_db_is_idempotent(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = init_db(db_path)  # second call must not raise
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    }
    assert tables == {"posts", "images", "char_index"}
    conn.close()
