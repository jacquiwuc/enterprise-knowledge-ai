
import json
import logging
from pathlib import Path

from pydantic import ValidationError

from app.processing.chunk_processor import create_chunks
from app.processing.chunk_storage import save_chunks
from app.processing.models import Document

logger = logging.getLogger(__name__)


def process_documents(
    input_path: Path,
    output_path: Path,
    chunk_size: int = 500,
    overlap: int = 50,
) -> dict[str, int]:
    """Read documents from JSONL, create chunks, and save them."""
    stats = {
        "documents_processed": 0,
        "chunks_generated": 0,
        "chunks_saved": 0,
        "records_failed": 0,
    }

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input document file not found: {input_path}"
        )

    chunks = []

    with input_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                document = Document.model_validate_json(line)
                document_chunks = create_chunks(
                    document,
                    chunk_size=chunk_size,
                    overlap=overlap,
                )
            except (ValidationError, ValueError, json.JSONDecodeError):
                logger.exception(
                    "Failed to process document at line %s in %s",
                    line_number,
                    input_path,
                )
                stats["records_failed"] += 1
                continue

            stats["documents_processed"] += 1
            stats["chunks_generated"] += len(document_chunks)
            chunks.extend(document_chunks)

    stats["chunks_saved"] = save_chunks(chunks, output_path)

    logger.info("Document chunking pipeline finished: %s", stats)
    return stats
