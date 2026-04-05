import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    poem_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id   INTEGER NOT NULL REFERENCES posts(id),
    filename  TEXT NOT NULL,
    position  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS char_index (
    character TEXT NOT NULL,
    image_id  INTEGER NOT NULL REFERENCES images(id),
    PRIMARY KEY (character, image_id)
);

CREATE INDEX IF NOT EXISTS idx_char ON char_index(character);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    """Create schema and return an open connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn
