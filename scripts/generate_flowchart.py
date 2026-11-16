"""Render the pipeline flowchart as a PNG image."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    raise

# ── Settings ──────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots" / "pipeline_flowchart.png"

# Colours
BG = "#0a0e27"
WHITE = "#ffffff"
ACCENT = "#00d4ff"
ORANGE = "#ff6d00"
MID_BLUE = "#1a237e"
CARD_BG = "#141a3a"
CARD_BORDER = "#1e2d6a"
ARROW = "#3a5a9c"

# Layout constants
NODE_W, NODE_H = 200, 80
GAP_X, GAP_Y = 60, 40
START_X = 60
TOP_Y = 80


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()  # type: ignore[return-value]


FONT_LG = _font(22)
FONT_SM = _font(16)
FONT_LABEL = _font(14)


def draw_node(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines: list[str],
    fill: str = CARD_BG,
    border: str = CARD_BORDER,
    shape: str = "rect",
) -> None:
    """Draw a rounded-rectangle (or cylinder) node with text."""
    rx, ry = x, y
    ww, hh = NODE_W, NODE_H

    # Background
    draw.rounded_rectangle([rx, ry, rx + ww, ry + hh], radius=12, fill=fill, outline=border)

    # Cylinder top/bottom ellipses for database shape
    if shape == "cylinder":
        draw.ellipse([rx + 10, ry - 8, rx + ww - 10, ry + 20], fill=border, outline="#2a4080")
        draw.ellipse([rx + 10, ry + hh - 20, rx + ww - 10, ry + hh + 8], fill=border, outline="#2a4080")

    # Text lines
    cy = ry + 20
    for i, line in enumerate(lines):
        fs = FONT_LG if i == 0 else FONT_SM
        bbox = draw.textbbox((0, 0), line, font=fs)
        tw = bbox[2] - bbox[0]
        tx = rx + (NODE_W - tw) // 2
        colour = ACCENT if i == 0 else WHITE
        draw.text((tx, cy), line, font=fs, fill=colour)
        cy += fs.getbbox(line)[3] - fs.getbbox(line)[1] + 6


def draw_arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int) -> None:
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=ARROW, width=3)
    # Arrowhead
    angle = 0.4
    import math

    head_len = 14
    rad = math.atan2(y2 - y1, x2 - x1)
    x3 = x2 - head_len * math.cos(rad - angle)
    y3 = y2 - head_len * math.sin(rad - angle)
    x4 = x2 - head_len * math.cos(rad + angle)
    y4 = y2 - head_len * math.sin(rad + angle)
    draw.polygon([(x2, y2), (x3, y3), (x4, y4)], fill=ARROW)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # ── Title ──
    title = "Sentinel Pipeline Flow"
    bbox = draw.textbbox((0, 0), title, font=FONT_LG)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 14), title, font=FONT_LG, fill=ACCENT)

    # ── Main pipeline nodes (left to right) ──
    nodes_main = [
        ("A", ["data/raw", "234 documents"]),
        ("B", ["Clean", "headers, footers,\nunicode, duplicates"]),
        ("C", ["Chunk", "900 chars,\n150 overlap"]),
        ("D", ["Embed", "gemini-embedding-2\n3072 dims"]),
        ("E", ["Qdrant Cloud", "sentinel_corpus\n(cosine)"]),
        ("R", ["Top 5 chunks", "with scores"]),
    ]

    # Position main nodes along top row
    node_x = {}
    for i, (key, lines) in enumerate(nodes_main):
        x = START_X + i * (NODE_W + GAP_X)
        y = TOP_Y
        draw_node(draw, x, y, lines, shape="cylinder" if key == "E" else "rect")
        node_x[key] = (x, y)

    # Arrows between main nodes
    for i in range(len(nodes_main) - 1):
        k1, k2 = nodes_main[i][0], nodes_main[i + 1][0]
        x1, y1 = node_x[k1]
        x2, y2 = node_x[k2]
        draw_arrow(draw, x1 + NODE_W, y1 + NODE_H // 2, x2, y2 + NODE_H // 2)

    # ── Query branch (below the pipeline) ──
    query_y = TOP_Y + NODE_H + GAP_Y + 60

    # Query node (left side, under B)
    q_node = (node_x["B"][0], query_y)
    draw_node(draw, q_node[0], q_node[1], ["Natural-language", "query"], fill="#1a1040")

    # Embed query (centre, under C)
    eq_node = (node_x["C"][0], query_y)
    draw_node(draw, eq_node[0], eq_node[1], ["Embed query"], fill="#1a1040")

    # Arrows: Q -> QE -> E
    draw_arrow(draw, q_node[0] + NODE_W, q_node[1] + NODE_H // 2, eq_node[0], eq_node[1] + NODE_H // 2)

    # QE up to E
    draw_arrow(draw, eq_node[0] + NODE_W // 2, eq_node[1], node_x["E"][0] + NODE_W // 2, node_x["E"][1] + NODE_H)

    # ── Legend ──
    legend_y = HEIGHT - 80
    legend = "Pickle → Chunk → Embed → Store → Search"
    bbox = draw.textbbox((0, 0), legend, font=FONT_LABEL)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, legend_y), legend, font=FONT_LABEL, fill="#5a7ab0")

    # ── Save ──
    img.save(OUTPUT, "PNG")
    print(f"Flowchart saved to {OUTPUT}")


if __name__ == "__main__":
    main()
