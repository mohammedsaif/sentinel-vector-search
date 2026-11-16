"""Generate a video thumbnail image for the Sentinel Vector Search demo."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    raise

# ── Settings ──────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots" / "video_thumbnail.png"

# Colours
BG = "#0a0e27"       # deep navy
ACCENT = "#00d4ff"   # cyan
WHITE = "#ffffff"
MID_BLUE = "#1a237e"
ORANGE = "#ff6d00"


def draw_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: str, outline: str | None = None) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline)


def draw_line(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, fill: str, width: int = 2) -> None:
    draw.line([(x1, y1), (x2, y2)], fill=fill, width=width)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_sub = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # ── Decorative vector-search visualisation (centre) ──
    cx, cy = WIDTH // 2, HEIGHT // 2 - 40

    # Concentric rings (search radius)
    for i, r in enumerate([180, 130, 80, 30]):
        alpha = 40 + i * 30
        color = f"{ACCENT}{alpha:02x}" if len(ACCENT) == 7 else ACCENT
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT, width=2)

    # Centre dot (query)
    draw_circle(draw, cx, cy, 12, ORANGE)

    # Random "document" points around the rings
    import random
    random.seed(42)  # deterministic
    for _ in range(25):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(30, 170)
        px = int(cx + dist * math.cos(angle))
        py = int(cy + dist * math.sin(angle))
        size = random.choice([4, 6, 8])
        draw_circle(draw, px, py, size, ACCENT)
        # Line from point to centre
        draw_line(draw, px, py, cx, cy, f"{ACCENT}30", width=1)

    # ── Title text (top) ──
    title = "Sentinel Vector Search"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    ty = 30

    # Shadow
    draw.text((tx + 2, ty + 2), title, font=font_title, fill="#00000080")
    draw.text((tx, ty), title, font=font_title, fill=WHITE)

    # ── Subtitle (bottom) ──
    subtitle = "Real-time AI-Powered Fraud Detection Pipeline"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox[2] - bbox[0]
    sx = (WIDTH - sw) // 2
    sy = HEIGHT - 100

    draw.text((sx + 1, sy + 1), subtitle, font=font_sub, fill="#00000080")
    draw.text((sx, sy), subtitle, font=font_sub, fill=ACCENT)

    # ── Pipeline badges (bottom-left) ──
    badges = ["CLEAN", "CHUNK", "EMBED", "SEARCH"]
    badge_x = 40
    badge_y = HEIGHT - 60
    for i, badge in enumerate(badges):
        bw = 90
        bh = 30
        bx = badge_x + i * 100
        by = badge_y
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=MID_BLUE, outline=ACCENT)
        tb = draw.textbbox((0, 0), badge, font=font_small)
        text_w = tb[2] - tb[0]
        draw.text((bx + bw // 2 - text_w // 2, by + (bh - (tb[3] - tb[1])) // 2), badge, font=font_small, fill=WHITE)

    # ── Tech badges (bottom-right) ──
    tech = ["Python", "Qdrant", "Gemini Embedding 2"]
    tech_x = WIDTH - 250
    tech_y = HEIGHT - 60
    for i, t in enumerate(tech):
        tx2 = tech_x
        ty2 = tech_y + i * 30
        draw.text((tx2, ty2), t, font=font_small, fill=ACCENT)

    # ── Save ──
    img.save(OUTPUT, "PNG")
    print(f"Thumbnail saved to {OUTPUT}")


if __name__ == "__main__":
    main()
