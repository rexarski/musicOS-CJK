#!/usr/bin/env python3
"""
Render text with a Rockbox .fnt to a PNG so a font can be checked without a
device.  Draws each line with the given font, black on white, scaled up.

Usage:
    preview_fnt.py --out preview.png --scale 3 \
        FONT.fnt "text line" [FONT2.fnt "text line" ...]

Requires: pip install pillow
"""

import argparse
import struct
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("pillow is required:  pip install pillow")


def read_fnt(path):
    data = open(path, "rb").read()
    maxw, height, ascent, depth = struct.unpack("<HHHH", data[4:12])
    first, defc, size, nbits, _, _ = struct.unpack("<IIIIII", data[12:36])
    pos = 36
    bits = data[pos:pos + nbits]
    pos += nbits
    if nbits >= 0xFFDB:
        pos = (pos + 3) & ~3
        offsets = struct.unpack(f"<{size}I", data[pos:pos + 4 * size])
        pos += 4 * size
    else:
        pos = (pos + 1) & ~1
        offsets = struct.unpack(f"<{size}H", data[pos:pos + 2 * size])
        pos += 2 * size
    widths = data[pos:pos + size]
    return dict(height=height, first=first, defc=defc, size=size, bits=bits,
                offsets=offsets, widths=widths, depth=depth)


def glyph(f, cp):
    if cp < f["first"] or cp >= f["first"] + f["size"]:
        cp = f["defc"]
    i = cp - f["first"]
    w, o, h = f["widths"][i], f["offsets"][i], f["height"]
    px = []
    for k in range(w * h):
        b = f["bits"][o + (k >> 1)]
        px.append((b >> (4 * (k & 1))) & 15)
    return w, px


def draw_line(f, text):
    h = f["height"]
    glyphs = [glyph(f, ord(ch)) for ch in text]
    width = sum(w for w, _ in glyphs) or 1
    img = Image.new("L", (width, h), 255)
    x = 0
    for w, px in glyphs:
        for k, v in enumerate(px):
            img.putpixel((x + k % w, k // w), v * 17)
        x += w
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("pairs", nargs="+", help="FONT.fnt TEXT [FONT.fnt TEXT ...]")
    args = ap.parse_args()
    if len(args.pairs) % 2:
        sys.exit("arguments must be FONT TEXT pairs")

    lines = []
    for i in range(0, len(args.pairs), 2):
        f = read_fnt(args.pairs[i])
        lines.append(draw_line(f, args.pairs[i + 1]))

    pad = 6
    W = max(im.width for im in lines) + 2 * pad
    H = sum(im.height + pad for im in lines) + pad
    canvas = Image.new("L", (W, H), 255)
    y = pad
    for im in lines:
        canvas.paste(im, (pad, y))
        y += im.height + pad
    canvas = canvas.resize((W * args.scale, H * args.scale), Image.NEAREST)
    canvas.save(args.out)
    print(f"wrote {args.out} ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()
