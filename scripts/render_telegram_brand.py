#!/usr/bin/env python3
"""Render petfeature header brand (lamp + wordmark) as PNG assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "app" / "static" / "img"
FONT_PATH = ROOT / "app" / "static" / "fonts" / "Vazirmatn-Bold.ttf"

BG = "#171210"
ACCENT = "#a6c3a0"
METAL = "#5a4936"
TEXT = "#ece5dc"
WORDMARK = "پت فیچر"


def draw_lamp(draw: ImageDraw.ImageDraw, cx: int, top: int, scale: float) -> int:
    """Draw the CSS header lamp; return total height."""
    shade_w = max(4, round(20 * scale))
    shade_h = max(3, round(10 * scale))
    pole_w = max(2, round(2 * scale))
    pole_h = max(2, round(9 * scale))
    base_w = max(4, round(13 * scale))
    base_h = max(2, round(3 * scale))

    left = cx - shade_w // 2
    inset = int(shade_w * 0.2)
    draw.polygon(
        [
            (left + inset, top),
            (left + shade_w - inset, top),
            (left + shade_w, top + shade_h),
            (left, top + shade_h),
        ],
        fill=ACCENT,
    )

    pole_top = top + shade_h
    draw.rectangle(
        [
            cx - pole_w // 2,
            pole_top,
            cx + pole_w // 2,
            pole_top + pole_h,
        ],
        fill=METAL,
    )

    base_top = pole_top + pole_h
    draw.rounded_rectangle(
        [
            cx - base_w // 2,
            base_top,
            cx + base_w // 2,
            base_top + base_h,
        ],
        radius=max(1, int(scale)),
        fill=METAL,
    )

    return base_top + base_h - top


def add_glow(img: Image.Image, cx: int, cy: int, radius: int) -> Image.Image:
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for i in range(radius, 0, -4):
        alpha = int(28 * (1 - i / radius))
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            fill=(166, 195, 160, alpha),
        )
    return Image.alpha_composite(img.convert("RGBA"), glow)


def render_square(size: int, out_path: Path) -> None:
    img = Image.new("RGBA", (size, size), BG)

    # Header lamp is ~22px tall; scale to ~30% of canvas height.
    lamp_total = int(size * 0.30)
    scale = lamp_total / 22
    lamp_top = int(size * 0.22)

    img = add_glow(img, size // 2, lamp_top + int(10 * scale), int(size * 0.18))

    draw = ImageDraw.Draw(img)
    lamp_h = draw_lamp(draw, size // 2, lamp_top, scale=scale)

    font_size = int(size * 0.105)
    font = ImageFont.truetype(str(FONT_PATH), font_size)
    bbox = draw.textbbox((0, 0), WORDMARK, font=font, anchor="lt")
    text_w = bbox[2] - bbox[0]
    text_x = (size - text_w) // 2 - bbox[0]
    text_y = lamp_top + lamp_h + int(size * 0.07)
    draw.text((text_x, text_y), WORDMARK, font=font, fill=TEXT, anchor="lt")

    img.convert("RGB").save(out_path, "PNG", optimize=True)


def render_horizontal(width: int, height: int, out_path: Path) -> None:
    """Header-style horizontal lockup."""
    img = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(img)

    scale = 2.2
    lamp_top = (height - int(22 * scale)) // 2
    lamp_h = draw_lamp(draw, int(width * 0.22), lamp_top, scale=scale)

    font_size = 34
    font = ImageFont.truetype(str(FONT_PATH), font_size)
    bbox = draw.textbbox((0, 0), WORDMARK, font=font)
    text_x = int(width * 0.22) + int(13 * scale) + 18
    text_y = lamp_top + (lamp_h - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((text_x, text_y), WORDMARK, font=font, fill=TEXT)

    img.convert("RGB").save(out_path, "PNG", optimize=True)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_square(512, OUT_DIR / "brand-telegram-512.png")
    render_square(1024, OUT_DIR / "brand-telegram-1024.png")
    render_horizontal(640, 200, OUT_DIR / "brand-lockup.png")
    print("Wrote:")
    for name in ("brand-telegram-512.png", "brand-telegram-1024.png", "brand-lockup.png"):
        path = OUT_DIR / name
        print(f"  {path} ({path.stat().st_size // 1024} KB)")
