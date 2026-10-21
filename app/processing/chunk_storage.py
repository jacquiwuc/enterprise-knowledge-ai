
import json
from pathlib import Path
from collections.abc import Iterable

from app.processing.chunk_models import TextChunk


def save_chunks(
    chunks: Iterable[TextChunk],
    output_path: Path,
) -> int:
    """Append new chunks to a JSONL file, skipping existing chunk IDs."""
    chunks = list(chunks)

    if not chunks:
        return 0

    existing_ids: set[str] = set()

    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                record = json.loads(line)
                existing_ids.add(record["chunk_id"])

    new_records = []
    for chunk in chunks:
        if chunk.chunk_id in existing_ids:
            continue

        new_records.append(
            json.dumps(
                chunk.model_dump(mode="json"),
                ensure_ascii=False,
            )
        )
        existing_ids.add(chunk.chunk_id)

    if not new_records:
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as file:
        for record in new_records:
            file.write(record + "\n")

    return len(new_records)
