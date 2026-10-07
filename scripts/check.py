#!/usr/bin/env python3
"""Validate the musicOS theme files in rockbox/.

Errors (exit status 1):
  - a theme .cfg points at a /.rockbox/ path that does not exist
  - a skin loads a bitmap or font that does not exist
  - a bitmap is not a BMP that Rockbox can load, or a font is not a
    Rockbox font
  - a sprite sheet's height is not a multiple of its sub-image count

Warnings (errors with --strict):
  - bitmaps that no skin loads (they still ship in the package)
  - a dark variant that loads a different set of bitmaps than its light
    counterpart

Usage: python3 scripts/check.py [--strict]
"""

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "rockbox"
SKIN_EXTS = (".wps", ".sbs", ".fms")

# '#' starts a comment that runs to the end of the line; '%#' is a literal '#'.
COMMENT_RE = re.compile(r"(?<!%)#.*$", re.MULTILINE)
BMP_RE = re.compile(r"[\w-]+\.bmp")
# %xl(label, filename, x, y[, number of sub-images])
PRELOAD_RE = re.compile(r"%xl\(([^)]*)\)")
# %Fl(id, filename[, glyph cache size])
FONT_RE = re.compile(r"%Fl\(\s*\d+\s*,\s*([^,)]+?)\s*[,)]")

BMP_DEPTHS = {1, 4, 8, 16, 24, 32}
BMP_COMPRESSION = {0: "BI_RGB", 3: "BI_BITFIELDS"}


class Report:
    def __init__(self, strict):
        self.strict = strict
        self.errors = 0
        self.warnings = 0

    def error(self, where, message):
        self.errors += 1
        print(f"error: {where}: {message}")

    def warning(self, where, message):
        if self.strict:
            self.error(where, message)
            return
        self.warnings += 1
        print(f"warning: {where}: {message}")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def read_skin(path):
    return COMMENT_RE.sub("", path.read_text(encoding="utf-8"))


def bmp_height(path, report):
    """Return the height of a loadable BMP, or None after reporting an error."""
    data = path.read_bytes()[:54]
    if len(data) < 54 or data[:2] != b"BM":
        report.error(rel(path), "not a BMP file")
        return None
    header_size, width, height, _planes, depth, compression = struct.unpack(
        "<IiiHHI", data[14:34]
    )
    if header_size < 40 or width <= 0 or height == 0:
        report.error(rel(path), "unsupported BMP header")
        return None
    if depth not in BMP_DEPTHS:
        report.error(rel(path), f"unsupported colour depth ({depth} bpp)")
        return None
    if compression not in BMP_COMPRESSION:
        report.error(rel(path), f"unsupported compression (type {compression})")
        return None
    # A negative height marks a top-down bitmap.
    return abs(height)


def check_fonts(report):
    for font in sorted((THEME / "fonts").iterdir()):
        if font.is_file() and font.read_bytes()[:4] != b"RB12":
            report.error(rel(font), "not a Rockbox font (missing RB12 header)")


def check_cfgs(report):
    cfgs = sorted((THEME / "themes").glob("*.cfg"))
    if not cfgs:
        report.error(rel(THEME / "themes"), "no theme .cfg files found")
    for cfg in cfgs:
        for number, line in enumerate(cfg.read_text(encoding="utf-8").splitlines(), 1):
            key, sep, value = line.partition(":")
            value = value.strip()
            if line.lstrip().startswith("#") or not sep or not value.startswith("/.rockbox/"):
                continue
            if not (THEME / value[len("/.rockbox/"):]).is_file():
                report.error(f"{rel(cfg)}:{number}", f"{key.strip()} points at missing file {value}")
    return len(cfgs)


def check_bitmap_files(report):
    """Validate every bitmap once; return {path: height, or None if unloadable}."""
    return {
        image: bmp_height(image, report)
        for image_dir in sorted(p for p in (THEME / "wps").iterdir() if p.is_dir())
        for image in sorted(image_dir.glob("*.bmp"))
    }


def check_skins(report, heights):
    """Check every skin file; return {skin path: set of bitmap names it loads}."""
    loaded = {}
    for skin in sorted(p for p in (THEME / "wps").iterdir() if p.suffix in SKIN_EXTS):
        text = read_skin(skin)
        image_dir = skin.with_suffix("")
        names = set(BMP_RE.findall(text))
        loaded[skin] = names

        for name in sorted(names):
            if not (image_dir / name).is_file():
                report.error(rel(skin), f"loads missing bitmap {rel(image_dir / name)}")

        for font in sorted(set(FONT_RE.findall(text))):
            if not (THEME / "fonts" / font).is_file():
                report.error(rel(skin), f"loads missing font fonts/{font}")

        for args in PRELOAD_RE.findall(text):
            fields = [field.strip() for field in args.split(",")]
            if len(fields) < 5 or not fields[4].isdigit():
                continue
            name, count = fields[1], int(fields[4])
            height = heights.get(image_dir / name)
            if count >= 1 and height is not None and height % count:
                report.error(
                    rel(skin),
                    f"{name} is {height}px tall, not a multiple of its {count} sub-images",
                )
    return loaded


def check_unused(report, loaded):
    for image_dir in sorted(p for p in (THEME / "wps").iterdir() if p.is_dir()):
        used = set()
        for ext in SKIN_EXTS:
            used |= loaded.get(image_dir.with_suffix(ext), set())
        unused = [image.name for image in sorted(image_dir.glob("*.bmp")) if image.name not in used]
        if unused:
            report.warning(
                rel(image_dir) + "/",
                f"{len(unused)} bitmap(s) not loaded by any skin: {', '.join(unused)}",
            )


def check_variants(report, loaded):
    for skin, names in loaded.items():
        if not skin.stem.endswith("_dark"):
            continue
        light = skin.with_name(skin.stem[: -len("_dark")] + skin.suffix)
        if light not in loaded:
            continue
        only_light = sorted(loaded[light] - names)
        only_dark = sorted(names - loaded[light])
        if only_light or only_dark:
            report.warning(
                rel(skin),
                f"loads different bitmaps than {light.name} "
                f"(only light: {only_light or '-'}; only dark: {only_dark or '-'})",
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    report = Report(args.strict)
    themes = check_cfgs(report)
    heights = check_bitmap_files(report)
    loaded = check_skins(report, heights)
    check_unused(report, loaded)
    check_variants(report, loaded)
    check_fonts(report)

    print(
        f"checked {themes} theme(s), {len(loaded)} skin file(s), {len(heights)} bitmap(s): "
        f"{report.errors} error(s), {report.warnings} warning(s)"
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
