#!/usr/bin/env python3
"""Validate an mz.readme-brief/2 without third-party packages."""
from __future__ import annotations
import json, re, sys
from pathlib import Path, PurePosixPath

UPSTREAM = "55bdb1c05414cd7a0cf911d02e55ece79777206e"
STATUSES = {"DRAFT", "GENERATION_BLOCKED", "VALIDATION_FAILED", "READY_FOR_REVIEW"}
LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")

def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def validate_copy(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object"); return []
    allowed = {"title", "value", "context", "processCue", "proofLabels"}
    unknown = set(value) - allowed
    if unknown: errors.append(f"{label} unknown fields: {', '.join(sorted(unknown))}")
    strings: list[str] = []
    for key in ("title", "value"):
        if not text(value.get(key)): errors.append(f"{label}.{key} must be a non-empty string")
        else: strings.append(value[key])
    for key in ("context", "processCue"):
        if key in value:
            if not text(value[key]): errors.append(f"{label}.{key} must be a non-empty string")
            else: strings.append(value[key])
    labels = value.get("proofLabels")
    if labels is not None:
        if not isinstance(labels, list) or not all(text(item) for item in labels): errors.append(f"{label}.proofLabels must contain non-empty strings")
        else: strings.extend(labels)
    return strings

def validate(data: object) -> list[str]:
    if not isinstance(data, dict): return ["brief root must be an object"]
    errors: list[str] = []
    required = {"format","scope","repository","audience","oneSentenceValue","primaryProof","firstSuccessfulAction","coreDecision","overlay","proofSources","lockedCopy","status"}
    allowed = required | {"heroCopy","localizedHeroCopy","localization"}
    missing, unknown = required-set(data), set(data)-allowed
    if missing: errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if unknown: errors.append(f"unknown fields: {', '.join(sorted(unknown))}")
    if data.get("format") != "mz.readme-brief/2": errors.append("format must be mz.readme-brief/2")
    if data.get("scope") not in {"audit","readme","asset-only"}: errors.append("invalid scope")
    for key in ("repository","audience","oneSentenceValue","primaryProof","firstSuccessfulAction"):
        if not text(data.get(key)): errors.append(f"{key} must be a non-empty string")
    core = data.get("coreDecision")
    core_keys = {"upstreamCommit","compositionMode","implementation","motion","motionAuthorized","themeSpec"}
    if not isinstance(core, dict): errors.append("coreDecision must be an object"); core = {}
    else:
        if set(core) != core_keys: errors.append("coreDecision fields must be exactly upstreamCommit, compositionMode, implementation, motion, motionAuthorized, themeSpec")
    if core.get("upstreamCommit") != UPSTREAM: errors.append("coreDecision.upstreamCommit must match the pinned upstream")
    if core.get("compositionMode") not in {"split","integrated","artifact-wall","background-proof","title-only"}: errors.append("invalid coreDecision.compositionMode")
    if core.get("implementation") not in {"svg","hybrid","raster","none"}: errors.append("invalid coreDecision.implementation")
    if core.get("motion") not in {"none","gif"}: errors.append("invalid coreDecision.motion")
    if not isinstance(core.get("motionAuthorized"), bool): errors.append("coreDecision.motionAuthorized must be boolean")
    if core.get("motion") == "gif" and core.get("motionAuthorized") is not True: errors.append("GIF requires explicit motion authorization")
    theme = core.get("themeSpec")
    theme_keys = {"palette","typography","shape","motif","composition"}
    if not isinstance(theme, dict) or set(theme) != theme_keys or not all(text(theme.get(k)) for k in theme_keys): errors.append("coreDecision.themeSpec requires five non-empty upstream theme fields")
    overlay = data.get("overlay")
    overlay_keys = {"id","activationReason","characterMode","companionMode","displayFont"}
    if not isinstance(overlay, dict): errors.append("overlay must be an object"); overlay = {}
    elif set(overlay) != overlay_keys: errors.append("overlay fields are invalid")
    if overlay.get("id") not in {"none","muzi"}: errors.append("invalid overlay.id")
    if overlay.get("activationReason") not in {"explicit-enable","explicit-disable","ownership-default","third-party-default","uncertain-default"}: errors.append("invalid overlay.activationReason")
    if overlay.get("characterMode") not in {"none","muzi"}: errors.append("invalid overlay.characterMode")
    if overlay.get("companionMode") not in {"include","exclude"}: errors.append("invalid overlay.companionMode")
    if overlay.get("displayFont") not in {"project-native","pfanhututi","fallback"}: errors.append("invalid overlay.displayFont")
    if overlay.get("id") == "none" and (overlay.get("characterMode"),overlay.get("companionMode"),overlay.get("displayFont")) != ("none","exclude","project-native"): errors.append("overlay none must use no character, no companion, and project-native font")
    if overlay.get("companionMode") == "include" and not (overlay.get("id") == "muzi" and overlay.get("characterMode") == "muzi"): errors.append("cat requires Muzi overlay and Muzi character")
    if overlay.get("displayFont") == "pfanhututi" and overlay.get("id") != "muzi": errors.append("PFanHuTuTi requires Muzi overlay")
    localization=data.get("localization")
    locale_set: set[str] = set()
    primary_locale: str | None = None
    if localization is not None:
        expected={"primaryLocale","outputLocales","assetStrategy","readmeFiles"}
        if not isinstance(localization,dict) or set(localization)!=expected: errors.append("localization fields must be exactly primaryLocale, outputLocales, assetStrategy, readmeFiles")
        else:
            primary_locale=localization.get("primaryLocale")
            output=localization.get("outputLocales")
            if not isinstance(primary_locale,str) or not LOCALE.fullmatch(primary_locale): errors.append("localization.primaryLocale must be a BCP 47-style tag")
            if not isinstance(output,list) or not output or not all(isinstance(item,str) and LOCALE.fullmatch(item) for item in output): errors.append("localization.outputLocales must contain BCP 47-style tags")
            elif len(set(output))!=len(output): errors.append("localization.outputLocales must be unique")
            else: locale_set=set(output)
            if primary_locale not in locale_set: errors.append("localization.primaryLocale must be included in outputLocales")
            if localization.get("assetStrategy")!="localized-assets": errors.append("localization.assetStrategy must be localized-assets")
            readmes=localization.get("readmeFiles")
            if not isinstance(readmes,dict) or set(readmes)!=locale_set: errors.append("localization.readmeFiles keys must exactly match outputLocales")
            else:
                for locale,path_value in readmes.items():
                    if not text(path_value): errors.append(f"localization.readmeFiles.{locale} must be non-empty"); continue
                    pure=PurePosixPath(path_value.replace("\\","/"))
                    if pure.is_absolute() or ".." in pure.parts: errors.append(f"localization.readmeFiles.{locale} must be repository-relative")
    proof = data.get("proofSources")
    if not isinstance(proof, list) or not all(text(x) for x in proof): errors.append("proofSources must contain non-empty strings")
    locked = data.get("lockedCopy")
    if not isinstance(locked, list) or not all(text(x) for x in locked): errors.append("lockedCopy must contain non-empty strings")
    visible: list[str] = []
    if core.get("implementation") != "none":
        if "heroCopy" not in data: errors.append("heroCopy is required when implementation is not none")
        else: visible += validate_copy(data.get("heroCopy"), "heroCopy", errors)
    localized = data.get("localizedHeroCopy")
    if localized is not None and localization is None: errors.append("localizedHeroCopy requires localization metadata")
    if localized is not None:
        if not isinstance(localized, dict) or not localized: errors.append("localizedHeroCopy must be a non-empty object")
        else:
            for locale, copy in localized.items(): visible += validate_copy(copy, f"localizedHeroCopy.{locale}", errors)
    if localization is not None and locale_set and primary_locale in locale_set:
        expected_secondary=locale_set-{primary_locale}
        actual_secondary=set(localized) if isinstance(localized,dict) else set()
        if actual_secondary != expected_secondary: errors.append("localizedHeroCopy keys must exactly match non-primary outputLocales")
    if data.get("scope") == "audit" and core.get("implementation") != "none": errors.append("audit scope requires implementation none")
    if data.get("status") not in STATUSES: errors.append("invalid status")
    if data.get("status") == "READY_FOR_REVIEW":
        if not proof: errors.append("READY_FOR_REVIEW requires proof sources")
        lockset = set(locked) if isinstance(locked, list) else set()
        if any(item not in lockset for item in visible): errors.append("READY_FOR_REVIEW requires every visible hero string in lockedCopy")
    return errors

def main() -> int:
    if len(sys.argv)!=2: print("usage: validate_brief.py path", file=sys.stderr); return 2
    try: data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors=validate(data)
    if errors: print("BRIEF VALIDATION FAILED\n"+"\n".join(f"- {e}" for e in errors),file=sys.stderr); return 1
    print(f"Brief validation passed: {Path(sys.argv[1]).resolve()}"); return 0
if __name__ == "__main__": raise SystemExit(main())
