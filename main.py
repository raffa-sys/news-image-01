# news-image-01 -- "The World in One Image"
# Sums up the world's news of Friday 13 November 2026 in one image.
# A deterministic, stdlib-only program (math, os, random, struct, zlib).
# It draws a newspaper front page and writes one 1024x1024 PNG to
# $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
# No network, no third-party code, no timestamps: two runs write identical bytes.
import math
import os
import random
import struct
import zlib

W = 1024
H = 1024

# ---- palette ----
PAPER = (245, 239, 224)   # warm off-white paper
NAVY = (20, 33, 61)      # masthead / headlines
GOLD = (202, 164, 44)    # masthead rule
INK = (32, 32, 32)       # body text
SOFT = (88, 88, 88)      # footer text
WHITE = (255, 255, 255)
RED = (214, 48, 49)
DARK = (26, 26, 26)
MIDGREY = (70, 70, 70)
LIGHT = (217, 217, 217)
LIGHTER = (240, 240, 240)

# Seeded RNG: the layout is fixed, so output is deterministic; the RNG only
# picks the zigzag phase of the drawn waves, in a fixed call order.
RNG = random.Random(20261113)

# ---- 5x7 bitmap font: each glyph is 7 rows of 5 bits ('1' = ink) ----
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00100", "00000", "00100", "00100", "00100", "10100", "01000"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ';': ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "00000", "00000", "01100", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

# ---- pixel buffer (RGB, row-major) ----
buf = bytearray(bytes(PAPER) * (W * H))


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def draw_line(x0, y0, x1, y1, color, t=1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    half = t // 2
    while True:
        fill_rect(x - half, y - half, t, t, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def polyline(pts, color, t=1):
    for a, b in zip(pts, pts[1:]):
        draw_line(a[0], a[1], b[0], b[1], color, t)


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = math.isqrt(r * r - dy * dy)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def ring(cx, cy, r, color, bg, t):
    fill_circle(cx, cy, r, color)
    fill_circle(cx, cy, r - t, bg)


def fill_tri(p0, p1, p2, color):
    xs = (p0[0], p1[0], p2[0])
    ys = (p0[1], p1[1], p2[1])
    x0 = max(0, min(xs))
    x1 = min(W - 1, max(xs))
    y0 = max(0, min(ys))
    y1 = min(H - 1, max(ys))

    def edge(ax, ay, bx, by, cx, cy):
        return (cx - ax) * (by - ay) - (cy - ay) * (bx - ax)

    area = edge(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1])
    if area == 0:
        return
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            w0 = edge(p1[0], p1[1], p2[0], p2[1], xx, yy)
            w1 = edge(p2[0], p2[1], p0[0], p0[1], xx, yy)
            w2 = edge(p0[0], p0[1], p1[0], p1[1], xx, yy)
            if area > 0:
                inside = w0 >= 0 and w1 >= 0 and w2 >= 0
            else:
                inside = w0 <= 0 and w1 <= 0 and w2 <= 0
            if inside:
                set_px(xx, yy, color)


def wave(cx, y, color):
    # Gentle zigzag wave; the starting phase comes from the seeded RNG,
    # consumed in a fixed order, so the output stays deterministic.
    ph = RNG.choice((0, 1))
    pts = []
    for i in range(9):
        xx = cx - 92 + i * 23
        yy = y + (5 if (i + ph) % 2 == 0 else -5)
        pts.append((xx, yy))
    polyline(pts, color, 3)


# ---- text ----
def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, color, scale=2, bold=False):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '1':
                    bw = scale + (1 if bold else 0)
                    fill_rect(cx + c * scale, y + r * scale, bw, scale, color)
        cx += 6 * scale
    return cx


