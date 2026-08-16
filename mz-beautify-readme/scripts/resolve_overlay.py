#!/usr/bin/env python3
"""Resolve optional Muzi Visual Overlay using explicit intent and owner only."""
from __future__ import annotations
import argparse, json

def resolve(repository: str, explicit: str="auto") -> dict[str,str]:
    if explicit=="enable": return {"id":"muzi","activationReason":"explicit-enable"}
    if explicit=="disable": return {"id":"none","activationReason":"explicit-disable"}
    parts=repository.strip().split("/",1)
    if len(parts)!=2 or not all(parts): return {"id":"none","activationReason":"uncertain-default"}
    if parts[0].casefold()=="muzigeek": return {"id":"muzi","activationReason":"ownership-default"}
    return {"id":"none","activationReason":"third-party-default"}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository",required=True); parser.add_argument("--explicit",choices=("auto","enable","disable"),default="auto")
    args=parser.parse_args(); print(json.dumps(resolve(args.repository,args.explicit),ensure_ascii=False,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
