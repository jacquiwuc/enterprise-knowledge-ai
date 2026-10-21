import hashlib

from bs4 import BeautifulSoup

from app.processing.models import Document


def parse_html(html: str, source_url: str) -> Document:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Remove elements that are not useful as document content.
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    content = " ".join(soup.stripped_strings)

    if not title:
        raise ValueError("The webpage has no usable title")

    if not content:
        raise ValueError("The webpage has no usable text content")

    content_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    return Document(
        source_url=source_url,
        title=title,
        content=content,
        content_hash=content_hash,
    )
