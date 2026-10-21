
from app.processing.embedder import TextEmbedder


def main():
    embedder = TextEmbedder()

    texts = [
        "Westpac provides banking services.",
        "A bank offers financial products to customers.",
    ]

    vectors = embedder.embed_texts(texts)

    print("Number of texts:", len(texts))
    print("Embedding dimension:", len(vectors[0]))
    print("First vector length:", len(vectors[0]))
    print("First vector sample:", vectors[0][:5])


if __name__ == "__main__":
    main()
