#!/usr/bin/env python3
"""
Inject CJK glyphs into an existing Rockbox .fnt font.

Rockbox has no font fallback: every glyph a viewport draws has to live in the
one .fnt file that viewport uses, otherwise the "default" glyph (a space in the
musicOS Inter fonts) is drawn instead and CJK text simply vanishes.

This tool keeps every glyph of the original font byte-for-byte and only adds
glyphs, rendered with FreeType from a TTF/OTF, for codepoints the original
font does not have.  The result is a strict superset of the input font with
the same height, ascent and look for Latin text.

File format (RB12, written by Rockbox's tools/convttf.c, read by firmware/font.c):

    "RB12"
    u16 maxwidth, u16 height, u16 ascent, u16 depth (1 = 4-bit antialiased)
    u32 firstchar, u32 defaultchar, u32 size (number of codepoints)
    u32 nbits (bytes of glyph data), u32 noffset, u32 nwidth
    glyph data: per glyph, height rows of width pixels, 4 bits per pixel,
                two pixels per byte, low nibble first, 15 = blank, 0 = full ink
    pad to 4 bytes, then u32 offset[size]   (u16 when nbits < 0xFFDB)
    u8 width[size]
    Codepoints without a glyph reuse the default glyph's offset and width.

Usage:
    build_cjk_fonts.py --in 20-Inter-SemiBold.fnt --cjk NotoSansCJKsc-Medium.otf \
        --px 17 --out 20-InterCJK-SemiBold.fnt [--ext-a] [--light] [--ranges all|core]

Requires: pip install freetype-py
"""

import argparse
import struct
import sys

try:
    import freetype
except ImportError:  # pragma: no cover
    sys.exit("freetype-py is required:  pip install freetype-py")

# Unicode blocks that make up "CJK support" for music tags.  BMP only: Rockbox
# stores codepoints as 16-bit values, so Extension B and later cannot be used.
CORE_RANGES = [
    (0x2E80, 0x2FDF, "CJK radicals / Kangxi radicals"),
    (0x3000, 0x303F, "CJK symbols and punctuation"),
    (0x3040, 0x309F, "Hiragana"),
    (0x30A0, 0x30FF, "Katakana"),
    (0x3100, 0x312F, "Bopomofo"),
    (0x3130, 0x318F, "Hangul compatibility jamo"),
    (0x31A0, 0x31BF, "Bopomofo extended"),
    (0x31F0, 0x31FF, "Katakana phonetic extensions"),
    (0x3200, 0x33FF, "Enclosed CJK letters, CJK compatibility"),
    (0x4E00, 0x9FFF, "CJK unified ideographs"),
    (0xAC00, 0xD7A3, "Hangul syllables"),
    (0xF900, 0xFAFF, "CJK compatibility ideographs"),
    (0xFE30, 0xFE4F, "CJK compatibility forms"),
    (0xFF00, 0xFFEF, "Halfwidth and fullwidth forms"),
]
EXT_A_RANGE = (0x3400, 0x4DBF, "CJK unified ideographs extension A")


def read_fnt(path):
    data = open(path, "rb").read()
    if data[:4] != b"RB12":
        raise SystemExit(f"{path}: not an RB12 Rockbox font")
    maxw, height, ascent, depth = struct.unpack("<HHHH", data[4:12])
    first, defc, size, nbits, noffset, nwidth = struct.unpack("<IIIIII", data[12:36])
    if depth != 1:
        raise SystemExit(f"{path}: only 4-bit antialiased fonts (depth=1) are supported")
    if noffset != size or nwidth != size:
        raise SystemExit(f"{path}: unexpected offset/width table sizes")
    pos = 36
    bits = bytearray(data[pos:pos + nbits])
    pos += nbits
    if nbits >= 0xFFDB:
        pos = (pos + 3) & ~3
        offsets = list(struct.unpack(f"<{size}I", data[pos:pos + 4 * size]))
        pos += 4 * size
    else:
        pos = (pos + 1) & ~1
        offsets = list(struct.unpack(f"<{size}H", data[pos:pos + 2 * size]))
        pos += 2 * size
    widths = list(data[pos:pos + size])
    return {
        "maxw": maxw, "height": height, "ascent": ascent, "first": first,
        "defc": defc, "bits": bits, "offsets": offsets, "widths": widths,
    }


def write_fnt(path, f):
    size = len(f["offsets"])
    nbits = len(f["bits"])
    out = bytearray(b"RB12")
    out += struct.pack("<HHHH", f["maxw"], f["height"], f["ascent"], 1)
    out += struct.pack("<IIIIII", f["first"], f["defc"], size, nbits, size, size)
    out += f["bits"]
    if nbits >= 0xFFDB:
        out += b"\0" * (((nbits + 3) & ~3) - nbits)
        out += struct.pack(f"<{size}I", *f["offsets"])
    else:
        out += b"\0" * (((nbits + 1) & ~1) - nbits)
        out += struct.pack(f"<{size}H", *f["offsets"])
    out += bytes(f["widths"])
    open(path, "wb").write(out)


