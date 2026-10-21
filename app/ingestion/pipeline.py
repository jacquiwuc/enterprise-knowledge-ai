
import logging
from collections.abc import Iterable

from app.ingestion.fetcher import ingest_url
from app.logging_config import configure_logging

logger = logging.getLogger(__name__)


def run_pipeline(urls: Iterable[str]) -> dict[str, int]:
    """Process URLs independently and continue after individual failures."""
    stats = {
        "total": 0,
        "saved": 0,
        "skipped": 0,
        "failed": 0,
    }

    for url in urls:
        stats["total"] += 1
        logger.info("Processing URL: %s", url)

        try:
            saved = ingest_url(url)
        except Exception:
            stats["failed"] += 1
            logger.exception("URL processing failed: %s", url)
            continue

        if saved:
            stats["saved"] += 1
        else:
            stats["skipped"] += 1

    logger.info(
        "Pipeline finished: total=%d saved=%d skipped=%d failed=%d",
        stats["total"],
        stats["saved"],
        stats["skipped"],
        stats["failed"],
    )

    return stats


if __name__ == "__main__":
    configure_logging()

    urls_file = "data/urls.txt"

    with open(urls_file, "r", encoding="utf-8") as file:
        urls = [
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        ]

    results = run_pipeline(urls)
    print("Pipeline results:", results)