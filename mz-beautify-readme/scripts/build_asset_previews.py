#!/usr/bin/env python3
"""Render raster README assets at GitHub desktop and mobile widths."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageColor


SURROUNDS = {"light": "#ffffff", "dark": "#0d1117"}
WIDTHS = (900, 360)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_asset_previews.py hero.(png|webp) output-dir", file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).expanduser().resolve()
    output = Path(sys.argv[2]).expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: asset not found: {source}", file=sys.stderr)
        return 2
    if source.suffix.lower() == ".svg":
        print("ERROR: SVG preview requires a browser or CairoSVG; render it to PNG first", file=sys.stderr)
        return 2
    output.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = image.convert("RGBA")
        for width in WIDTHS:
            height = round(image.height * width / image.width)
            rendered = image.resize((width, height), Image.Resampling.LANCZOS)
            margin = 32 if width >= 900 else 16
            for mode, color in SURROUNDS.items():
                canvas = Image.new("RGBA", (width + 2 * margin, height + 2 * margin), ImageColor.getrgb(color) + (255,))
                canvas.alpha_composite(rendered, (margin, margin))
                target = output / f"{source.stem}-{width}-{mode}.png"
                canvas.convert("RGB").save(target, optimize=True)
                print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
