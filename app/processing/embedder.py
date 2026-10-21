
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class TextEmbedder:
    """Generate text embeddings using a Sentence Transformers model."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Convert texts into normalized embedding vectors."""
        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("Texts must not contain empty strings")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings.tolist()
