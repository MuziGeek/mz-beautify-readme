#!/usr/bin/env python3
"""Build the split upstream decision + Muzi Overlay README hero."""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


SOURCE = Path(__file__).resolve().parent
README_ROOT = SOURCE.parent
ASSETS = README_ROOT / "assets"
REPO_ROOT = SOURCE.parents[2]
IDENTITY = REPO_ROOT / "mz-beautify-readme" / "assets" / "identity"
BRIEF = SOURCE / "hero-brief.json"
FONT_PROVENANCE = SOURCE / "font-provenance.json"
IDENTITY_PROVENANCE = SOURCE / "identity-provenance.json"

PAPER = (252, 241, 224)
INK = "#17243a"
BLACK = "#171717"
MUTED = "#6d6a62"
MUSTARD = "#e7ad1a"
RUST = "#b95336"
DIVIDER = "#c8bfb0"


def system_font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    root = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def display_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    override = os.environ.get("MZ_DISPLAY_FONT")
    if override:
        path = Path(override).resolve()
        expected = json.loads(FONT_PROVENANCE.read_text(encoding="utf-8"))["sha256"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("MZ_DISPLAY_FONT hash mismatch")
        return ImageFont.truetype(path, size)
    return system_font(["FZSTK.TTF", "segoeprb.ttf", "STKAITI.TTF"], size)


def fit_display(draw: ImageDraw.ImageDraw, text: str, width: int, start: int, minimum: int) -> ImageFont.ImageFont:
    for size in range(start, minimum - 1, -1):
        font = display_font(size)
        if draw.textbbox((0, 0), text, font=font)[2] <= width:
            return font
    return display_font(minimum)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split(" ")
    if len(words) == 1:
        return [text]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def corner_background(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    patch = max(12, min(28, width // 10, height // 10))
    pixels = []
    for box in (
        (0, 0, patch, patch),
        (width - patch, 0, width, patch),
        (0, height - patch, patch, height),
        (width - patch, height - patch, width, height),
    ):
        pixels.extend(rgb.crop(box).getdata())
    return tuple(int(statistics.median(channel)) for channel in zip(*pixels))


def foreground(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, corner_background(rgb))
    red, green, blue = ImageChops.difference(rgb, background).split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    alpha = maximum.point(lambda value: 0 if value <= 7 else 255 if value >= 30 else int((value - 7) * 255 / 23))
    layer = rgb.convert("RGBA")
    layer.putalpha(alpha)
    return layer


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def verify_identity_inputs() -> None:
    provenance = json.loads(IDENTITY_PROVENANCE.read_text(encoding="utf-8"))
    for item in provenance["inputs"]:
        path = REPO_ROOT / Path(item["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"identity hash mismatch: {item['path']}")


def build_subject() -> Image.Image:
    verify_identity_inputs()
    subject = Image.new("RGBA", (570, 350), (0, 0, 0, 0))
    muzi = contain(foreground(Image.open(IDENTITY / "muzi-crayon-fullbody-style.png")), (365, 365))
    cat = contain(foreground(Image.open(IDENTITY / "muzi-crayon-cat-master.png")), (165, 165))
    subject.alpha_composite(muzi, (6, -6))
    subject.alpha_composite(cat, (392, 166))
    target = ASSETS / "source" / "hero-illustration.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    subject.save(target, optimize=True)
    return subject


def rail_line(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]]) -> None:
    draw.line(points, fill=INK, width=3, joint="curve")


def rail_markers(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], labels: list[str], mobile: bool) -> None:
    colors = (RUST, MUSTARD, "#d9e6f0")
    font = system_font(["Dengb.ttf", "segoeuib.ttf"], 13 if mobile else 12)
    for (x, y), color, label in zip(points, colors, labels):
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color, outline=INK, width=2)
        box = draw.textbbox((0, 0), label, font=font)
        draw.text((x - (box[2] - box[0]) / 2, y + 10), label, font=font, fill=MUTED)


def text_block(draw: ImageDraw.ImageDraw, copy: dict, mobile: bool) -> None:
    left = 36 if mobile else 48
    top = 28 if mobile else 34
    width = 648 if mobile else 420
    context = system_font(["Dengb.ttf", "segoeuib.ttf"], 17 if mobile else 14)
    value = system_font(["Deng.ttf", "msyh.ttc", "segoeui.ttf"], 26 if mobile else 20)
    cue = system_font(["Dengb.ttf", "segoeuib.ttf"], 16 if mobile else 14)
    draw.text((left, top), copy["context"], font=context, fill=MUTED)
    title = fit_display(draw, copy["title"], width, 62 if mobile else 55, 38)
    title_y = top + (40 if mobile else 30)
    draw.text((left, title_y), copy["title"], font=title, fill=BLACK)
    bar_y = top + (112 if mobile else 98)
    draw.rounded_rectangle((left, bar_y, left + (330 if mobile else 285), bar_y + 10), 5, fill=MUSTARD)
    if mobile:
        lines = wrap_text(draw, copy["value"], value, width)
        for index, line in enumerate(lines):
            draw.text((left, bar_y + 22 + index * 30), line, font=value, fill=INK)
        draw.text((left, bar_y + 22 + len(lines) * 30 + 6), copy["processCue"], font=cue, fill=MUTED)
    else:
        draw.text((left, bar_y + 22), copy["value"], font=value, fill=INK)
        draw.text((left, bar_y + 62), copy["processCue"], font=cue, fill=MUTED)


def build(copy: dict, subject: Image.Image, output: Path, mobile: bool) -> None:
    size = (720, 600) if mobile else (1200, 360)
    canvas = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(canvas)
    if mobile:
        draw.line((24, 266, 696, 266), fill=DIVIDER, width=2)
        points = [(150, 570), (360, 562), (570, 570)]
        rail_line(draw, points)
        scene = contain(subject, (500, 307))
        canvas.paste(scene, (110, 278), scene)
        rail_markers(draw, points, copy["proofLabels"], True)
    else:
        draw.line((500, 28, 500, 332), fill=DIVIDER, width=2)
        points = [(566, 312), (850, 304), (1148, 312)]
        rail_line(draw, points)
        scene = contain(subject, (570, 340))
        canvas.paste(scene, (560, 5), scene)
        rail_markers(draw, points, copy["proofLabels"], False)
    text_block(draw, copy, mobile)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "WEBP", quality=92, method=6)


def main() -> None:
    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    assert brief["coreDecision"]["compositionMode"] == "split"
    assert brief["coreDecision"]["implementation"] == "hybrid"
    subject = build_subject()
    copies = {"en": brief["heroCopy"], **brief.get("localizedHeroCopy", {})}
    for locale, copy in copies.items():
        suffix = "" if locale == "en" else f".{locale}"
        build(copy, subject, ASSETS / f"hero{suffix}.webp", False)
        build(copy, subject, ASSETS / f"hero{suffix}.mobile.webp", True)


if __name__ == "__main__":
    main()
