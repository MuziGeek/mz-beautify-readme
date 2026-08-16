#!/usr/bin/env python3
"""Audit dominant empty edge bands in a raster README Hero."""
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path
from PIL import Image

def measure(path: Path, threshold: int=28, min_row_density: float=.003) -> dict:
    image=Image.open(path).convert("RGB"); width,height=image.size; patch=max(4,min(20,width//10,height//10))
    boxes=((0,0,patch,patch),(width-patch,0,width,patch),(0,height-patch,patch,height),(width-patch,height-patch,width,height))
    samples=[pixel for box in boxes for pixel in image.crop(box).getdata()]
    background=tuple(int(statistics.median(channel)) for channel in zip(*samples))
    minimum=max(4,math.ceil(width*min_row_density)); active=[]
    pixels=image.load()
    for y in range(height):
        count=0
        for x in range(width):
            pixel=pixels[x,y]
            if max(abs(pixel[i]-background[i]) for i in range(3)) >= threshold:
                count+=1
                if count>=minimum: active.append(y); break
    if not active: raise ValueError("no meaningful content rows detected")
    top,bottom=min(active),max(active)
    active_set=set(active); longest=(0,0); start=None
    for y in range(top,bottom+2):
        if y<=bottom and y not in active_set:
            if start is None: start=y
        elif start is not None:
            if y-start>longest[1]-longest[0]: longest=(start,y)
            start=None
    return {"path":str(path),"width":width,"height":height,"background":background,"contentRows":[top,bottom],"largestInternalEmptyBandRows":list(longest),"largestInternalEmptyBandRatio":round((longest[1]-longest[0])/height,4),"topWhitespaceRatio":round(top/height,4),"bottomWhitespaceRatio":round((height-1-bottom)/height,4),"verticalContentOccupancy":round((bottom-top+1)/height,4)}

def validate(result: dict, max_edge_ratio: float=.18, max_imbalance: float=2.5, max_internal_ratio: float=.18) -> list[str]:
    top=result["topWhitespaceRatio"]; bottom=result["bottomWhitespaceRatio"]; errors=[]
    if bottom>max_edge_ratio and bottom>max(top,.02)*max_imbalance: errors.append("dominant empty bottom band")
    if top>max_edge_ratio and top>max(bottom,.02)*max_imbalance: errors.append("dominant empty top band")
    if result["largestInternalEmptyBandRatio"]>max_internal_ratio: errors.append("dominant empty internal band")
    return errors

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("image",type=Path)
    parser.add_argument("--threshold",type=int,default=28); parser.add_argument("--min-row-density",type=float,default=.003)
    parser.add_argument("--max-edge-ratio",type=float,default=.18); parser.add_argument("--max-imbalance",type=float,default=2.5)
    parser.add_argument("--max-internal-ratio",type=float,default=.18)
    args=parser.parse_args()
    try: result=measure(args.image.resolve(),args.threshold,args.min_row_density)
    except (OSError,ValueError) as exc: parser.error(str(exc))
    errors=validate(result,args.max_edge_ratio,args.max_imbalance,args.max_internal_ratio); result["status"]="FAIL" if errors else "PASS"; result["errors"]=errors
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
