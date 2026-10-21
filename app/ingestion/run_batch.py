
import logging
from pathlib import Path

from app.ingestion.batch_fetcher import ingest_urls
from app.ingestion.url_loader import load_urls
from app.logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> int:
    configure_logging()

    config_path = Path("config/urls.txt")

    try:
        urls = load_urls(config_path)
    except (OSError, ValueError) as exc:
        logger.error("Unable to load URL configuration: %s", exc)
        return 1

    if not urls:
        logger.warning("No URLs found in configuration: %s", config_path)
        return 0

    results = ingest_urls(urls)

    logger.info("Final batch results: %s", results)

    if results["failed"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
