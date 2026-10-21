
import json

from app.processing.chunk_models import TextChunk
from app.processing.chunk_storage import save_chunks


def make_chunk(chunk_id: str, text: str) -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        source_url="https://example.com",
        title="Example Page",
        chunk_index=0,
        text=text,
    )


def test_save_chunks_creates_jsonl_file(tmp_path):
    output_path = tmp_path / "processed" / "chunks.jsonl"
    chunks = [
        make_chunk("chunk-001", "First chunk"),
        make_chunk("chunk-002", "Second chunk"),
    ]

    saved_count = save_chunks(chunks, output_path)

    assert saved_count == 2
    assert output_path.exists()

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    records = [json.loads(line) for line in lines]
    assert records[0]["chunk_id"] == "chunk-001"
    assert records[1]["text"] == "Second chunk"


def test_save_chunks_preserves_unicode(tmp_path):
    output_path = tmp_path / "chunks.jsonl"
    chunk = make_chunk("chunk-003", "企业知识智能平台")

    save_chunks([chunk], output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "企业知识智能平台" in content


def test_save_chunks_skips_existing_chunk_ids(tmp_path):
    output_path = tmp_path / "chunks.jsonl"
    chunk = make_chunk("chunk-001", "First chunk")

    assert save_chunks([chunk], output_path) == 1
    assert save_chunks([chunk], output_path) == 0

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_save_chunks_skips_duplicate_ids_in_same_batch(tmp_path):
    output_path = tmp_path / "chunks.jsonl"
    chunks = [
        make_chunk("chunk-001", "First version"),
        make_chunk("chunk-001", "Duplicate version"),
    ]

    assert save_chunks(chunks, output_path) == 1

    records = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(records) == 1
    assert records[0]["text"] == "First version"


def test_save_chunks_with_empty_input_does_not_create_file(tmp_path):
    output_path = tmp_path / "chunks.jsonl"

    assert save_chunks([], output_path) == 0
    assert not output_path.exists()
