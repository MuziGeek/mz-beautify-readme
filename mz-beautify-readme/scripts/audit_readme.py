#!/usr/bin/env python3
"""Audit README image references, accessibility, and GitHub-safe SVG usage."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_TAG = re.compile(r"<img\b[^>]*>", re.I)
HTML_SOURCE_TAG = re.compile(r"<source\b[^>]*>", re.I)
HTML_SRC = re.compile(r"\bsrc=[\"']([^\"']+)[\"']", re.I)
HTML_SRCSET = re.compile(r"\bsrcset=[\"']([^\"']+)[\"']", re.I)
HTML_ALT = re.compile(r"\balt=[\"']([^\"']*)[\"']", re.I)
UNSAFE_TAGS = {"script", "foreignObject"}
REMOTE = ("http://", "https://", "//")


def local_target(src: str, base: Path) -> Path | None:
    if src.startswith((*REMOTE, "data:", "#")):
        return None
    clean = src.split("#", 1)[0].split("?", 1)[0]
    return (base / clean).resolve()


def audit_svg(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"invalid SVG XML: {exc}"]
    if "viewBox" not in root.attrib:
        issues.append("missing viewBox")
    found = {"title": False, "desc": False}
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag in found:
            found[tag] = True
        if tag in UNSAFE_TAGS:
            issues.append(f"contains unsupported <{tag}>")
        for key, value in node.attrib.items():
            name = key.rsplit("}", 1)[-1]
            if name in {"href", "src"} and value.strip().lower().startswith(REMOTE):
                issues.append(f"contains remote resource: {value}")
            if "url(http" in value.replace(" ", "").lower():
                issues.append("contains remote CSS resource")
    for name, present in found.items():
        if not present:
            issues.append(f"missing <{name}>")
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"@font-face|https?://[^\s\"')]+\.(?:woff2?|ttf|otf)", text, re.I):
        issues.append("contains remote or embedded font declaration")
    return list(dict.fromkeys(issues))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_readme.py path/to/README.md", file=sys.stderr)
        return 2
    readme = Path(sys.argv[1]).expanduser().resolve()
    if not readme.is_file():
        print(f"ERROR: README not found: {readme}", file=sys.stderr)
        return 2
    text = readme.read_text(encoding="utf-8")
    issues: list[str] = []
    sources = MARKDOWN_IMAGE.findall(text)
    for tag in HTML_TAG.findall(text):
        src = HTML_SRC.search(tag)
        if src:
            sources.append(src.group(1))
        alt = HTML_ALT.search(tag)
        if not alt or not alt.group(1).strip():
            issues.append(f"HTML image missing useful alt text: {tag[:120]}")
    for tag in HTML_SOURCE_TAG.findall(text):
        srcset = HTML_SRCSET.search(tag)
        if not srcset:
            issues.append(f"HTML source missing srcset: {tag[:120]}")
            continue
        for candidate in srcset.group(1).split(","):
            source = candidate.strip().split()[0] if candidate.strip() else ""
            if source:
                sources.append(source)
    checked = 0
    remote = 0
    for src in dict.fromkeys(sources):
        target = local_target(src, readme.parent)
        if target is None:
            if src.startswith(REMOTE):
                remote += 1
            continue
        checked += 1
        if not target.is_file():
            issues.append(f"missing image: {src}")
        elif target.suffix.lower() == ".svg":
            issues.extend(f"{src}: {issue}" for issue in audit_svg(target))
    print(f"README: {readme}")
    print(f"Local images checked: {checked}")
    print(f"Remote images observed: {remote}")
    if issues:
        print("README AUDIT FAILED", file=sys.stderr)
        print("\n".join(f"- {issue}" for issue in issues), file=sys.stderr)
        return 1
    print("README audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
