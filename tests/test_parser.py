import pytest

from app.ingestion.parser import parse_html


def test_parse_html_extracts_title_and_content():
    html = """
    <html>
      <head><title>Transfer FAQ</title></head>
      <body>
        <p>International transfer fees may apply.</p>
        <script>ignore this script</script>
      </body>
    </html>
    """

    document = parse_html(
        html,
        "https://example.com/faq",
    )

    assert document.title == "Transfer FAQ"
    assert "International transfer fees may apply." in document.content
    assert "ignore this script" not in document.content
    assert len(document.content_hash) == 64


def test_parse_html_rejects_missing_title():
    html = "<html><body><p>Some content</p></body></html>"

    with pytest.raises(ValueError, match="no usable title"):
        parse_html(html, "https://example.com/no-title")
