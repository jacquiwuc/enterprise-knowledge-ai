
from pathlib import Path
from urllib.parse import urlparse


def load_urls(config_path: Path) -> list[str]:
    """Load valid HTTP(S) URLs from a text file."""
    if not config_path.exists():
        raise FileNotFoundError(
            f"URL configuration file not found: {config_path}"
        )

    urls = []

    for line_number, line in enumerate(
        config_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        url = line.strip()

        # Ignore blank lines and comments.
        if not url or url.startswith("#"):
            continue

        parsed = urlparse(url)

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
        ):
            raise ValueError(
                f"Invalid URL at line {line_number}: {url}"
            )

        urls.append(url)

    return urls
