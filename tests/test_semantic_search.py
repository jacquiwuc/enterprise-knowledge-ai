
import json

import numpy as np
import pytest

from app.processing import semantic_search


def write_embeddings(path, records):
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def test_load_embeddings_reads_valid_records(tmp_path):
    path = tmp_path / "embeddings.jsonl"

    write_embeddings(path, [
        {
            "chunk_id": "chunk-1",
            "embedding": [1.0, 0.0],
        }
    ])

    records = semantic_search.load_embeddings(path)

    assert len(records) == 1
    assert records[0]["chunk_id"] == "chunk-1"


def test_load_embeddings_raises_for_missing_file(tmp_path):
    path = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError):
        semantic_search.load_embeddings(path)


def test_search_rejects_blank_query(tmp_path):
    path = tmp_path / "embeddings.jsonl"

    with pytest.raises(ValueError, match="Query must not be empty"):
        semantic_search.search("   ", path)


def test_search_ranks_most_similar_first(tmp_path, monkeypatch):
    path = tmp_path / "embeddings.jsonl"

    write_embeddings(path, [
        {
            "chunk_id": "less-similar",
            "title": "Second",
            "embedding": [0.0, 1.0],
        },
        {
            "chunk_id": "most-similar",
            "title": "First",
            "embedding": [1.0, 0.0],
        },
    ])

    class FakeEmbedder:
        def embed_texts(self, texts):
            assert texts == ["test query"]
            return [[1.0, 0.0]]

    monkeypatch.setattr(
        semantic_search,
        "TextEmbedder",
        FakeEmbedder,
    )

    results = semantic_search.search(
        "test query",
        path,
        top_k=2,
    )

    assert results[0]["chunk_id"] == "most-similar"
    assert results[0]["score"] == pytest.approx(1.0)
    assert results[1]["chunk_id"] == "less-similar"
    assert results[1]["score"] == pytest.approx(0.0)
    assert "embedding" not in results[0]


def test_search_respects_top_k(tmp_path, monkeypatch):
    path = tmp_path / "embeddings.jsonl"

    write_embeddings(path, [
        {"chunk_id": "a", "embedding": [1.0, 0.0]},
        {"chunk_id": "b", "embedding": [0.8, 0.6]},
        {"chunk_id": "c", "embedding": [0.0, 1.0]},
    ])

    class FakeEmbedder:
        def embed_texts(self, texts):
            return [[1.0, 0.0]]

    monkeypatch.setattr(
        semantic_search,
        "TextEmbedder",
        FakeEmbedder,
    )

    results = semantic_search.search("query", path, top_k=2)

    assert len(results) == 2
    assert results[0]["chunk_id"] == "a"
