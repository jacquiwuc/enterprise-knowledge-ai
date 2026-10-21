
"""Batch ingestion for multiple URLs."""

import logging
from collections.abc import Iterable

from app.ingestion.fetcher import ingest_url

logger = logging.getLogger(__name__)


def ingest_urls(urls: Iterable[str]) -> dict[str, int]:
    """Ingest URLs independently so one failure does not stop the batch."""
    results = {
        "total": 0,
        "succeeded": 0,
        "skipped": 0,
        "failed": 0,
    }

    for url in urls:
        results["total"] += 1
        logger.info("Starting batch ingestion: %s", url)

        try:
            saved = ingest_url(url)

            if saved:
                results["succeeded"] += 1
                logger.info("Batch ingestion succeeded: %s", url)
            else:
                results["skipped"] += 1
                logger.info(
                    "Batch ingestion skipped or not newly saved: %s", url
                )

        except Exception:
            results["failed"] += 1
            logger.exception("Batch ingestion failed: %s", url)
            continue

    logger.info("Batch ingestion summary: %s", results)
    return results
