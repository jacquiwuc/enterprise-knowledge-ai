
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from app.processing.embedder import TextEmbedder

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDINGS_PATH = Path("data/processed/embeddings.jsonl")


def load_embeddings(
    embeddings_path: str | Path = DEFAULT_EMBEDDINGS_PATH,
) -> list[dict[str, Any]]:
    """Load valid embedding records from a JSONL file."""
    path = Path(embeddings_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Embeddings file not found: {path}"
        )

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping invalid JSON at line %s",
                    line_number,
                )
                continue

            if not isinstance(record, dict):
                continue

            vector = record.get("embedding")
            chunk_id = record.get("chunk_id")

            if not chunk_id or not isinstance(vector, list):
                continue

            try:
                vector_array = np.asarray(vector, dtype=np.float64)
            except (TypeError, ValueError):
                continue

            if (
                vector_array.ndim != 1
                or vector_array.size == 0
                or not np.isfinite(vector_array).all()
                or np.linalg.norm(vector_array) == 0
            ):
                continue

            records.append(record)

    return records


def search(
    query: str,
    embeddings_path: str | Path = DEFAULT_EMBEDDINGS_PATH,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Return the most semantically similar chunks for a query."""
    if not query or not query.strip():
        raise ValueError("Query must not be empty")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    records = load_embeddings(embeddings_path)

    if not records:
        return []

    embedder = TextEmbedder()
    query_vector = np.asarray(
        embedder.embed_texts([query])[0],
        dtype=np.float64,
    )

    if (
        query_vector.ndim != 1
        or query_vector.size == 0
        or not np.isfinite(query_vector).all()
        or np.linalg.norm(query_vector) == 0
    ):
        raise ValueError("Query embedding is invalid")

    scored_records = []

    for record in records:
        vector = np.asarray(
            record["embedding"],
            dtype=np.float64,
        )

        if vector.shape != query_vector.shape:
            logger.warning(
                "Skipping incompatible vector for chunk %s",
                record["chunk_id"],
            )
            continue

        # Cosine similarity: dot product of normalized vectors.
        denominator = np.linalg.norm(vector) * np.linalg.norm(
            query_vector
        )
        if denominator == 0:
            continue

        score = float(np.dot(vector, query_vector) / denominator)

        result = {
            key: value
            for key, value in record.items()
            if key != "embedding"
        }
        result["text"] = record.get("text", "")
        result["score"] = score
        scored_records.append(result)

    scored_records.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_records[:top_k]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    question = input("Enter your question: ").strip()

    results = search(question, top_k=3)

    if not results:
        print("No matching chunks found.")
    else:
        for rank, result in enumerate(results, start=1):
            print(f"\n--- Result {rank} ---")
            print(f"Score: {result['score']:.4f}")
            print(f"Title: {result.get('title')}")
            print(f"Source: {result.get('source_url')}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Text: {result.get('text', '')[:500]}")
