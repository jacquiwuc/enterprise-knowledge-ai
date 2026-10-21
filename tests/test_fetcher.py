import logging
import httpx
import pytest

from app.ingestion.fetcher import fetch_html


def test_fetch_html_success(monkeypatch):
    url = "https://example.com"
    request = httpx.Request("GET", url)
    response = httpx.Response(
        200,
        text="<html><title>Example</title></html>",
        request=request,
    )

    def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "get", fake_get)

    html = fetch_html(url)

    assert "<title>Example</title>" in html


def test_fetch_html_http_error(monkeypatch):
    url = "https://example.com/missing"
    request = httpx.Request("GET", url)
    response = httpx.Response(
        404,
        request=request,
    )

    def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_html(url)


def test_fetch_html_timeout(monkeypatch):
    url = "https://example.com"

    def fake_get(*args, **kwargs):
        raise httpx.TimeoutException(
            "Request timed out",
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(httpx.TimeoutException):
        fetch_html(url)


def test_fetch_html_logs_http_error(monkeypatch, caplog):
    url = "https://example.com/missing"
    request = httpx.Request("GET", url)
    response = httpx.Response(404, request=request)

    def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "get", fake_get)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(httpx.HTTPStatusError):
            fetch_html(url)

    assert "HTTP status error" in caplog.text
    assert url in caplog.text

