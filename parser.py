import base64
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from db import init_db

_CHINESE_RE = re.compile(r"[\u4e00-\u9fff]{4,}")


def is_poem_text(text: str) -> bool:
    """Return True if text contains at least 4 consecutive Chinese characters."""
    return bool(_CHINESE_RE.search(text))


def extract_posts(html_content: str) -> list[dict]:
    """
    Parse HTML and return a list of dicts:
      {"poem_text": str, "images": [base64_str, ...]}

    Only posts with poem text are returned. Posts where no span
    passes is_poem_text are skipped.
    """
    soup = BeautifulSoup(html_content, "lxml")
    posts = []

    for post_el in soup.find_all(attrs={"data-ad-preview": "message"}):
        poem_text = ""
        for span in post_el.find_all("span", attrs={"dir": "auto"}):
            candidate = span.get_text(separator="", strip=True)
            if is_poem_text(candidate):
                poem_text = candidate
                break

        if not poem_text:
            continue

        # Images are siblings of the text container, not children.
        # Walk up to find the nearest ancestor that contains feedImage tags
        # for exactly this post (stops before an ancestor shared with other posts).
        container = post_el
        for ancestor in post_el.parents:
            imgs_in = ancestor.find_all("img", attrs={"data-imgperflogname": "feedImage"})
            posts_in = ancestor.find_all(attrs={"data-ad-preview": "message"})
            if imgs_in and len(posts_in) == 1:
                container = ancestor
                break

        images = []
        for img in container.find_all(
            "img", attrs={"data-imgperflogname": "feedImage"}
        ):
            src = img.get("src", "")
            if src.startswith("data:image/jpeg;base64,"):
                images.append(src.split(",", 1)[1])

        posts.append({"poem_text": poem_text, "images": images})

    return posts


def save_image(b64_data: str, filepath: Path) -> None:
    """Decode base64 JPEG data and write it to filepath (overwrites if exists)."""
    filepath.write_bytes(base64.b64decode(b64_data))


def parse_file(
    html_path: str,
    db_path: str = "calligraphy.db",
    images_dir: str = "images",
) -> None:
    """
    Parse an HTML file, extract posts, save images, and populate the database.
    Posts and images accumulate on re-run. char_index deduplicates via INSERT OR IGNORE.
    Posts with no images are stored in the posts table but not indexed (no char_index rows).
    """
    images_path = Path(images_dir)
    images_path.mkdir(exist_ok=True)

    conn = init_db(db_path)

    print(f"Reading {html_path} ...")
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()

    posts = extract_posts(html_content)
    print(f"Found {len(posts)} posts with poem text")

    for post_num, post in enumerate(posts, start=1):
        cursor = conn.execute(
            "INSERT INTO posts (poem_text) VALUES (?)", (post["poem_text"],)
        )
        post_id = cursor.lastrowid

        for img_pos, b64_data in enumerate(post["images"]):
            filename = f"post{post_id:03d}_img{img_pos:02d}.jpg"
            save_image(b64_data, images_path / filename)

            cursor = conn.execute(
                "INSERT INTO images (post_id, filename, position) VALUES (?, ?, ?)",
                (post_id, filename, img_pos),
            )
            image_id = cursor.lastrowid

            for char in set(post["poem_text"]):
                if "\u4e00" <= char <= "\u9fff":
                    conn.execute(
                        "INSERT OR IGNORE INTO char_index (character, image_id) VALUES (?, ?)",
                        (char, image_id),
                    )

        conn.commit()
        if post_num % 100 == 0:
            print(f"  {post_num}/{len(posts)} posts processed")

    conn.close()
    print(f"Done. {len(posts)} posts indexed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <html_file> [db_path] [images_dir]")
        sys.exit(1)
    html_path = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "calligraphy.db"
    images_dir = sys.argv[3] if len(sys.argv) > 3 else "images"
    parse_file(html_path, db_path, images_dir)