def has_glyph(f, cp):
    i = cp - f["first"]
    if i < 0 or i >= len(f["offsets"]):
        return False
    if cp == f["defc"]:
        return True
    return f["offsets"][i] != f["offsets"][f["defc"] - f["first"]]


def render_glyph(face, cp, height, ascent, flags):
    """Return (width, packed_bytes, clipped) or None if the face lacks cp."""
    gi = face.get_char_index(cp)
    if gi == 0:
        return None
    face.load_glyph(gi, flags)
    g = face.glyph
    bm = g.bitmap
    adv = (g.advance.x + 32) >> 6
    w = max(adv, bm.width)
    if w == 0:
        return None
    if w > 255:
        raise SystemExit(f"U+{cp:04X}: glyph width {w} does not fit in a byte")

    grid = bytearray(b"\x0f") * (w * height)
    x0 = g.bitmap_left
    if x0 < 0:
        x0 = 0
    if x0 + bm.width > w:
        x0 = w - bm.width
    y0 = ascent - g.bitmap_top
    clipped = False
    buf = bm.buffer
    for r in range(bm.rows):
        y = y0 + r
        if y < 0 or y >= height:
            if any(buf[r * bm.pitch + c] > 64 for c in range(bm.width)):
                clipped = True
            continue
        row = r * bm.pitch
        base = y * w + x0
        for c in range(bm.width):
            grid[base + c] = (255 - buf[row + c] + 8) // 17

    packed = bytearray((w * height + 1) // 2)
    for k in range(w * height):
        if k & 1:
            packed[k >> 1] |= grid[k] << 4
        else:
            packed[k >> 1] = grid[k]
    return w, packed, clipped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="src", required=True, help="existing Rockbox .fnt (kept intact)")
    ap.add_argument("--cjk", required=True, help="TTF/OTF providing the CJK glyphs")
    ap.add_argument("--px", type=int, required=True, help="em size in pixels for the CJK glyphs")
    ap.add_argument("--out", required=True, help="output .fnt")
    ap.add_argument("--ext-a", action="store_true", help="also include CJK Extension A (adds ~6.5k glyphs)")
    ap.add_argument("--light", action="store_true", help="use FreeType light hinting")
    ap.add_argument("--face-index", type=int, default=0, help="face index inside a .ttc")
    args = ap.parse_args()

    font = read_fnt(args.src)
    face = freetype.Face(args.cjk, args.face_index)
    face.set_pixel_sizes(0, args.px)
    flags = freetype.FT_LOAD_RENDER | (
        freetype.FT_LOAD_TARGET_LIGHT if args.light else freetype.FT_LOAD_TARGET_NORMAL
    )

    ranges = list(CORE_RANGES) + ([EXT_A_RANGE] if args.ext_a else [])
    last_cp = max(hi for _, hi, _ in ranges)
    first = font["first"]
    if last_cp - first + 1 > len(font["offsets"]):
        def_off = font["offsets"][font["defc"] - first]
        def_w = font["widths"][font["defc"] - first]
        extra = last_cp - first + 1 - len(font["offsets"])
        font["offsets"] += [def_off] * extra
        font["widths"] += [def_w] * extra

    added = skipped = missing = clipped_total = 0
    per_range = []
    for lo, hi, name in ranges:
        n = 0
        for cp in range(lo, hi + 1):
            if cp < first:
                continue
            if has_glyph(font, cp):
                skipped += 1
                continue
            res = render_glyph(face, cp, font["height"], font["ascent"], flags)
            if res is None:
                missing += 1
                continue
            w, packed, clipped = res
            clipped_total += clipped
            i = cp - first
            font["offsets"][i] = len(font["bits"])
            font["widths"][i] = w
            font["bits"] += packed
            font["maxw"] = max(font["maxw"], w)
            n += 1
        per_range.append((name, n))
        added += n

    write_fnt(args.out, font)
    print(f"{args.out}: height {font['height']} ascent {font['ascent']} maxwidth {font['maxw']}, "
          f"{len(font['offsets'])} codepoints, {len(font['bits'])} glyph bytes")
    for name, n in per_range:
        print(f"  +{n:6d}  {name}")
    print(f"  added {added}, already present {skipped}, not in CJK font {missing}, "
          f"vertically clipped {clipped_total}")
    if clipped_total:
        print("  warning: some glyphs were clipped, consider a smaller --px", file=sys.stderr)


if __name__ == "__main__":
    main()
