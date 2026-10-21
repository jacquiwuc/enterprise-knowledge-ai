
from app.ingestion import pipeline


def test_pipeline_continues_after_one_url_fails(monkeypatch):
    calls = []

    def fake_ingest_url(url):
        calls.append(url)

        if url == "https://example.org":
            raise TimeoutError("Simulated timeout")

        return True

    monkeypatch.setattr(pipeline, "ingest_url", fake_ingest_url)

    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    stats = pipeline.run_pipeline(urls)

    assert calls == urls
    assert stats == {
        "total": 3,
        "saved": 2,
        "skipped": 0,
        "failed": 1,
    }


def test_pipeline_counts_duplicates(monkeypatch):
    results = iter([True, False, False])

    monkeypatch.setattr(
        pipeline,
        "ingest_url",
        lambda url: next(results),
    )

    stats = pipeline.run_pipeline(
        [
            "https://example.com",
            "https://example.org",
            "https://example.net",
        ]
    )

    assert stats == {
        "total": 3,
        "saved": 1,
        "skipped": 2,
        "failed": 0,
    }


def test_pipeline_handles_empty_url_list():
    stats = pipeline.run_pipeline([])

    assert stats == {
        "total": 0,
        "saved": 0,
        "skipped": 0,
        "failed": 0,
    }
