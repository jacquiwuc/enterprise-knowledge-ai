
import logging
from typing import Any

from app.processing.rag_context import build_context
from app.processing.semantic_search import search

logger = logging.getLogger(__name__)


def retrieve_context(
    question: str,
    top_k: int = 3,
    max_context_chars: int = 6000,
) -> dict[str, Any]:
    """Retrieve relevant chunks and assemble source-labelled context."""
    if not question or not question.strip():
        raise ValueError("Question must not be empty")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if max_context_chars < 1:
        raise ValueError("max_context_chars must be at least 1")

    results = search(question, top_k=top_k)
    context = build_context(results, max_chars=max_context_chars)

    sources = []
    for result in results:
        if not result.get("text", "").strip():
            continue

        sources.append({
            "chunk_id": result.get("chunk_id"),
            "title": result.get("title"),
            "source_url": result.get("source_url"),
            "score": result.get("score"),
        })

    logger.info(
        "Retrieved %s results for a question",
        len(sources),
    )

    return {
        "question": question.strip(),
        "context": context,
        "sources": sources,
        "result_count": len(sources),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    question = input("Enter your question: ").strip()

    try:
        response = retrieve_context(question)

        print("\n=== Retrieved Context ===")
        print(response["context"] or "No relevant context found.")

        print("\n=== Sources ===")
        for source in response["sources"]:
            print(
                f"- {source['title']} | "
                f"{source['source_url']} | "
                f"score={source['score']:.4f}"
            )

        print(f"\nResults: {response['result_count']}")

    except (ValueError, FileNotFoundError) as exc:
        print(f"Unable to retrieve context: {exc}")
