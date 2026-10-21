
import json
import logging
from pathlib import Path

from app.processing.embedder import TextEmbedder
from app.processing.embedding_storage import save_embeddings

logger = logging.getLogger(__name__)

DEFAULT_INPUT_PATH = Path("data/processed/chunks.jsonl")
DEFAULT_OUTPUT_PATH = Path("data/processed/embeddings.jsonl")


def load_chunks(input_path: str | Path) -> list[dict]:
    """Load chunk records from a JSONL file."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Chunk file not found: {path}")

    chunks = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping invalid JSON at %s:%s: %s",
                    path,
                    line_number,
                    exc,
                )
                continue

            if not isinstance(record, dict):
                logger.warning(
                    "Skipping non-object JSON at %s:%s",
                    path,
                    line_number,
                )
                continue

            if not record.get("chunk_id"):
                logger.warning(
                    "Skipping record without chunk_id at %s:%s",
                    path,
                    line_number,
                )
                continue

            text = record.get("text")
            if not isinstance(text, str) or not text.strip():
                logger.warning(
                    "Skipping record without usable text at %s:%s",
                    path,
                    line_number,
                )
                continue

            chunks.append(record)

    return chunks


def process_chunks(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    batch_size: int = 32,
) -> int:
    """Generate and save embeddings for chunks not yet processed."""
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    chunks = load_chunks(input_path)

    if not chunks:
        logger.warning("No valid chunks found in %s", input_path)
        return 0

    output_file = Path(output_path)
    existing_ids = set()

    if output_file.exists():
        with output_file.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    existing = json.loads(line)
                except json.JSONDecodeError:
                    continue

                chunk_id = existing.get("chunk_id")
                if chunk_id:
                    existing_ids.add(chunk_id)

    pending_chunks = [
        chunk for chunk in chunks
        if chunk["chunk_id"] not in existing_ids
    ]

    if not pending_chunks:
        logger.info("All chunks already have embeddings")
        return 0

    embedder = TextEmbedder()
    saved_count = 0

    for start in range(0, len(pending_chunks), batch_size):
        batch = pending_chunks[start:start + batch_size]
        texts = [chunk["text"] for chunk in batch]
        vectors = embedder.embed_texts(texts)

        records = []

        for chunk, vector in zip(batch, vectors):
            records.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "source_url": chunk.get("source_url"),
                "title": chunk.get("title"),
                "chunk_index": chunk.get("chunk_index"),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimension": len(vector),
                "embedding": vector,
            })

        saved_count += save_embeddings(records, output_file)

        logger.info(
            "Processed batch %s; generated %s vectors",
            start // batch_size + 1,
            len(vectors),
        )

    return saved_count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = process_chunks()
    print(f"New embeddings saved: {count}")
