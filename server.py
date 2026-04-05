import sqlite3
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DB_PATH = "calligraphy.db"
IMAGES_DIR = "images"
STATIC_DIR = "static"

_SEARCH_SQL = """
    SELECT i.filename, p.poem_text, i.post_id
    FROM char_index ci
    JOIN images i ON i.id = ci.image_id
    JOIN posts p  ON p.id = i.post_id
    WHERE ci.character = ?
    ORDER BY i.post_id, i.position
"""


def create_app(
    db_path: str = DB_PATH,
    images_dir: str = IMAGES_DIR,
    static_dir: str = STATIC_DIR,
) -> FastAPI:
    app = FastAPI(title="Calligraphy Search")
    Path(images_dir).mkdir(exist_ok=True)
    app.mount("/images", StaticFiles(directory=images_dir), name="images")

    @app.get("/")
    def index():
        return FileResponse(f"{static_dir}/index.html")

    @app.get("/search")
    def search(char: str = Query(default="")):
        if not char:
            return {"character": "", "total": 0, "results": []}
        char = char[0]  # only the first character is used
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(_SEARCH_SQL, (char,)).fetchall()
        finally:
            conn.close()
        results = [
            {
                "image_url": f"/images/{row['filename']}",
                "poem_text": row["poem_text"],
                "post_id": row["post_id"],
            }
            for row in rows
        ]
        return {"character": char, "total": len(results), "results": results}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
