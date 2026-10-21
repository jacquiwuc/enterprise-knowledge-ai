import json
from pathlib import Path


def load_existing_hashes(path: Path) -> set[str]:
    if not path.exists():
        return set()

    hashes = set()

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            hashes.add(record["content_hash"])

    return hashes
