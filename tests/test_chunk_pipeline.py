
import hashlib
import json

import pytest

from app.processing.chunk_pipeline import process_documents
from app.processing.models import Document


def make_document(content: str, title: str = "Example Page") -> Document:
    return Document(
        source_url="https://example.com",
        title=title,
        content=content,
        content_hash=hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest(),
    )


def write_document_jsonl(path, documents):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for document in documents:
            file.write(
                document.model_dump_json() + "\n"
            )


def test_process_documents_creates_chunks(tmp_path):
    input_path = tmp_path / "documents.jsonl"
    output_path = tmp_path / "chunks.jsonl"

    document = make_document("a" * 12)
    write_document_jsonl(input_path, [document])

    stats = process_documents(
        input_path,
        output_path,
        chunk_size=5,
        overlap=0,
    )

    assert stats == {
        "documents_processed": 1,
        "chunks_generated": 3,
        "chunks_saved": 3,
        "records_failed": 0,
    }

    records = [
        json.loads(line)
        for line in output_path.read_text(
            encoding="utf-8"
        ).splitlines()
    ]

    assert len(records) == 3
    assert records[0]["title"] == "Example Page"
    assert records[0]["chunk_index"] == 0
    assert records[0]["text"] == "aaaaa"


def test_process_documents_does_not_duplicate_chunks(tmp_path):
    input_path = tmp_path / "documents.jsonl"
    output_path = tmp_path / "chunks.jsonl"

    write_document_jsonl(
        input_path,
        [make_document("This is a test document.")],
    )

    first = process_documents(input_path, output_path)
    second = process_documents(input_path, output_path)

    assert first["chunks_saved"] > 0
    assert second["chunks_generated"] == first["chunks_generated"]
    assert second["chunks_saved"] == 0

    assert len(output_path.read_text(encoding="utf-8").splitlines()) == (
        first["chunks_saved"]
    )


def test_process_documents_rejects_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_documents(
            tmp_path / "missing.jsonl",
            tmp_path / "chunks.jsonl",
        )


def test_process_documents_continues_after_invalid_record(tmp_path):
    input_path = tmp_path / "documents.jsonl"
    output_path = tmp_path / "chunks.jsonl"

    valid_document = make_document("A valid document.")
    input_path.write_text(
        '{"not":"a valid Document"}\n'
        + valid_document.model_dump_json()
        + "\n",
        encoding="utf-8",
    )

    stats = process_documents(input_path, output_path)

    assert stats["records_failed"] == 1
    assert stats["documents_processed"] == 1
    assert stats["chunks_saved"] > 0


def test_process_documents_skips_blank_lines(tmp_path):
    input_path = tmp_path / "documents.jsonl"
    output_path = tmp_path / "chunks.jsonl"

    document = make_document("A valid document.")
    input_path.write_text(
        "\n" + document.model_dump_json() + "\n\n",
        encoding="utf-8",
    )

    stats = process_documents(input_path, output_path)

    assert stats["documents_processed"] == 1
    assert stats["records_failed"] == 0
