#!/usr/bin/env python3
"""Plan deterministic README Hero filenames for one or more locales."""
from __future__ import annotations
import argparse, json, re

LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")

def plan(primary: str, locales: list[str], extension: str, mobile: bool) -> dict:
    if not LOCALE.fullmatch(primary): raise ValueError(f"invalid primary locale: {primary}")
    if not locales or any(not LOCALE.fullmatch(item) for item in locales): raise ValueError("all locales must use BCP 47-style tags")
    if len(set(locales)) != len(locales): raise ValueError("locales must be unique")
    if primary not in locales: raise ValueError("primary locale must be included in locales")
    ext=extension.removeprefix(".").lower()
    if ext not in {"svg","png","webp"}: raise ValueError("extension must be svg, png, or webp")
    assets={}
    for locale in locales:
        marker="" if locale==primary else f".{locale}"
        record={"desktop":f"hero{marker}.{ext}"}
        if mobile: record["mobile"]=f"hero{marker}.mobile.{ext}"
        assets[locale]=record
    return {"primaryLocale":primary,"outputLocales":locales,"assets":assets}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-locale",required=True); parser.add_argument("--locales",nargs="+",required=True)
    parser.add_argument("--extension",default="webp"); parser.add_argument("--mobile",action="store_true")
    args=parser.parse_args()
    try: result=plan(args.primary_locale,args.locales,args.extension,args.mobile)
    except ValueError as exc: parser.error(str(exc))
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
