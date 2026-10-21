
import pytest
from pydantic import ValidationError

from app.processing.chunk_models import TextChunk


def test_text_chunk_accepts_valid_data():
    chunk = TextChunk(
        chunk_id="example-000",
        source_url="https://example.com",
        title="Example Page",
        chunk_index=0,
        text="This is a test chunk.",
    )

    assert chunk.chunk_id == "example-000"
    assert str(chunk.source_url) == "https://example.com/"
    assert chunk.title == "Example Page"
    assert chunk.chunk_index == 0
    assert chunk.text == "This is a test chunk."


def test_text_chunk_rejects_negative_index():
    with pytest.raises(ValidationError):
        TextChunk(
            chunk_id="example-001",
            source_url="https://example.com",
            title="Example Page",
            chunk_index=-1,
            text="Test content",
        )


def test_text_chunk_rejects_empty_text():
    with pytest.raises(ValidationError):
        TextChunk(
            chunk_id="example-002",
            source_url="https://example.com",
            title="Example Page",
            chunk_index=0,
            text="",
        )


def test_text_chunk_rejects_empty_title():
    with pytest.raises(ValidationError):
        TextChunk(
            chunk_id="example-003",
            source_url="https://example.com",
            title="",
            chunk_index=0,
            text="Test content",
        )
