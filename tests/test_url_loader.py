
import pytest

from app.ingestion.url_loader import load_urls


def test_load_urls_ignores_blank_lines_and_comments(tmp_path):
    config_path = tmp_path / "urls.txt"
    config_path.write_text(
        "# Public test websites\n"
        "\n"
        "https://example.com\n"
        "  https://www.iana.org  \n",
        encoding="utf-8",
    )

    result = load_urls(config_path)

    assert result == [
        "https://example.com",
        "https://www.iana.org",
    ]


def test_load_urls_missing_file_raises_error(tmp_path):
    config_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        load_urls(config_path)


def test_load_urls_rejects_invalid_url(tmp_path):
    config_path = tmp_path / "urls.txt"
    config_path.write_text(
        "not-a-valid-url\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid URL"):
        load_urls(config_path)


def test_load_urls_rejects_unsupported_scheme(tmp_path):
    config_path = tmp_path / "urls.txt"
    config_path.write_text(
        "ftp://example.com/file\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid URL"):
        load_urls(config_path)


def test_load_urls_empty_file_returns_empty_list(tmp_path):
    config_path = tmp_path / "urls.txt"
    config_path.write_text("", encoding="utf-8")

    assert load_urls(config_path) == []
