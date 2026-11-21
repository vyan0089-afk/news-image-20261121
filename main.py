#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 entry, THE TWENTY-FIRST.

The front page is drawn ahead of time by generate.py and shipped in this
repository as entry.png. All this program does is place those exact bytes
where the grader looks for them. Pure standard library, no network, no
randomness: the bytes written out are always the bytes shipped in.
"""

import os
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    picture = repo_root / "entry.png"
    payload = picture.read_bytes()
    destination_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination_dir.mkdir(parents=True, exist_ok=True)
    (destination_dir / "entry.png").write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
