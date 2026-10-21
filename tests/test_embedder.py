
import numpy as np
import pytest

from app.processing.embedder import TextEmbedder


def test_embed_texts_returns_empty_list_for_empty_input():
    embedder = TextEmbedder.__new__(TextEmbedder)

    assert embedder.embed_texts([]) == []


def test_embed_texts_rejects_blank_text():
    embedder = TextEmbedder.__new__(TextEmbedder)

    with pytest.raises(ValueError, match="empty strings"):
        embedder.embed_texts(["hello", "   "])


def test_embed_texts_returns_vectors():
    embedder = TextEmbedder.__new__(TextEmbedder)

    class FakeModel:
        def encode(self, texts, **kwargs):
            assert texts == ["hello", "world"]
            assert kwargs["normalize_embeddings"] is True
            assert kwargs["convert_to_numpy"] is True

            return np.array([
                [0.6, 0.8],
                [1.0, 0.0],
            ])

    embedder.model = FakeModel()

    result = embedder.embed_texts(["hello", "world"])

    assert result == [[0.6, 0.8], [1.0, 0.0]]
