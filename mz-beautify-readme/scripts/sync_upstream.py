#!/usr/bin/env python3
"""Check or refresh the pinned upstream design-core snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream-lock.json"
REPOSITORY = "oil-oil/beautify-github-readme"
DEFAULT_COMMIT = "55bdb1c05414cd7a0cf911d02e55ece79777206e"
UPSTREAM_ROOT = "skills/beautify-github-readme"
FILES = (
    ("SKILL.md", "references/upstream/SKILL.md"),
    ("references/content-architecture.md", "references/upstream/content-architecture.md"),
    ("references/github-readme-canvas.md", "references/upstream/github-readme-canvas.md"),
    ("references/hybrid-svg-production.md", "references/upstream/hybrid-svg-production.md"),
    ("references/motion-production.md", "references/upstream/motion-production.md"),
    ("references/project-native-hero.md", "references/upstream/project-native-hero.md"),
    ("references/showcase-contribution.md", "references/upstream/showcase-contribution.md"),
    ("references/svg-production.md", "references/upstream/svg-production.md"),
    ("references/visual-direction.md", "references/upstream/visual-direction.md"),
    ("scripts/audit_readme.py", "scripts/upstream/audit_readme.py"),
    ("scripts/render_motion_gif.py", "scripts/upstream/render_motion_gif.py"),
)


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "mz-beautify-readme-sync/0.2"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def resolve_commit(ref: str) -> str:
    if len(ref) == 40 and all(char in "0123456789abcdef" for char in ref.lower()):
        return ref.lower()
    url = f"https://api.github.com/repos/{REPOSITORY}/commits/{ref}"
    return json.loads(request_bytes(url).decode("utf-8"))["sha"]


def apply(commit: str) -> None:
    entries: list[dict[str, str]] = []
    for source, relative in FILES:
        url = f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/{UPSTREAM_ROOT}/{source}"
        data = request_bytes(url)
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append({"source": f"{UPSTREAM_ROOT}/{source}", "path": relative, "sha256": hashlib.sha256(data).hexdigest()})
        print(relative)
    lock = {
        "format": "mz.upstream-snapshot/1",
        "repository": REPOSITORY,
        "commit": commit,
        "license": "MIT",
        "files": entries,
    }
    LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(LOCK.relative_to(ROOT))


def check() -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    locked = lock["commit"]
    current = resolve_commit("main")
    print(f"locked={locked}")
    print(f"upstream_main={current}")
    print("up_to_date=" + ("yes" if locked == current else "no"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--commit", default=DEFAULT_COMMIT, help="40-character commit or GitHub ref")
    args = parser.parse_args()
    if args.check:
        return check()
    apply(resolve_commit(args.commit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
