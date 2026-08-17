#!/usr/bin/env python3
"""Validate the local MZ Beautify README repository and public payload."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = ROOT.name
PAYLOAD = ROOT / SKILL_ID
MANIFEST = ROOT / "PUBLIC_MANIFEST.json"
ALLOWED_ROOTS = {
    ".gitattributes", ".gitignore", "LICENSE", "NOTICE.md",
    "PUBLIC_MANIFEST.json", "README.md", "README.zh-CN.md", "docs", SKILL_ID, "tools",
}
FORBIDDEN_PARTS = {"raw", "rejected", "tmp", "__pycache__", ".pytest_cache"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
TEXT_EXTENSIONS = {".json", ".md", ".py", ".svg", ".txt", ".yaml", ".yml"}
BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
FORBIDDEN_TEXT = (
    (re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}"), "possible secret"),
    (re.compile(r"(?i)[a-z]:\\(?:users|gitproject|muzi)\\", re.ASCII), "Windows absolute path"),
    (re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"), "email address"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "Chinese mobile number"),
    (re.compile("|".join((
        "muzi-(?:core|character|icon|knowledge|zine|readme)",
        "PFan" + "HuTuTi",
        "Muzi Visual " + "Overlay",
        "muzi-" + "crayon",
        "assets/" + "identity",
        "extensions/" + "muzi",
    )), re.IGNORECASE), "private visual identifier"),
)


def repository_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(ROOT).parts
        and "release" not in path.relative_to(ROOT).parts
        and not FORBIDDEN_PARTS.intersection(part.lower() for part in path.relative_to(ROOT).parts)
    )


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def tree_hash() -> str:
    rows: list[str] = []
    paths = (item for item in repository_files() if PAYLOAD in item.parents)
    for path in sorted(paths, key=lambda item: item.relative_to(PAYLOAD).as_posix()):
        relative = path.relative_to(PAYLOAD).as_posix()
        rows.append(f"{relative}\t{hashlib.sha256(normalized_bytes(path)).hexdigest()}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def validate_markdown_links(path: Path, errors: list[str]) -> None:
    # Vendored upstream Markdown is byte-locked and its relative links are
    # intentionally resolved by the root orchestrator rather than rewritten.
    if (PAYLOAD / "references" / "upstream") in path.parents:
        return
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        clean = target.split("#", 1)[0]
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        if not (path.parent / clean).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")


def main() -> int:
    errors: list[str] = []
    if not (PAYLOAD / "SKILL.md").is_file():
        errors.append(f"Missing payload: {SKILL_ID}/SKILL.md")
    for path in repository_files():
        relative = path.relative_to(ROOT)
        if relative.parts[0] not in ALLOWED_ROOTS:
            errors.append(f"Unexpected root path: {relative.as_posix()}")
        suffix = path.suffix.lower()
        if suffix in BINARY_EXTENSIONS:
            if "assets" not in {part.lower() for part in relative.parts} and "docs" not in {part.lower() for part in relative.parts}:
                errors.append(f"Binary outside assets/docs: {relative.as_posix()}")
            continue
        if path.name not in TEXT_NAMES and suffix not in TEXT_EXTENSIONS:
            errors.append(f"Undeclared file type: {relative.as_posix()}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in FORBIDDEN_TEXT:
            if label == "private visual identifier" and path == Path(__file__).resolve():
                continue
            scan = re.sub(r"(?i)\b[0-9a-f]{64}\b", "<sha256>", text) if label == "Chinese mobile number" else text
            if pattern.search(scan):
                errors.append(f"{relative.as_posix()}: {label}")
        if suffix == ".md":
            validate_markdown_links(path, errors)
        if suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative.as_posix()}: invalid JSON: {exc}")

    skill_text = (PAYLOAD / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n"):
        errors.append("SKILL.md lacks YAML frontmatter")
    else:
        _, frontmatter, _ = skill_text.split("---\n", 2)
        keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
        if keys != ["name", "description"]:
            errors.append("SKILL.md frontmatter keys must be exactly name and description")
        if f"name: {SKILL_ID}" not in frontmatter:
            errors.append("SKILL.md name does not match repository payload")

    for name in ("LICENSE", "NOTICE.md", "THIRD_PARTY_NOTICES.md"):
        if not (PAYLOAD / name).is_file():
            errors.append(f"Payload lacks {name}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("format") != "mz.public-skill/1" or manifest.get("version") != "1.0.0":
        errors.append("PUBLIC_MANIFEST.json has an unexpected format or version")
    if manifest.get("repository") != f"MuziGeek/{SKILL_ID}":
        errors.append("PUBLIC_MANIFEST.json repository mismatch")
    skill = manifest.get("skill", {})
    if skill.get("id") != SKILL_ID or skill.get("directory") != SKILL_ID:
        errors.append("PUBLIC_MANIFEST.json Skill identity mismatch")
    actual = tree_hash()
    if skill.get("treeHash") != actual:
        errors.append(f"Skill tree hash mismatch: expected {actual}")
    if manifest.get("release", {}).get("tag") != "v1.0.0":
        errors.append("release tag mismatch")

    verifier = PAYLOAD / "scripts" / "verify_upstream_snapshot.py"
    result = subprocess.run([sys.executable, str(verifier)], text=True, capture_output=True)
    if result.returncode:
        errors.append(f"upstream snapshot verification failed: {result.stdout}{result.stderr}".strip())

    snapshot = PAYLOAD / "references" / "visual-engine"
    snapshot_manifest = json.loads((snapshot / "engine-snapshot.json").read_text(encoding="utf-8"))
    compat = json.loads((PAYLOAD / "references" / "mz-engine-compat.json").read_text(encoding="utf-8"))
    snapshot_verifier = snapshot / "scripts" / "verify_snapshot.py"
    result = subprocess.run([sys.executable, str(snapshot_verifier), str(snapshot)], text=True, capture_output=True)
    if result.returncode:
        errors.append(f"MZ Visual Engine snapshot verification failed: {result.stdout}{result.stderr}".strip())
    if any(snapshot_manifest.get(key) != compat.get(key) for key in ("engineVersion", "target", "snapshotHash", "sourceCatalogHash")):
        errors.append("MZ Visual Engine compatibility declaration does not match the bundled Snapshot")

    engine = manifest.get("visualEngine", {})
    if (
        engine.get("version") != "2.0.0"
        or engine.get("snapshotHash") != snapshot_manifest.get("snapshotHash")
        or engine.get("sourceCatalogHash") != snapshot_manifest.get("sourceCatalogHash")
    ):
        errors.append("PUBLIC_MANIFEST.json Visual Engine declaration mismatch")

    quick = ROOT / "tools" / "quick_validate.py"
    if quick.is_file():
        result = subprocess.run([sys.executable, str(quick), str(PAYLOAD)], text=True, capture_output=True)
        if result.returncode:
            errors.append(f"quick validation failed: {result.stdout}{result.stderr}".strip())

    showcase_checks = (
        ("Skill tests", PAYLOAD / "scripts" / "test_mz_beautify_readme.py", []),
        ("English README audit", PAYLOAD / "scripts" / "audit_readme.py", [ROOT / "README.md"]),
        ("Chinese README audit", PAYLOAD / "scripts" / "audit_readme.py", [ROOT / "README.zh-CN.md"]),
    )
    for label, script, arguments in showcase_checks:
        result = subprocess.run([sys.executable, str(script), *map(str, arguments)], text=True, capture_output=True)
        if result.returncode:
            errors.append(f"{label} failed: {result.stdout}{result.stderr}".strip())

    if errors:
        print("PUBLIC VALIDATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Public release validation passed: {SKILL_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
