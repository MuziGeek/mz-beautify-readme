#!/usr/bin/env python3
"""Validate an mz.readme-asset/3 manifest and all declared hashes."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

UPSTREAM = "55bdb1c05414cd7a0cf911d02e55ece79777206e"
LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def check_file(item: object, root: Path, label: str, errors: list[str]) -> None:
    if not isinstance(item, dict): errors.append(f"{label} must be an object"); return
    if not {"path", "sha256"} <= set(item): errors.append(f"{label} requires path and sha256"); return
    if set(item) - {"path", "sha256", "role", "license", "locale", "viewport"}: errors.append(f"{label} has unknown fields")
    if "locale" in item and (not isinstance(item["locale"], str) or not LOCALE.fullmatch(item["locale"])): errors.append(f"{label}.locale must be a BCP 47-style tag")
    if "viewport" in item and item["viewport"] not in {"desktop", "mobile", "responsive"}: errors.append(f"{label}.viewport is invalid")
    relative, expected = item.get("path"), item.get("sha256")
    if not isinstance(relative, str) or not relative: errors.append(f"{label}.path must be non-empty"); return
    pure = PurePosixPath(relative.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts or ':' in relative: errors.append(f"{label}.path must be repository-relative"); return
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected): errors.append(f"{label}.sha256 must be lowercase SHA-256"); return
    path = (root / Path(*pure.parts)).resolve()
    try: path.relative_to(root.resolve())
    except ValueError: errors.append(f"{label}.path escapes manifest root"); return
    if not path.is_file(): errors.append(f"{label} missing: {relative}"); return
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected: errors.append(f"{label} hash mismatch: {relative}")


def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data, dict): return ["manifest root must be an object"]
    errors: list[str] = []
    required = {"format", "status", "repository", "upstreamCore", "brief", "visualBrief", "publishedAsset", "sources", "validation"}
    allowed = required | {"variants", "localization", "extension", "review"}
    if required - set(data): errors.append(f"missing fields: {', '.join(sorted(required-set(data)))}")
    if set(data) - allowed: errors.append(f"unknown fields: {', '.join(sorted(set(data)-allowed))}")
    if data.get("format") != "mz.readme-asset/3": errors.append("format must be mz.readme-asset/3")
    if data.get("status") not in {"DRAFT", "GENERATION_BLOCKED", "VALIDATION_FAILED", "READY_FOR_REVIEW"}: errors.append("invalid status")
    if not isinstance(data.get("repository"), str) or not data.get("repository", "").strip(): errors.append("repository must be non-empty")
    if data.get("upstreamCore") != {"repository": "oil-oil/beautify-github-readme", "commit": UPSTREAM}: errors.append("upstreamCore must match pinned upstream")
    extension = data.get("extension")
    if extension is not None:
        if not isinstance(extension, dict) or set(extension) != {"id", "namespace", "version", "manifestHash"}: errors.append("extension identity is invalid")
        elif not re.fullmatch(r"[0-9a-f]{64}", str(extension.get("manifestHash", ""))): errors.append("extension manifestHash must be lowercase SHA-256")
    for key in ("brief", "visualBrief", "publishedAsset"): check_file(data.get(key), root, key, errors)
    variants = data.get("variants")
    if variants is not None:
        if not isinstance(variants, list) or not variants: errors.append("variants must be non-empty when present")
        else:
            for index, item in enumerate(variants): check_file(item, root, f"variants[{index}]", errors)
    localization = data.get("localization")
    if localization is not None:
        if not isinstance(localization, dict) or set(localization) != {"primaryLocale", "outputLocales"}: errors.append("localization fields must be primaryLocale and outputLocales")
        else:
            primary, output = localization.get("primaryLocale"), localization.get("outputLocales")
            locale_set = set(output) if isinstance(output, list) and all(isinstance(item, str) and LOCALE.fullmatch(item) for item in output) else set()
            if not isinstance(output, list) or not output or len(locale_set) != len(output): errors.append("localization.outputLocales must contain unique locale tags")
            if not isinstance(primary, str) or not LOCALE.fullmatch(primary) or primary not in locale_set: errors.append("localization.primaryLocale must be included in outputLocales")
            public = [data.get("publishedAsset")] + (variants if isinstance(variants, list) else [])
            pairs: list[tuple[str, str]] = []; viewports = {locale: set() for locale in locale_set}
            for index, item in enumerate(public):
                if not isinstance(item, dict): continue
                locale, viewport = item.get("locale"), item.get("viewport")
                if locale not in locale_set or viewport not in {"desktop", "mobile", "responsive"}: errors.append(f"public asset {index} requires a declared locale and viewport")
                else: pairs.append((locale, viewport)); viewports[locale].add(viewport)
            if len(pairs) != len(set(pairs)): errors.append("localized public assets cannot duplicate locale and viewport")
            if locale_set and any(not values for values in viewports.values()): errors.append("every output locale requires at least one public asset")
            if locale_set and len({frozenset(values) for values in viewports.values()}) > 1: errors.append("every output locale must provide the same viewport set")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources: errors.append("sources must be non-empty")
    else:
        for index, item in enumerate(sources): check_file(item, root, f"sources[{index}]", errors)
    validation = data.get("validation")
    if not isinstance(validation, dict) or not validation: errors.append("validation must be non-empty")
    elif data.get("status") == "READY_FOR_REVIEW":
        failed = [key for key, value in validation.items() if isinstance(value, bool) and not value]
        if failed: errors.append(f"READY_FOR_REVIEW has failed checks: {', '.join(sorted(failed))}")
    if data.get('status') == 'READY_FOR_REVIEW':
        from validate_readme_review import read_ref, read_json, validate as validate_review
        review_path = read_ref(data.get('review'), root, errors, 'review')
        review = read_json(review_path, errors, 'review')
        deliverables = [data.get(key) for key in ('brief', 'visualBrief', 'publishedAsset')]
        deliverables += variants if isinstance(variants, list) else []
        deliverables += sources if isinstance(sources, list) else []
        # Review and asset manifests share a repository root, even when reports live below it.
        if review_path and review_path.parent != root.resolve(): errors.append('review must be at the manifest root')
        locales = localization.get('outputLocales') if isinstance(localization, dict) else None
        if review:
            errors.extend(validate_review(review, root, [item for item in deliverables if isinstance(item, dict)], locales))
            from validate_brief import validate as validate_brief
            brief_data = read_json(read_ref(data.get('brief'), root, errors, 'brief'), errors, 'brief')
            errors.extend(validate_brief(brief_data))
            visual_data = read_json(read_ref(data.get('visualBrief'), root, errors, 'visualBrief'), errors, 'visualBrief')
            if brief_data.get('visualBrief') != visual_data: errors.append('visualBrief differs from the locked brief')
            if brief_data.get('repository') != data.get('repository'): errors.append('brief repository mismatch')
            if brief_data.get('scope') != review.get('scope'): errors.append('brief and review scopes differ')
            mappings = brief_data.get('localization', {}).get('readmeFiles', {})
            reviewed = review.get('readmes', {})
            if mappings and (not isinstance(reviewed, dict) or {k: v.get('path') for k, v in reviewed.items() if isinstance(v, dict)} != mappings):
                errors.append('review README paths differ from the localized brief')
    return errors


def main() -> int:
    if len(sys.argv) != 2: print("usage: validate_asset_manifest.py path", file=sys.stderr); return 2
    path = Path(sys.argv[1]).resolve()
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: print(f"ERROR: {exc}", file=sys.stderr); return 2
    errors = validate(data, path.parent)
    if errors: print("ASSET MANIFEST VALIDATION FAILED\n" + "\n".join(f"- {item}" for item in errors), file=sys.stderr); return 1
    print(f"Asset manifest validation passed: {path}"); return 0


if __name__ == "__main__": raise SystemExit(main())
