#!/usr/bin/env python3
"""Verify the vendored beautify-github-readme snapshot without network access."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream-lock.json"


def main() -> int:
    try:
        data = json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"UPSTREAM SNAPSHOT INVALID: {exc}", file=sys.stderr)
        return 1
    errors: list[str] = []
    if data.get("format") != "mz.upstream-snapshot/1":
        errors.append("unexpected lock format")
    if data.get("repository") != "oil-oil/beautify-github-readme":
        errors.append("unexpected upstream repository")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        errors.append("lock has no files")
        files = []
    for item in files:
        relative = item.get("path", "")
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing snapshot file: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item.get("sha256"):
            errors.append(f"snapshot hash mismatch: {relative}")
    if errors:
        print("UPSTREAM SNAPSHOT INVALID", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Upstream snapshot verified: {data['repository']}@{data['commit']}")
    print(f"Files checked: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
