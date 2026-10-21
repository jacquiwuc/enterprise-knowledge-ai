
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_embeddings(
    embeddings: list[dict[str, Any]],
    output_path: str | Path,
) -> int:
    """Append embeddings to JSONL, skipping previously saved chunk IDs."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing_ids: set[str] = set()

    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(
                        "Skipping invalid JSON at %s:%s",
                        path,
                        line_number,
                    )
                    continue

                chunk_id = record.get("chunk_id")
                if chunk_id:
                    existing_ids.add(chunk_id)

    saved_count = 0

    with path.open("a", encoding="utf-8") as file:
        for record in embeddings:
            chunk_id = record.get("chunk_id")

            if not chunk_id:
                logger.warning("Skipping embedding without chunk_id")
                continue

            if chunk_id in existing_ids:
                continue

            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )
            existing_ids.add(chunk_id)
            saved_count += 1

    logger.info(
        "Saved %s new embeddings to %s",
        saved_count,
        path,
    )
    return saved_count
