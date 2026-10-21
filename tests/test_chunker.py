
import pytest

from app.processing.chunker import split_text


def test_empty_text_returns_empty_list():
    assert split_text("") == []
    assert split_text("   ") == []

def test_short_text_returns_one_chunk():
    assert split_text(
        "Hello world",
        chunk_size=20,
        overlap=0,
    ) == ["Hello world"]


def test_long_text_is_split_into_chunks():
    text = "a" * 12

    chunks = split_text(text, chunk_size=5, overlap=0)

    assert chunks == ["aaaaa", "aaaaa", "aa"]
    assert "".join(chunks) == text


def test_chunks_have_expected_overlap():
    text = "abcdefghijkl"

    chunks = split_text(text, chunk_size=6, overlap=2)

    assert chunks == ["abcdef", "efghij", "ijkl"]
    assert chunks[0][-2:] == chunks[1][:2]
    assert chunks[1][-2:] == chunks[2][:2]


def test_chunk_size_must_be_positive():
    with pytest.raises(ValueError, match="chunk_size"):
        split_text("hello", chunk_size=0)


def test_overlap_cannot_be_negative():
    with pytest.raises(ValueError, match="overlap"):
        split_text("hello", overlap=-1)


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError, match="overlap"):
        split_text("hello", chunk_size=5, overlap=5)
