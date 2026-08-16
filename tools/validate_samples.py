#!/usr/bin/env python3
"""Validate README sample provenance and copied asset hashes."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "docs" / "readme" / "samples"
MANIFEST = SAMPLES / "provenance.json"
LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def main() -> int:
    errors: list[str] = []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if data.get("format") != "mz.readme-samples/1" or data.get("status") != "READY_FOR_REVIEW":
        errors.append("unexpected sample manifest identity or status")
    samples = data.get("samples")
    if not isinstance(samples, list) or len(samples) != 2:
        errors.append("samples must contain exactly the Icon Design and Visual Engine cases")
        samples = []
    repositories: set[str] = set()
    for sample_index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            errors.append(f"samples[{sample_index}] must be an object")
            continue
        repository = sample.get("repository")
        if not isinstance(repository, str) or repository in repositories:
            errors.append(f"samples[{sample_index}] repository must be unique")
        else:
            repositories.add(repository)
        digest = sample.get("sourceManifestSha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"samples[{sample_index}] has invalid sourceManifestSha256")
        pairs: set[tuple[str, str]] = set()
        for asset_index, asset in enumerate(sample.get("assets", [])):
            label = f"samples[{sample_index}].assets[{asset_index}]"
            if not isinstance(asset, dict):
                errors.append(f"{label} must be an object")
                continue
            relative = asset.get("path")
            locale = asset.get("locale")
            viewport = asset.get("viewport")
            digest = asset.get("sha256")
            pure = PurePosixPath(relative) if isinstance(relative, str) else None
            if pure is None or pure.is_absolute() or ".." in pure.parts:
                errors.append(f"{label}.path must be sample-relative")
                continue
            pair = (locale, viewport)
            if not isinstance(locale, str) or not LOCALE.fullmatch(locale) or viewport not in {"desktop", "mobile"}:
                errors.append(f"{label} has invalid locale or viewport")
            elif pair in pairs:
                errors.append(f"{label} duplicates locale and viewport")
            else:
                pairs.add(pair)
            target = SAMPLES / Path(*pure.parts)
            if not target.is_file():
                errors.append(f"{label} missing: {relative}")
            elif not isinstance(digest, str) or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                errors.append(f"{label} hash mismatch: {relative}")
        if pairs != {("en", "desktop"), ("en", "mobile"), ("zh-CN", "desktop"), ("zh-CN", "mobile")}:
            errors.append(f"samples[{sample_index}] must provide both locales at desktop and mobile viewports")
    if repositories != {"MuziGeek/mz-icon-design", "MuziGeek/mz-visual-engine"}:
        errors.append("sample repository set is incomplete")
    if errors:
        print("SAMPLE VALIDATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("README sample provenance validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
