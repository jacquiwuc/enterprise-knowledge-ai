
import hashlib

from app.processing.chunk_models import TextChunk
from app.processing.chunker import split_text
from app.processing.models import Document


def create_chunks(
    document: Document,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[TextChunk]:
    """Split a document into chunks and preserve its source metadata."""
    text_parts = split_text(
        document.content,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    chunks = []

    for index, text in enumerate(text_parts):
        chunk_id_source = (
            f"{document.source_url}|{document.content_hash}|{index}"
        )
        chunk_id = hashlib.sha256(
            chunk_id_source.encode("utf-8")
        ).hexdigest()

        chunks.append(
            TextChunk(
                chunk_id=chunk_id,
                source_url=document.source_url,
                title=document.title,
                chunk_index=index,
                text=text,
            )
        )

    return chunks
