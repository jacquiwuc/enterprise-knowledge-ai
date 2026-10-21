
from unittest.mock import call

import pytest

import app.ingestion.batch_fetcher as batch_fetcher


def test_ingest_urls_all_succeed(monkeypatch):
    urls = ["https://example.com/a", "https://example.com/b"]

    monkeypatch.setattr(
        batch_fetcher,
        "ingest_url",
        lambda url: True,
    )

    result = batch_fetcher.ingest_urls(urls)

    assert result == {
        "total": 2,
        "succeeded": 2,
        "skipped": 0,
        "failed": 0,
    }


def test_ingest_urls_continues_after_failure(monkeypatch):
    urls = [
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/c",
    ]
    processed = []

    def fake_ingest_url(url):
        processed.append(url)

        if url == urls[1]:
            raise TimeoutError("Request timed out")

        return True

    monkeypatch.setattr(
        batch_fetcher,
        "ingest_url",
        fake_ingest_url,
    )

    result = batch_fetcher.ingest_urls(urls)

    assert processed == urls
    assert result == {
        "total": 3,
        "succeeded": 2,
        "skipped": 0,
        "failed": 1,
    }


def test_ingest_urls_counts_skipped_documents(monkeypatch):
    monkeypatch.setattr(
        batch_fetcher,
        "ingest_url",
        lambda url: url.endswith("/new"),
    )

    result = batch_fetcher.ingest_urls([
        "https://example.com/existing",
        "https://example.com/new",
    ])

    assert result == {
        "total": 2,
        "succeeded": 1,
        "skipped": 1,
        "failed": 0,
    }


def test_ingest_urls_empty_input():
    result = batch_fetcher.ingest_urls([])

    assert result == {
        "total": 0,
        "succeeded": 0,
        "skipped": 0,
        "failed": 0,
    }


def test_ingest_urls_logs_failure(monkeypatch, caplog):
    import logging

    def fail(url):
        raise ValueError("Invalid URL")

    monkeypatch.setattr(batch_fetcher, "ingest_url", fail)

    with caplog.at_level(logging.ERROR):
        result = batch_fetcher.ingest_urls([
            "https://example.com/bad"
        ])

    assert result["failed"] == 1
    assert "Batch ingestion failed" in caplog.text
    assert "Invalid URL" in caplog.text
