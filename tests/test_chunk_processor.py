
import pytest

from app.processing.chunk_processor import create_chunks
from app.processing.models import Document


def make_document(content: str) -> Document:
    import hashlib

    return Document(
        source_url="https://example.com",
        title="Example Page",
        content=content,
        content_hash=hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest(),
    )


def test_create_chunks_preserves_source_metadata():
    document = make_document("a" * 12)

    chunks = create_chunks(
        document,
        chunk_size=5,
        overlap=0,
    )

    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert all(chunk.title == "Example Page" for chunk in chunks)
    assert all(
        str(chunk.source_url) == "https://example.com/"
        for chunk in chunks
    )
    assert [chunk.text for chunk in chunks] == [
        "aaaaa",
        "aaaaa",
        "aa",
    ]


def test_create_chunks_generates_stable_ids():
    document = make_document("This is a document with enough text.")

    first = create_chunks(document, chunk_size=10, overlap=2)
    second = create_chunks(document, chunk_size=10, overlap=2)

    assert [chunk.chunk_id for chunk in first] == [
        chunk.chunk_id for chunk in second
    ]


def test_create_chunks_returns_empty_list_for_whitespace_content():
    document = make_document("   ")

    assert create_chunks(document) == []


def test_create_chunks_rejects_invalid_chunk_parameters():
    document = make_document("Some text")

    with pytest.raises(ValueError, match="chunk_size"):
        create_chunks(document, chunk_size=0)

    with pytest.raises(ValueError, match="overlap"):
        create_chunks(document, chunk_size=10, overlap=10)
