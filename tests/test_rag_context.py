
import pytest

from app.processing.rag_context import build_context


def test_build_context_includes_source_and_text():
    results = [
        {
            "title": "Example Domain",
            "source_url": "https://example.com/",
            "text": "This domain is for documentation examples.",
            "score": 0.8,
        }
    ]

    context = build_context(results)

    assert "Example Domain" in context
    assert "https://example.com/" in context
    assert "This domain is for documentation examples." in context
    assert "0.8000" in context


def test_build_context_skips_empty_text():
    results = [
        {"title": "Empty", "text": "   "},
        {"title": "Useful", "text": "Useful information"},
    ]

    context = build_context(results)

    assert "Empty" not in context
    assert "Useful information" in context


def test_build_context_respects_max_chars():
    results = [
        {
            "title": "Example",
            "source_url": "https://example.com/",
            "text": "A" * 1000,
        }
    ]

    context = build_context(results, max_chars=100)

    assert len(context) <= 100


def test_build_context_rejects_invalid_max_chars():
    with pytest.raises(ValueError, match="max_chars"):
        build_context([], max_chars=0)


def test_build_context_handles_empty_results():
    assert build_context([]) == ""
