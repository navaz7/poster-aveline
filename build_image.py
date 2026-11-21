#!/usr/bin/env python3
"""Build a vintage travel poster for AVELINE, a place that isn't there.

Flat, limited-palette poster in the style of 1930s railway lithographs:
a cliffside city of stairs above a turquoise sea. Rendered entirely with
Pillow primitives (no external assets) at 1024x1024.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# --- Limited vintage palette ---------------------------------------------
INK = (43, 33, 24)            # dark brown-black ink
CREAM = (247, 236, 203)       # sky top / paper cream
PALE_GOLD = (238, 199, 118)   # sky bottom
SUN = (232, 158, 52)          # low sun disc
SUN_RING = (178, 62, 38)      # crimson-terracotta ring
TEAL_DARK = (13, 74, 79)      # deep sea shadow
TEAL = (18, 99, 102)          # deep teal sea
TEAL_LIGHT = (52, 143, 138)   # sea highlight
CLIFF_FAR = (196, 128, 74)    # ochre, distant cliff
CLIFF_NEAR = (166, 95, 46)    # darker ochre, near cliff
CLIFF_SHADOW = (128, 68, 34)
ROOF = (172, 58, 36)          # terracotta roofs
ROOF_DARK = (142, 44, 30)
CRIMSON = (164, 38, 32)       # crimson accents
WALL_CREAM = (243, 226, 182)  # house walls
WALL_OCHRE = (226, 178, 106)
WALL_ROSE = (214, 141, 96)
STAIR = (250, 242, 214)       # cream stair path


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_centered(draw, cx, y, text, fnt, fill, tracking=0):
    """Draw text centred at cx; optional letter tracking (px per char)."""
    if tracking <= 0:
        draw.text((cx, y), text, font=fnt, fill=fill, anchor="ma")
        return
    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=fnt)
        widths.append(bbox[2] - bbox[0])
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="la")
        x += w + tracking


def text_width(draw, text, fnt, tracking=0):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    if tracking:
        w += tracking * (len(text) - 1)
    return w


def gradient_sky(img):
    """Vertical cream -> pale gold gradient for the top ~72% of the poster."""
    draw = ImageDraw.Draw(img)
    top, bottom = CREAM, PALE_GOLD
    sky_h = 740
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        # gentle ease so the gold gathers near the horizon
        t = t * t * 0.35 + t * 0.65
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=c)


def house(draw, x, y, w, h, wall, roof=ROOF):
    """One simple geometric house: rectangle wall + triangular roof + door."""
    draw.rectangle([x, y, x + w, y + h], fill=wall)
    # roof overhangs the walls slightly
    draw.polygon(
        [(x - 5, y), (x + w + 5, y), (x + w // 2, y - int(w * 0.42))],
        fill=roof,
    )
    # door and one small window, in ink
    dw = max(6, w // 5)
    draw.rectangle([x + w // 2 - dw // 2, y + h - int(h * 0.45),
                    x + w // 2 + dw // 2, y + h], fill=INK)
    ww = max(5, w // 6)
    wx = x + w // 5
    draw.rectangle([wx, y + h // 4, wx + ww, y + h // 4 + ww], fill=INK)


def sailboat(draw, cx, cy, scale, hull=INK, sail=CREAM, accent=CRIMSON):
    """Simple sailboat: hull trapezoid, mast, two triangular sails."""
    s = scale
    # hull
    draw.polygon(
        [(cx - 34 * s, cy), (cx + 34 * s, cy),
         (cx + 22 * s, cy + 13 * s), (cx - 22 * s, cy + 13 * s)],
        fill=hull,
    )
    # mast
    draw.line([(cx, cy), (cx, cy - 58 * s)], fill=INK, width=max(2, int(3 * s)))
    # main sail (right) and jib (left)
    draw.polygon(
        [(cx + 3 * s, cy - 56 * s), (cx + 3 * s, cy - 4 * s), (cx + 30 * s, cy - 4 * s)],
        fill=sail,
    )
    draw.polygon(
        [(cx - 3 * s, cy - 50 * s), (cx - 3 * s, cy - 4 * s), (cx - 26 * s, cy - 4 * s)],
        fill=accent,
    )


def bird(draw, cx, cy, s, colour=INK):
    """Stylised gull: two strokes meeting in a shallow dipped V."""
    w = max(3, int(3 * s))
    draw.line([(cx - 17 * s, cy - 7 * s), (cx, cy + 3 * s)], fill=colour, width=w)
    draw.line([(cx, cy + 3 * s), (cx + 17 * s, cy - 7 * s)], fill=colour, width=w)


def main():
    random.seed(7)
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # ---- Sky ------------------------------------------------------------
    gradient_sky(img)
    draw = ImageDraw.Draw(img)

    # ---- Sun: large, low, sitting just above the horizon ---------------
    sun_cx, sun_cy, sun_r = 512, 468, 178
    draw.ellipse([sun_cx - sun_r - 14, sun_cy - sun_r - 14,
                  sun_cx + sun_r + 14, sun_cy + sun_r + 14], outline=SUN_RING, width=6)
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r,
                  sun_cx + sun_r, sun_cy + sun_r], fill=SUN)
    # thin horizontal banding across the sun for a lithograph feel;
    # each line is clipped to the chord width at its height
    for i, yy in enumerate(range(sun_cy + 40, sun_cy + sun_r - 6, 26)):
        dy = yy - sun_cy
        half = int(math.sqrt(max(0, sun_r * sun_r - dy * dy))) - 16
        draw.line([(sun_cx - half, yy), (sun_cx + half, yy)],
                  fill=SUN_RING if i % 2 == 0 else SUN, width=3)

    # ---- Distant headland (right, behind the city) ----------------------
    draw.polygon(
        [(640, 742), (760, 560), (880, 520), (1024, 600), (1024, 780), (640, 780)],
        fill=CLIFF_FAR,
    )

    # ---- Sea band --------------------------------------------------------
    sea_top = 742
    draw.rectangle([0, sea_top, W, H], fill=TEAL)
    draw.rectangle([0, sea_top, W, sea_top + 10], fill=TEAL_LIGHT)
    # gentle wave dashes in the sea
    for row, yy in enumerate(range(sea_top + 46, H - 120, 44)):
        offset = 30 if row % 2 else 0
        for xx in range(40 + offset, W - 60, 130):
            draw.line([(xx, yy), (xx + 44, yy)], fill=TEAL_LIGHT, width=4)

    # ---- Main cliff (left and centre), city-bearing ----------------------
    cliff = [
        (0, 470), (120, 430), (250, 452), (360, 500), (440, 560),
        (500, 640), (540, 742), (520, 800), (300, 812), (120, 800), (0, 786),
    ]
    draw.polygon(cliff, fill=CLIFF_NEAR)
    # shadow facet on the cliff face
    draw.polygon(
        [(250, 452), (360, 500), (440, 560), (500, 640), (540, 742),
         (470, 742), (420, 620), (330, 540), (250, 500)],
        fill=CLIFF_SHADOW,
    )
    # harbour quay at the cliff foot
    draw.polygon([(300, 812), (520, 800), (560, 742), (620, 742),
                  (640, 800), (640, 828), (300, 838)], fill=CLIFF_SHADOW)

    # ---- Winding stair path: cream zigzag from harbour to the top --------
    stair_pts = [
        (585, 760), (505, 726), (520, 692), (448, 660), (462, 622),
        (392, 592), (404, 552), (330, 524), (342, 486), (268, 462),
    ]
    draw.line(stair_pts, fill=STAIR, width=13, joint="curve")
    # stair treads: short cross ticks along the path
    for (x1, y1), (x2, y2) in zip(stair_pts, stair_pts[1:]):
        steps = 4
        for i in range(1, steps):
            t = i / steps
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            draw.line([(px - 9, py), (px + 9, py)], fill=CLIFF_NEAR, width=2)

    # ---- Houses climbing the cliff ---------------------------------------
    houses = [
        # (x, y, w, h, wall)
        (52, 452, 62, 48, WALL_CREAM),
        (140, 428, 56, 44, WALL_OCHRE),
        (228, 440, 60, 46, WALL_CREAM),
        (96, 512, 58, 46, WALL_ROSE),
        (196, 500, 64, 50, WALL_CREAM),
        (300, 492, 56, 44, WALL_OCHRE),
        (150, 576, 62, 48, WALL_CREAM),
        (262, 560, 58, 46, WALL_ROSE),
        (356, 548, 60, 46, WALL_CREAM),
        (214, 636, 60, 48, WALL_OCHRE),
        (330, 622, 62, 48, WALL_CREAM),
        (420, 600, 54, 42, WALL_ROSE),
        (300, 700, 58, 44, WALL_CREAM),
        (404, 684, 56, 44, WALL_OCHRE),
    ]
    for hx, hy, hw, hh, wall in houses:
        house(draw, hx, hy, hw, hh, wall,
              roof=ROOF_DARK if (hx // 10) % 3 == 0 else ROOF)

    # a couple of houses on the distant headland
    house(draw, 806, 528, 52, 40, WALL_CREAM)
    house(draw, 884, 552, 48, 38, WALL_OCHRE)

    # slender cypress trees punctuating the slope — classic poster shorthand
    # for a Mediterranean cliff town
    for cx, cy, ch in ((186, 560, 52), (392, 668, 46), (128, 640, 42), (470, 668, 40)):
        draw.polygon([(cx - 9, cy), (cx + 9, cy), (cx, cy - ch)], fill=(38, 84, 62))
        draw.rectangle([cx - 2, cy, cx + 2, cy + 6], fill=INK)

    # ---- Bell tower: the landmark, high on the cliff ---------------------
    tx, ty = 96, 268  # tower top-left (below the title block)
    tw, th = 64, 168
    draw.rectangle([tx, ty + 44, tx + tw, ty + th], fill=WALL_CREAM)
    # pyramidal cap in crimson
    draw.polygon([(tx - 8, ty + 44), (tx + tw + 8, ty + 44), (tx + tw // 2, ty - 6)],
                 fill=CRIMSON)
    draw.ellipse([tx + tw // 2 - 6, ty - 18, tx + tw // 2 + 6, ty - 6], fill=INK)
    # arched belfry opening with a bell
    draw.pieslice([tx + 14, ty + 58, tx + tw - 14, ty + 96], start=180, end=360, fill=INK)
    draw.rectangle([tx + 14, ty + 76, tx + tw - 14, ty + 96], fill=INK)
    draw.polygon([(tx + tw // 2 - 8, ty + 96), (tx + tw // 2 + 8, ty + 96),
                  (tx + tw // 2 + 5, ty + 110), (tx + tw // 2 - 5, ty + 110)], fill=SUN)
    # small window lower down
    draw.rectangle([tx + tw // 2 - 6, ty + 126, tx + tw // 2 + 6, ty + 144], fill=INK)

    # ---- Lighthouse on the harbour point ---------------------------------
    lx, ly = 596, 640  # base area on the quay point
    draw.polygon([(lx, ly + 102), (lx + 16, ly), (lx + 36, ly), (lx + 52, ly + 102)],
                 fill=WALL_CREAM)
    draw.rectangle([lx + 4, ly + 34, lx + 48, ly + 50], fill=CRIMSON)
    draw.rectangle([lx + 9, ly + 68, lx + 43, ly + 82], fill=CRIMSON)
    # lamp room
    draw.rectangle([lx + 14, ly - 20, lx + 38, ly + 2], fill=INK)
    draw.rectangle([lx + 19, ly - 16, lx + 33, ly - 3], fill=PALE_GOLD)
    draw.polygon([(lx + 10, ly - 20), (lx + 42, ly - 20), (lx + 26, ly - 34)], fill=CRIMSON)
    # light beams over the sea
    draw.polygon([(lx + 38, ly - 10), (760, ly - 44), (760, ly + 6)], fill=(214, 178, 96))
    draw.polygon([(lx + 38, ly - 10), (712, ly + 52), (688, ly + 16)], fill=(214, 178, 96))

    # ---- Sailboats in the harbour / on the sea ----------------------------
    sailboat(draw, 742, 838, 1.05)
    sailboat(draw, 872, 884, 0.8, sail=WALL_CREAM, accent=TEAL_DARK)
    sailboat(draw, 636, 902, 0.62, sail=PALE_GOLD, accent=CRIMSON)
    # reflections
    for bx, bw in ((742, 60), (872, 44), (636, 34)):
        pass  # kept minimal: flat poster style, no reflections

    # ---- Birds -------------------------------------------------------------
    for bx, by, bs in ((726, 356, 1.2), (806, 318, 0.95), (884, 398, 1.05),
                       (252, 316, 0.9)):
        bird(draw, bx, by, bs)

    # ---- Typography ---------------------------------------------------------
    # Title across the top
    title_font = font(SERIF_BOLD, 118)
    # shrink to fit inside the frame if needed
    while text_width(draw, "AVELINE", title_font, tracking=10) > 880:
        title_font = font(SERIF_BOLD, title_font.size - 4)
    draw_centered(draw, W // 2, 44, "AVELINE", title_font, INK, tracking=10)

    # rule under the title
    draw.line([(212, 196), (812, 196)], fill=CRIMSON, width=5)
    draw.line([(212, 208), (812, 208)], fill=INK, width=2)

    # Subtitle beneath the title
    sub_font = font(SERIF, 37)
    draw_centered(draw, W // 2, 224, "the City of a Thousand Stairs", sub_font, INK)

    # Tagline near the bottom, on the sea
    tag_font = font(SANS_BOLD, 34)
    tag = "WHERE EVERY STREET GOES UP TO THE SKY"
    while text_width(draw, tag, tag_font, tracking=3) > 900:
        tag_font = font(SANS_BOLD, tag_font.size - 2)
    draw_centered(draw, W // 2, 900, tag, tag_font, CREAM, tracking=3)

    # Footer line
    foot_font = font(SANS, 24)
    draw_centered(draw, W // 2, 948, "Aveline State Railways  ·  Summer Season",
                  foot_font, (196, 222, 214))

    # ---- Border frame -------------------------------------------------------
    draw.rectangle([26, 26, W - 26, H - 26], outline=INK, width=6)
    draw.rectangle([42, 42, W - 42, H - 42], outline=INK, width=2)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
