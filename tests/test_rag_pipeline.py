
import pytest

from app.processing import rag_pipeline


def test_retrieve_context_combines_search_and_context(monkeypatch):
    fake_results = [
        {
            "chunk_id": "chunk-1",
            "title": "Example Domain",
            "source_url": "https://example.com/",
            "text": "Example content",
            "score": 0.9,
        }
    ]

    def fake_search(question, top_k):
        assert question == "test question"
        assert top_k == 2
        return fake_results

    def fake_build_context(results, max_chars):
        assert results == fake_results
        assert max_chars == 500
        return "Example context"

    monkeypatch.setattr(rag_pipeline, "search", fake_search)
    monkeypatch.setattr(rag_pipeline, "build_context", fake_build_context)

    result = rag_pipeline.retrieve_context(
        "test question",
        top_k=2,
        max_context_chars=500,
    )

    assert result["question"] == "test question"
    assert result["context"] == "Example context"
    assert result["result_count"] == 1
    assert result["sources"][0]["chunk_id"] == "chunk-1"


def test_retrieve_context_rejects_blank_question():
    with pytest.raises(ValueError, match="Question must not be empty"):
        rag_pipeline.retrieve_context("   ")


def test_retrieve_context_rejects_invalid_top_k():
    with pytest.raises(ValueError, match="top_k"):
        rag_pipeline.retrieve_context("question", top_k=0)


def test_retrieve_context_rejects_invalid_context_limit():
    with pytest.raises(ValueError, match="max_context_chars"):
        rag_pipeline.retrieve_context("question", max_context_chars=0)


def test_retrieve_context_handles_no_results(monkeypatch):
    monkeypatch.setattr(rag_pipeline, "search", lambda question, top_k: [])
    monkeypatch.setattr(
        rag_pipeline,
        "build_context",
        lambda results, max_chars: "",
    )

    result = rag_pipeline.retrieve_context("unknown question")

    assert result["context"] == ""
    assert result["sources"] == []
    assert result["result_count"] == 0
