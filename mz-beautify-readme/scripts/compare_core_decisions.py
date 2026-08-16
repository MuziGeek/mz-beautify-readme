#!/usr/bin/env python3
"""Assert that two v2 briefs differ only in Overlay fields and review status."""
from __future__ import annotations
import json, sys
from pathlib import Path

def normalized(data: dict) -> dict:
    return {k:v for k,v in data.items() if k not in {"overlay","status"}}
def compare(left: dict,right: dict)->list[str]:
    return [] if normalized(left)==normalized(right) else ["briefs differ outside overlay/status"]
def main()->int:
    if len(sys.argv)!=3: print("usage: compare_core_decisions.py none.json muzi.json",file=sys.stderr); return 2
    try: left=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); right=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors=compare(left,right)
    if errors: print("CORE INVARIANCE FAILED\n- "+errors[0],file=sys.stderr); return 1
    print("Core invariance passed"); return 0
if __name__=="__main__": raise SystemExit(main())
