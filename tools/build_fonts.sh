#!/usr/bin/env bash
# Rebuild the musicOS CJK fonts from the original Latin-only Inter .fnt files
# (tools/base/) plus Noto Sans CJK glyphs.
#
#   tools/build_fonts.sh            # Simplified Chinese glyph forms (default)
#   CJK_LANG=jp tools/build_fonts.sh   # Japanese forms   (also: tc, kr)
#   EXT_A=1 tools/build_fonts.sh       # add CJK Extension A (~6.5k rare hanzi)
#
# Requires: python3 with freetype-py (pip install freetype-py), curl.
set -euo pipefail
cd "$(dirname "$0")/.."

CJK_LANG=${CJK_LANG:-sc}
SRC=${CJK_SRC_DIR:-build/srcfonts}
PY=${PYTHON:-python3}
EXTRA=()
[ "${EXT_A:-0}" = "1" ] && EXTRA+=(--ext-a)

case "$CJK_LANG" in
  sc) DIR=SimplifiedChinese ;;
  tc) DIR=TraditionalChinese ;;
  jp) DIR=Japanese ;;
  kr) DIR=Korean ;;
  *) echo "CJK_LANG must be sc, tc, jp or kr" >&2; exit 1 ;;
esac
BASE_URL="https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/$DIR"

mkdir -p "$SRC"
for w in Medium Bold; do
  f="$SRC/NotoSansCJK$CJK_LANG-$w.otf"
  [ -f "$f" ] || curl -L -o "$f" "$BASE_URL/NotoSansCJK$CJK_LANG-$w.otf"
done

# CJK em size is ~0.85x the nominal Inter size so ideographs fit inside the
# existing ascent/descent and sit at roughly 1.25x the Latin cap height.
$PY tools/build_cjk_fonts.py --in tools/base/20-Inter-SemiBold.fnt \
  --cjk "$SRC/NotoSansCJK$CJK_LANG-Medium.otf" --px 17 "${EXTRA[@]}" \
  --out rockbox/fonts/20-InterCJK-SemiBold.fnt
$PY tools/build_cjk_fonts.py --in tools/base/15-Inter-Bold.fnt \
  --cjk "$SRC/NotoSansCJK$CJK_LANG-Bold.otf" --px 13 "${EXTRA[@]}" \
  --out rockbox/fonts/15-InterCJK-Bold.fnt
$PY tools/build_cjk_fonts.py --in tools/base/13-Inter-SemiBold.fnt \
  --cjk "$SRC/NotoSansCJK$CJK_LANG-Medium.otf" --px 11 "${EXTRA[@]}" \
  --out rockbox/fonts/13-InterCJK-SemiBold.fnt

ls -la rockbox/fonts/