def wrap(s, scale, maxw):
    lines = []
    cur = ''
    for wd in s.split(' '):
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---- story icons (flat shapes, drawn in the panel's coloured band) ----
def icon_peace(cx, cy, bg):
    ring(cx, cy, 46, WHITE, bg, 7)
    draw_line(cx, cy - 46, cx, cy + 46, WHITE, 7)
    draw_line(cx, cy, cx - 33, cy + 33, WHITE, 7)
    draw_line(cx, cy, cx + 33, cy + 33, WHITE, 7)


def icon_chip(cx, cy, bg):
    # falling chart in red, upper area
    pts = [(cx - 72, cy - 54), (cx - 24, cy - 40), (cx + 24, cy - 20), (cx + 66, cy - 4)]
    polyline(pts, RED, 5)
    fill_tri((cx + 66, cy - 4), (cx + 50, cy - 8), (cx + 60, cy + 8), RED)
    # chip, lower area
    fill_rect(cx - 42, cy + 14, 84, 50, DARK)
    for yy in (cy + 24, cy + 39, cy + 54):
        fill_rect(cx - 52, yy, 10, 6, DARK)
        fill_rect(cx + 42, yy, 10, 6, DARK)
    fill_rect(cx - 24, cy + 26, 48, 26, MIDGREY)


def icon_cloud(cx, cy, bg):
    fill_circle(cx - 32, cy + 8, 24, WHITE)
    fill_circle(cx + 2, cy - 10, 28, WHITE)
    fill_circle(cx + 34, cy + 10, 22, WHITE)
    fill_rect(cx - 56, cy + 8, 112, 24, WHITE)
    draw_line(cx - 26, cy - 26, cx + 26, cy + 26, RED, 8)
    draw_line(cx + 26, cy - 26, cx - 26, cy + 26, RED, 8)


def icon_ship(cx, cy, bg):
    wave(cx, cy + 48, WHITE)
    wave(cx, cy + 60, WHITE)
    fill_rect(cx - 78, cy + 6, 148, 24, LIGHT)
    fill_tri((cx + 70, cy + 6), (cx + 70, cy + 30), (cx + 96, cy + 30), LIGHT)
    fill_rect(cx - 42, cy - 20, 72, 26, LIGHTER)
    fill_rect(cx + 8, cy - 50, 6, 30, LIGHTER)
    fill_rect(cx - 4, cy - 54, 30, 6, LIGHTER)
    fill_rect(cx + 36, cy - 8, 26, 14, (200, 200, 200))
    draw_line(cx + 62, cy - 2, cx + 82, cy - 8, (200, 200, 200), 4)


def icon_cross(cx, cy, bg):
    ring(cx, cy, 56, WHITE, bg, 4)
    fill_rect(cx - 11, cy - 36, 22, 72, WHITE)
    fill_rect(cx - 36, cy - 11, 72, 22, WHITE)


def icon_tanker(cx, cy, bg):
    wave(cx, cy + 44, WHITE)
    wave(cx, cy + 56, WHITE)
    fill_rect(cx - 86, cy + 8, 150, 20, LIGHT)
    fill_tri((cx + 64, cy + 8), (cx + 64, cy + 28), (cx + 88, cy + 28), LIGHT)
    fill_rect(cx + 28, cy - 18, 30, 26, LIGHTER)
    fill_rect(cx + 44, cy - 32, 12, 14, (180, 180, 180))
    # naval mine: dark spiked circle, upper left
    mx, my = cx - 62, cy - 28
    fill_circle(mx, my, 15, DARK)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x0 = mx + int(13 * math.cos(rad))
        y0 = my + int(13 * math.sin(rad))
        x1 = mx + int(24 * math.cos(rad))
        y1 = my + int(24 * math.sin(rad))
        draw_line(x0, y0, x1, y1, DARK, 4)
    fill_circle(mx, my, 5, (90, 90, 90))


# ---- the six verified stories of Friday 13 November 2026 ----
# (headline, one-line summary of at most 70 chars, band colour, icon)
STORIES = [
    ("UKRAINE PEACE TALKS",
     "Putin meets US envoys; Europe gets a seat; biggest swap planned.",
     (0, 87, 183), icon_peace),
    ("NVIDIA CEO RESIGNS",
     "Jensen Huang steps down; shares fall 16%; Kress is interim chief.",
     (118, 185, 0), icon_chip),
    ("MICROSOFT 365 DOWN",
     "Mail and Teams fail worldwide as servers drop offline.",
     (0, 120, 212), icon_cloud),
    ("CHINA-TAIWAN DRILLS",
     "Taiwan details China's large unannounced Pacific naval drills.",
     (46, 74, 98), icon_ship),
    ("GAZA HOSPITAL STRIKE",
     "Strike on Khan Younis hospital kills six, including a surgeon.",
     (15, 118, 110), icon_cross),
    ("HORMUZ TANKER HIT",
     "LNG tanker struck by a naval mine in the Strait of Hormuz.",
     (14, 77, 100), icon_tanker),
]


def draw_panel(px, py, title, summary, band, icon):
    # border + white body
    fill_rect(px, py, 480, 253, NAVY)
    fill_rect(px + 2, py + 2, 476, 249, WHITE)
    # coloured icon band
    fill_rect(px + 2, py + 2, 476, 140, band)
    icon(px + 240, py + 72, band)
    # bold headline
    draw_text(px + 18, py + 158, title, NAVY, 3, bold=True)
    # summary, wrapped to at most two lines, dark on white
    lines = wrap(summary, 2, 480 - 36)
    ly = py + 189
    for ln in lines[:2]:
        draw_text(px + 18, ly, ln, INK, 2)
        ly += 20


def draw_page():
    # masthead: dark bar with the date, gold rule beneath
    fill_rect(0, 0, W, 76, NAVY)
    fill_rect(0, 76, W, 4, GOLD)
    date = "FRIDAY 13 NOVEMBER 2026"
    draw_text((W - text_w(date, 3)) // 2, 27, date, WHITE, 3, bold=True)
    # big headline
    head = "THE WORLD IN ONE IMAGE"
    draw_text((W - text_w(head, 5)) // 2, 102, head, NAVY, 5, bold=True)
    # rule under the headline
    fill_rect(24, 152, W - 48, 3, NAVY)
    # six story panels, 2 columns x 3 rows
    for idx, (title, summary, band, icon) in enumerate(STORIES):
        col = idx % 2
        row = idx // 2
        px = 24 + col * (480 + 16)
        py = 168 + row * (253 + 16)
        draw_panel(px, py, title, summary, band, icon)
    # footer rule + line
    fill_rect(24, 968, W - 48, 2, NAVY)
    foot = "13 November 2026 - the day in six stories"
    draw_text((W - text_w(foot, 2)) // 2, 988, foot, SOFT, 2)


# ---- minimal pure-stdlib PNG encoder (RGB, no filtering) ----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += _chunk(b"IHDR", ihdr)
    out += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += _chunk(b"IEND", b"")
    return out


def main():
    draw_page()
    data = png_bytes()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
