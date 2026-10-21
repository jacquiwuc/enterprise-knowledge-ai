import hashlib
import logging
from pathlib import Path

import httpx

from app.ingestion.parser import parse_html
from app.ingestion.storage import save_if_new
from app.logging_config import configure_logging

logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str:
    logger.info("Fetching webpage: %s", url)

    try:
        response = httpx.get(
            url,
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": "EnterpriseKnowledgeAI/0.1"
            },
        )
        response.raise_for_status()

    except httpx.HTTPStatusError:
        logger.exception("HTTP status error for URL: %s", url)
        raise

    except httpx.RequestError:
        logger.exception("Network request failed for URL: %s", url)
        raise

    logger.info(
        "Fetched webpage successfully: %s, status=%s",
        url,
        response.status_code,
    )

    return response.text


def save_html(html: str, output_path: Path) -> None:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
    except OSError:
        logger.exception(
            "Failed to save raw HTML: %s",
            output_path,
        )
        raise

    logger.info("Saved raw HTML: %s", output_path)


def ingest_url(url: str) -> bool:
    """Fetch, parse and save one document. Return True if newly saved."""
    logger.info("Starting ingestion: %s", url)

    html = fetch_html(url)
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    raw_path = Path("data/raw") / f"{url_hash}.html"
    save_html(html, raw_path)

    try:
        document = parse_html(html, url)
    except Exception:
        logger.exception("Failed to parse webpage: %s", url)
        raise

    output_path = Path("data/processed/documents.jsonl")

    try:
        saved = save_if_new(document, output_path)
    except (OSError, ValueError, KeyError):
        logger.exception("Failed to save document: %s", url)
        raise

    if saved:
        logger.info(
            "Document saved: title=%s, url=%s",
            document.title,
            url,
        )
    else:
        logger.info("Duplicate document skipped: %s", url)

    return saved


if __name__ == "__main__":
    configure_logging()

    try:
        ingest_url("https://example.com")
    except (httpx.HTTPError, ValueError, OSError) :
        logger.error("Ingestion failed; see previous error logs")
        raise SystemExit(1)
