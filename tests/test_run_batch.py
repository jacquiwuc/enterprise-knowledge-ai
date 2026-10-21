
import app.ingestion.run_batch as run_batch


def test_main_runs_batch_with_configured_urls(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "urls.txt").write_text(
        "https://example.com\nhttps://www.iana.org\n",
        encoding="utf-8",
    )

    captured = {}

    def fake_ingest_urls(urls):
        captured["urls"] = urls
        return {
            "total": 2,
            "succeeded": 1,
            "skipped": 1,
            "failed": 0,
        }

    monkeypatch.setattr(run_batch, "ingest_urls", fake_ingest_urls)

    assert run_batch.main() == 0
    assert captured["urls"] == [
        "https://example.com",
        "https://www.iana.org",
    ]


def test_main_returns_error_when_config_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert run_batch.main() == 1


def test_main_returns_success_when_url_list_is_empty(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "urls.txt").write_text("", encoding="utf-8")

    def unexpected_ingest(urls):
        raise AssertionError("Batch should not run for an empty URL list")

    monkeypatch.setattr(run_batch, "ingest_urls", unexpected_ingest)

    assert run_batch.main() == 0


def test_main_returns_error_when_batch_has_failures(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "urls.txt").write_text(
        "https://example.com\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        run_batch,
        "ingest_urls",
        lambda urls: {
            "total": 1,
            "succeeded": 0,
            "skipped": 0,
            "failed": 1,
        },
    )

    assert run_batch.main() == 1
