#!/usr/bin/env python3
"""Generate README hero and social preview PNGs (no runtime deps beyond Pillow)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def _font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def render_console_demo(path: Path) -> None:
    w, h = 1100, 620
    img = Image.new("RGB", (w, h), "#000000")
    draw = ImageDraw.Draw(img)
    mono = _font(13, mono=True)
    mono_sm = _font(11, mono=True)
    sans = _font(14)

    draw.line([(0, 48), (w, 48)], fill="#333333", width=1)
    draw.text((32, 16), "BURNER", fill="#ffffff", font=mono)
    draw.text((w - 200, 18), "DOCS · ABOUT", fill="#888888", font=mono_sm)

    draw.text((32, 72), "DELEGATE TO THE SWARM", fill="#888888", font=mono_sm)
    draw.rectangle([(32, 98), (w - 32, 168)], outline="#555555", width=1)
    draw.text((48, 118), "Check demo product for stock and report status", fill="#cccccc", font=sans)

    draw.text((32, 188), "Agents", fill="#888888", font=mono_sm)
    draw.rectangle([(100, 182), (160, 212)], outline="#555555", width=1)
    draw.text((112, 192), "3", fill="#ffffff", font=mono_sm)
    draw.rectangle([(200, 182), (380, 212)], fill="#ffffff", outline="#ffffff")
    draw.text((248, 192), "DELEGATE", fill="#000000", font=mono_sm)

    y0 = 240
    draw.line([(32, y0), (w - 32, y0)], fill="#333333", width=1)
    col = 300
    draw.line([(col, y0), (col, h - 32)], fill="#333333", width=1)

    draw.text((48, y0 + 16), "SWARM", fill="#888888", font=mono_sm)
    agents = [
        ("agent-01", "destroyed"),
        ("agent-02", "destroyed"),
        ("agent-03", "running"),
    ]
    for i, (aid, state) in enumerate(agents):
        yy = y0 + 48 + i * 36
        draw.text((48, yy), aid, fill="#ffffff", font=mono_sm)
        draw.text((col - 100, yy), state, fill="#888888", font=mono_sm)

    draw.text((col + 16, y0 + 16), "RUN.LOG", fill="#888888", font=mono_sm)
    logs = [
        "14:32:01 task accepted",
        "14:32:02 agent-01 born  seed=a8f2912c…",
        "14:32:03 agent-01 fetch … out of stock",
        "14:32:05 agent-01 identity destroyed",
        "14:32:05 proof 0xfcc74ccff96a3991…",
        "14:32:06 swarm complete — strangers only",
    ]
    for i, line in enumerate(logs):
        color = "#ffffff" if line.startswith("14:32:05 proof") else "#aaaaaa"
        draw.text((col + 16, y0 + 48 + i * 22), line, fill=color, font=mono_sm)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def render_social_preview(path: Path) -> None:
    w, h = 1280, 640
    img = Image.new("RGB", (w, h), "#000000")
    draw = ImageDraw.Draw(img)
    mono = _font(28, mono=True)
    mono_lg = _font(52, mono=True)
    sans = _font(22)

    draw.text((80, 200), "BURNER", fill="#ffffff", font=mono_lg)
    draw.text(
        (80, 290),
        "Delegate to a swarm of disposable agents.",
        fill="#cccccc",
        font=sans,
    )
    draw.text(
        (80, 330),
        "The web sees strangers, not you.",
        fill="#888888",
        font=sans,
    )
    draw.rectangle([(80, 400), (340, 448)], outline="#ffffff", width=1)
    draw.text((110, 412), "github.com/NotPBShaw/burner-agents", fill="#ffffff", font=mono)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


if __name__ == "__main__":
    render_console_demo(ASSETS / "console-demo.png")
    render_social_preview(ASSETS / "social-preview.png")
    print("Wrote", ASSETS / "console-demo.png")
    print("Wrote", ASSETS / "social-preview.png")
