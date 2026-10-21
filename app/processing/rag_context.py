
from typing import Any


def build_context(
    results: list[dict[str, Any]],
    max_chars: int = 6000,
) -> str:
    """Build a source-labelled context from semantic search results."""
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1")

    sections: list[str] = []
    used_chars = 0

    for rank, result in enumerate(results, start=1):
        text = result.get("text", "").strip()

        if not text:
            continue

        source = result.get("source_url") or "Unknown source"
        title = result.get("title") or "Untitled"
        score = result.get("score")

        header = f"[Source {rank}] Title: {title}\nURL: {source}"

        if score is not None:
            header += f"\nSimilarity: {score:.4f}"

        section = f"{header}\nContent:\n{text}"

        remaining = max_chars - used_chars

        if remaining <= 0:
            break

        if len(section) > remaining:
            section = section[:remaining]

        sections.append(section)
        used_chars += len(section)

    return "\n\n---\n\n".join(sections)
