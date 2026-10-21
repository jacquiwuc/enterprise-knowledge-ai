from app.ingestion.storage import save_if_new
import json

from app.ingestion.storage import save_document
from app.processing.deduplicator import load_existing_hashes
from app.processing.models import Document


def make_document() -> Document:
    return Document(
        source_url="https://example.com/faq",
        title="Transfer FAQ",
        content="International transfer fees may apply.",
        content_hash="a" * 64,
    )


def test_save_document_creates_jsonl_file(tmp_path):
    output_path = tmp_path / "documents.jsonl"
    document = make_document()

    save_document(document, output_path)

    assert output_path.exists()


def test_saved_document_is_valid_jsonl(tmp_path):
    output_path = tmp_path / "documents.jsonl"
    document = make_document()

    save_document(document, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    record = json.loads(lines[0])

    assert record["title"] == "Transfer FAQ"
    assert record["content"] == "International transfer fees may apply."
    assert record["content_hash"] == "a" * 64
    assert record["source_url"] == "https://example.com/faq"


def test_missing_file_returns_empty_hashes(tmp_path):
    output_path = tmp_path / "does_not_exist.jsonl"

    hashes = load_existing_hashes(output_path)

    assert hashes == set()
    assert not output_path.exists()


def test_existing_hash_is_loaded(tmp_path):
    output_path = tmp_path / "documents.jsonl"
    document = make_document()

    save_document(document, output_path)

    hashes = load_existing_hashes(output_path)

    assert document.content_hash in hashes
    assert len(hashes) == 1


def test_duplicate_document_is_not_written_twice(tmp_path):
    output_path = tmp_path / "documents.jsonl"
    document = make_document()

    first_result = save_if_new(document, output_path)
    second_result = save_if_new(document, output_path)

    assert first_result is True
    assert second_result is False

    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

