#!/usr/bin/env python3
"""Validate an mz.readme-brief/3 without third-party packages."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path, PurePosixPath

UPSTREAM = "55bdb1c05414cd7a0cf911d02e55ece79777206e"
LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_visual_brief(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["visualBrief must be an object"]
    errors: list[str] = []
    if value.get("format") != "mz.visual-brief/1": errors.append("visualBrief.format must be mz.visual-brief/1")
    if value.get("engineVersion") != "2.0.0": errors.append("visualBrief.engineVersion must be 2.0.0")
    if value.get("status") != "RESOLVED": errors.append("visualBrief must be RESOLVED")
    if value.get("target") != {"skill": "mz-beautify-readme", "mode": "readme"}: errors.append("visualBrief target must be mz-beautify-readme/readme")
    asset = value.get("asset")
    if not isinstance(asset, dict) or asset.get("profile") != "readme-visual": errors.append("visualBrief asset profile must be readme-visual")
    compat = value.get("engineCompat")
    if not isinstance(compat, dict) or compat.get("format") != "mz.engine-compat/1": errors.append("visualBrief Engine compatibility is invalid")
    elif not all(isinstance(compat.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", compat[key]) for key in ("snapshotHash", "sourceCatalogHash")):
        errors.append("visualBrief Engine hashes must be lowercase SHA-256")
    return errors


def copy_strings(copy: object) -> list[str]:
    if not isinstance(copy, dict): return []
    values = [copy.get("title"), copy.get("value"), copy.get("context"), copy.get("processCue")]
    values.extend(copy.get("proofLabels", []) if isinstance(copy.get("proofLabels"), list) else [])
    return [item for item in values if text(item)]


def validate(data: object) -> list[str]:
    if not isinstance(data, dict): return ["brief root must be an object"]
    errors: list[str] = []
    required = {"format", "scope", "repository", "audience", "oneSentenceValue", "primaryProof", "firstSuccessfulAction", "coreDecision", "visualBrief", "proofSources", "lockedCopy", "status"}
    allowed = required | {"localization", "heroCopy", "localizedHeroCopy"}
    if required - set(data): errors.append(f"missing fields: {', '.join(sorted(required-set(data)))}")
    if set(data) - allowed: errors.append(f"unknown fields: {', '.join(sorted(set(data)-allowed))}")
    if data.get("format") != "mz.readme-brief/3": errors.append("format must be mz.readme-brief/3")
    if data.get("scope") not in {"audit", "readme", "asset-only"}: errors.append("invalid scope")
    for key in ("repository", "audience", "oneSentenceValue", "primaryProof", "firstSuccessfulAction"):
        if not text(data.get(key)): errors.append(f"{key} must be non-empty")
    core = data.get("coreDecision")
    if not isinstance(core, dict): errors.append("coreDecision must be an object")
    else:
        expected = {"upstreamCommit", "compositionMode", "implementation", "motion", "motionAuthorized", "themeSpec"}
        if set(core) != expected: errors.append("coreDecision fields are invalid")
        if core.get("upstreamCommit") != UPSTREAM: errors.append("coreDecision upstreamCommit is not pinned")
        if core.get("compositionMode") not in {"split", "integrated", "artifact-wall", "background-proof", "title-only"}: errors.append("invalid compositionMode")
        if core.get("implementation") not in {"svg", "hybrid", "raster", "none"}: errors.append("invalid implementation")
        if core.get("motion") not in {"none", "gif"} or not isinstance(core.get("motionAuthorized"), bool): errors.append("invalid motion decision")
        if core.get("motion") == "gif" and core.get("motionAuthorized") is not True: errors.append("GIF requires explicit motion authorization")
        theme = core.get("themeSpec")
        if not isinstance(theme, dict) or set(theme) != {"palette", "typography", "shape", "motif", "composition"} or not all(text(item) for item in theme.values()): errors.append("themeSpec must contain five non-empty fields")
    errors.extend(validate_visual_brief(data.get("visualBrief")))
    sources = data.get("proofSources")
    if not isinstance(sources, list) or not sources or not all(text(item) for item in sources): errors.append("proofSources must be a non-empty string list")
    locked = data.get("lockedCopy")
    if not isinstance(locked, list) or not all(text(item) for item in locked): errors.append("lockedCopy must be a string list")
    hero = data.get("heroCopy")
    if hero is not None and (not isinstance(hero, dict) or not {"title", "value"} <= set(hero) or not all(text(item) for item in copy_strings(hero))): errors.append("heroCopy is invalid")
    localization = data.get("localization")
    localized = data.get("localizedHeroCopy")
    if localized is not None and localization is None: errors.append("localizedHeroCopy requires localization metadata")
    if localization is not None:
        expected = {"primaryLocale", "outputLocales", "assetStrategy", "readmeFiles"}
        if not isinstance(localization, dict) or set(localization) != expected: errors.append("localization fields must be exactly primaryLocale, outputLocales, assetStrategy, readmeFiles")
        else:
            primary, output, readmes = localization.get("primaryLocale"), localization.get("outputLocales"), localization.get("readmeFiles")
            locale_set = set(output) if isinstance(output, list) and all(isinstance(item, str) and LOCALE.fullmatch(item) for item in output) else set()
            if not isinstance(primary, str) or not LOCALE.fullmatch(primary) or primary not in locale_set: errors.append("localization primaryLocale must be included in valid outputLocales")
            if not isinstance(output, list) or not output or len(locale_set) != len(output): errors.append("outputLocales must be unique valid locale tags")
            if localization.get("assetStrategy") != "localized-assets": errors.append("assetStrategy must be localized-assets")
            if not isinstance(readmes, dict) or set(readmes) != locale_set: errors.append("readmeFiles keys must exactly match outputLocales")
            elif any(not text(path) or PurePosixPath(path.replace('\\', '/')).is_absolute() or '..' in PurePosixPath(path.replace('\\', '/')).parts for path in readmes.values()): errors.append("readmeFiles must be safe repository-relative paths")
            expected_secondary = locale_set - {primary}
            if not isinstance(localized, dict) or set(localized) != expected_secondary: errors.append("localizedHeroCopy keys must exactly match non-primary outputLocales")
    visible = copy_strings(hero)
    if isinstance(localized, dict):
        for item in localized.values(): visible.extend(copy_strings(item))
    if visible and isinstance(locked, list) and any(item not in locked for item in visible): errors.append("every visible copy string must appear in lockedCopy")
    if data.get("status") not in {"DRAFT", "GENERATION_BLOCKED", "VALIDATION_FAILED", "READY_FOR_REVIEW"}: errors.append("invalid status")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_brief.py path/to/readme-brief.json", file=sys.stderr)
        return 2
    try: data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    errors = validate(data)
    if errors:
        print("README BRIEF VALIDATION FAILED\n" + "\n".join(f"- {item}" for item in errors), file=sys.stderr); return 1
    print("README brief validation passed"); return 0


if __name__ == "__main__": raise SystemExit(main())
