#!/usr/bin/env python3
"""Validate an mz.readme-asset/2 manifest and all declared hashes."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path, PurePosixPath

UPSTREAM="55bdb1c05414cd7a0cf911d02e55ece79777206e"
LOCALE=re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
def check_file(item: object, root: Path, label: str, errors: list[str]) -> None:
    if not isinstance(item,dict): errors.append(f"{label} must be an object"); return
    if not {"path","sha256"} <= set(item): errors.append(f"{label} requires path and sha256"); return
    if set(item)-{"path","sha256","role","license","locale","viewport"}: errors.append(f"{label} has unknown fields")
    if "locale" in item and (not isinstance(item["locale"],str) or not LOCALE.fullmatch(item["locale"])): errors.append(f"{label}.locale must be a BCP 47-style tag")
    if "viewport" in item and item["viewport"] not in {"desktop","mobile","responsive"}: errors.append(f"{label}.viewport is invalid")
    rel,digest=item.get("path"),item.get("sha256")
    if not isinstance(rel,str) or not rel: errors.append(f"{label}.path must be non-empty"); return
    pure=PurePosixPath(rel.replace("\\","/"))
    if pure.is_absolute() or ".." in pure.parts: errors.append(f"{label}.path must be repository-relative"); return
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest): errors.append(f"{label}.sha256 must be lowercase SHA-256"); return
    path=(root/Path(*pure.parts)).resolve()
    try: path.relative_to(root.resolve())
    except ValueError: errors.append(f"{label}.path escapes manifest root"); return
    if not path.is_file(): errors.append(f"{label} missing: {rel}"); return
    if hashlib.sha256(path.read_bytes()).hexdigest()!=digest: errors.append(f"{label} hash mismatch: {rel}")

def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data,dict): return ["manifest root must be an object"]
    errors=[]
    required={"format","status","repository","upstreamCore","overlayId","brief","publishedAsset","sources","validation"}
    allowed=required|{"variants","localization"}
    if required-set(data): errors.append(f"missing fields: {', '.join(sorted(required-set(data)))}")
    if set(data)-allowed: errors.append(f"unknown fields: {', '.join(sorted(set(data)-allowed))}")
    if data.get("format")!="mz.readme-asset/2": errors.append("format must be mz.readme-asset/2")
    if data.get("status") not in {"DRAFT","GENERATION_BLOCKED","VALIDATION_FAILED","READY_FOR_REVIEW"}: errors.append("invalid status")
    if not isinstance(data.get("repository"),str) or not data.get("repository","").strip(): errors.append("repository must be non-empty")
    core=data.get("upstreamCore")
    if core!={"repository":"oil-oil/beautify-github-readme","commit":UPSTREAM}: errors.append("upstreamCore must match pinned upstream")
    if data.get("overlayId") not in {"none","muzi"}: errors.append("invalid overlayId")
    check_file(data.get("brief"),root,"brief",errors); check_file(data.get("publishedAsset"),root,"publishedAsset",errors)
    variants=data.get("variants")
    if variants is not None:
        if not isinstance(variants,list) or not variants: errors.append("variants must be non-empty when present")
        else:
            for i,item in enumerate(variants): check_file(item,root,f"variants[{i}]",errors)
    localization=data.get("localization")
    if localization is not None:
        if not isinstance(localization,dict) or set(localization)!={"primaryLocale","outputLocales"}: errors.append("localization fields must be primaryLocale and outputLocales")
        else:
            primary=localization.get("primaryLocale"); output=localization.get("outputLocales")
            locale_set=set(output) if isinstance(output,list) and all(isinstance(item,str) and LOCALE.fullmatch(item) for item in output) else set()
            if not isinstance(output,list) or not output or len(locale_set)!=len(output): errors.append("localization.outputLocales must contain unique BCP 47-style tags")
            if not isinstance(primary,str) or not LOCALE.fullmatch(primary) or primary not in locale_set: errors.append("localization.primaryLocale must be included in outputLocales")
            public=[data.get("publishedAsset")]+(variants if isinstance(variants,list) else [])
            if isinstance(data.get("publishedAsset"),dict) and data["publishedAsset"].get("locale")!=primary: errors.append("publishedAsset.locale must match primaryLocale")
            pairs=[]; viewports={locale:set() for locale in locale_set}
            for index,item in enumerate(public):
                if not isinstance(item,dict): continue
                locale,viewport=item.get("locale"),item.get("viewport")
                if locale not in locale_set or viewport not in {"desktop","mobile","responsive"}: errors.append(f"public asset {index} requires a declared locale and viewport")
                else: pairs.append((locale,viewport)); viewports[locale].add(viewport)
            if len(pairs)!=len(set(pairs)): errors.append("localized public assets cannot duplicate locale and viewport")
            if locale_set and any(not values for values in viewports.values()): errors.append("every output locale requires at least one public asset")
            if locale_set and len({frozenset(values) for values in viewports.values()})>1: errors.append("every output locale must provide the same viewport set")
    sources=data.get("sources")
    if not isinstance(sources,list) or not sources: errors.append("sources must be non-empty")
    else:
        for i,item in enumerate(sources): check_file(item,root,f"sources[{i}]",errors)
    validation=data.get("validation")
    if not isinstance(validation,dict) or not validation: errors.append("validation must be non-empty")
    elif data.get("status")=="READY_FOR_REVIEW":
        failed=[k for k,v in validation.items() if isinstance(v,bool) and not v]
        if failed: errors.append(f"READY_FOR_REVIEW has failed checks: {', '.join(sorted(failed))}")
    return errors

def main()->int:
    if len(sys.argv)!=2: print("usage: validate_asset_manifest.py path",file=sys.stderr); return 2
    path=Path(sys.argv[1]).resolve()
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors=validate(data,path.parent)
    if errors: print("ASSET MANIFEST VALIDATION FAILED\n"+"\n".join(f"- {e}" for e in errors),file=sys.stderr); return 1
    print(f"Asset manifest validation passed: {path}"); return 0
if __name__=="__main__": raise SystemExit(main())
