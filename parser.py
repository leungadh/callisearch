import re
from bs4 import BeautifulSoup

_CHINESE_RE = re.compile(r"[\u4e00-\u9fff]{4,}")


def is_poem_text(text: str) -> bool:
    """Return True if text contains at least 4 consecutive Chinese characters."""
    return bool(_CHINESE_RE.search(text))


def extract_posts(html_content: str) -> list:
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

        images = []
        for img in post_el.find_all(
            "img", attrs={"data-imgperflogname": "feedImage"}
        ):
            src = img.get("src", "")
            if src.startswith("data:image/jpeg;base64,"):
                images.append(src.split(",", 1)[1])

        posts.append({"poem_text": poem_text, "images": images})

    return posts
