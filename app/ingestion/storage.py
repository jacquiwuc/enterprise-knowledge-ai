
import json
from pathlib import Path

from app.processing.deduplicator import load_existing_hashes
from app.processing.models import Document


def save_document(document: Document, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                document.model_dump(mode="json"),
                ensure_ascii=False,
            )
        )
        file.write("\n")


def save_if_new(document: Document, output_path: Path) -> bool:
    existing_hashes = load_existing_hashes(output_path)

    if document.content_hash in existing_hashes:
        return False

    save_document(document, output_path)
    return True
