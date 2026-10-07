#!/usr/bin/env python3
"""Report how much of each CJK character set the theme fonts can draw.

Reads Rockbox .fnt files (RB12 format). A character counts as covered when
the font has its own glyph for it; characters without one are drawn as the
font's default character (a blank space in the musicOS fonts).

Usage: python3 scripts/font_coverage.py [FONT.fnt ...]

With no arguments, every .fnt file in rockbox/fonts/ is checked.
"""

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = struct.Struct("<4s4H6I")  # magic, maxwidth, height, ascent, depth, then
# firstchar, defaultchar, size, bits_size, noffset, nwidth


def load(path):
    """Return a function telling whether the font has a glyph for a code point."""
    data = path.read_bytes()
    magic, _, _, _, _, first, default, size, bits_size, noffset, _ = HEADER.unpack_from(data)
    if magic != b"RB12":
        raise ValueError(f"{path}: not a Rockbox font")
    start = HEADER.size + bits_size
    if bits_size < 0xFFDB:  # Rockbox switches to 32-bit offsets above this size
        offsets = struct.unpack_from(f"<{noffset}H", data, (start + 1) & ~1)
    else:
        offsets = struct.unpack_from(f"<{noffset}I", data, (start + 3) & ~3)
    # The font converter points characters without a glyph at the default glyph.
    default_offset = offsets[default - first]

    def has(cp):
        i = cp - first
        return 0 <= i < size and (cp == default or offsets[i] != default_offset)

    return has


def double_byte(codec, first, last):
    """Characters of a legacy double-byte character set between two byte codes."""
    chars = []
    for code in range(first, last + 1):
        lead, trail = divmod(code, 256)
        if trail < 0x40:
            continue
        try:
            text = bytes([lead, trail]).decode(codec)
        except UnicodeDecodeError:
            continue
        if len(text) == 1:
            chars.append(ord(text))
    return chars


CHARSETS = [
    ("Korean", "Hangul syllables, all", range(0xAC00, 0xD7A4)),
    ("Korean", "KS X 1001 Hangul", double_byte("euc_kr", 0xB0A1, 0xC8FE)),
    ("Japanese", "Hiragana and katakana", [*range(0x3041, 0x3097), *range(0x30A1, 0x30FB), 0x30FC]),
    ("Japanese", "JIS X 0208 kanji, level 1", double_byte("euc_jp", 0xB0A1, 0xCFD3)),
    ("Japanese", "JIS X 0208 kanji, level 2", double_byte("euc_jp", 0xD0A1, 0xF4A6)),
    ("Chinese", "GB 2312 level 1 (Simplified)", double_byte("gb2312", 0xB0A1, 0xD7F9)),
    ("Chinese", "GB 2312 level 2 (Simplified)", double_byte("gb2312", 0xD8A1, 0xF7FE)),
    ("Chinese", "Big5 common (Traditional)", double_byte("big5", 0xA440, 0xC67E)),
]


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    fonts = [Path(a) for a in args] or sorted((ROOT / "rockbox" / "fonts").glob("*.fnt"))
    for font in fonts:
        has = load(font)
        print(font.name)
        for language, name, chars in CHARSETS:
            chars = list(chars)
            covered = sum(map(has, chars))
            print(f"  {language:9} {name:30} {covered:6,} / {len(chars):<6,} {covered / len(chars):7.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
