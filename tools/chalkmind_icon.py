"""Chalkmind brand mark: a chalk square-root sign (also reads as a tick) on a
chalkboard-green tile, with a highlighter-yellow AI sparkle in the root.

All geometry is in a 1024 x 1024 design space and drawn 4x supersampled for
clean anti-aliasing at every size.
"""
import math
from PIL import Image, ImageDraw

# Brand colours
BOARD_TOP = (16, 94, 80)      # #105E50 chalkboard green (light corner)
BOARD_BOTTOM = (8, 52, 46)    # #08342E chalkboard green (dark corner)
CHALK = (248, 250, 252)       # #F8FAFC chalk white
SPARK = (250, 204, 21)        # #FACC15 highlighter yellow

SS = 4  # supersampling factor

# Radical / tick path (design space). The middle section is a tick.
GLYPH = [(232, 548), (330, 500), (438, 762), (628, 262), (806, 262)]
STROKE = 88
SPARK_CENTER = (722, 500)
SPARK_R = 104


def _gradient(size):
    """Diagonal chalkboard gradient."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = tuple(int(BOARD_TOP[i] + (BOARD_BOTTOM[i] - BOARD_TOP[i]) * t) for i in range(3))
    return img


def _sparkle_points(cx, cy, r, waist=0.16, steps=40):
    """Classic four-point AI sparkle: tips joined by concave curves."""
    tips = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pts = []
    for i in range(4):
        a, b = tips[i], tips[(i + 1) % 4]
        # control point pulled toward the centre makes the sides concave
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ctrl = (cx + (mx - cx) * waist * 2, cy + (my - cy) * waist * 2)
        for k in range(steps):
            t = k / steps
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * ctrl[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * ctrl[1] + t * t * b[1]
            pts.append((x, y))
    return pts


def draw_glyph(draw, scale, offset=(0, 0), chalk=CHALK, spark=SPARK, stroke=STROKE):
    ox, oy = offset
    pts = [(ox + x * scale, oy + y * scale) for x, y in GLYPH]
    w = stroke * scale
    draw.line(pts, fill=chalk, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]):  # round caps
        draw.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=chalk)
    for p in pts[1:-1]:  # round joins (PIL's curve joint is approximate)
        draw.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=chalk)
    sx, sy = SPARK_CENTER
    draw.polygon(_sparkle_points(ox + sx * scale, oy + sy * scale, SPARK_R * scale), fill=spark)


def render_tile(size, rounded=True, radius_ratio=0.225, glyph_scale=0.9):
    """Full icon: gradient tile + glyph. Transparent outside rounded corners."""
    big = size * SS
    tile = _gradient(big // SS).resize((big, big), Image.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = big / 1024 * glyph_scale
    off = (big - 1024 * s) / 2
    draw_glyph(d, s, (off, off))
    tile.alpha_composite(layer)
    if rounded:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * radius_ratio), fill=255)
        tile.putalpha(mask)
    return tile.resize((size, size), Image.LANCZOS)


def render_glyph_only(size, glyph_scale, monochrome=False):
    """Transparent canvas with the glyph centred (adaptive-icon foreground)."""
    big = size * SS
    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = big / 1024 * glyph_scale
    off = (big - 1024 * s) / 2
    white = (255, 255, 255)
    draw_glyph(d, s, (off, off), chalk=white if monochrome else CHALK, spark=white if monochrome else SPARK)
    return layer.resize((size, size), Image.LANCZOS)
