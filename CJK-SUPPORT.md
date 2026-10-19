# CJK support in musicOS

Notes gathered from the Rockbox manual (iPod Video build, sections 8.5, 8.6.3,
13.1.5, 13.2.4, appendix D) and the Rockbox sources (`firmware/font.c`,
`tools/convttf.c`, `apps/settings_list.c`), and what was done with them.

## Why CJK text was blank

1. **Rockbox has no font fallback.** Each viewport draws with exactly one
   `.fnt` file. Any codepoint the file does not contain is drawn with the
   font's *default glyph*. The musicOS Inter fonts were converted with
   `convttf`, whose default glyph is the first character in the font, a space.
   So every Chinese, Japanese or Korean character became an invisible space.
2. **Every text viewport needs the glyphs.** The theme uses four font slots:
   the UI font from `musicOS_v2.cfg` (`font:`), plus `%Fl(2..4, …)` in the
   `.wps` and `.sbs` for title, artist, mini-player and menu title. All of them
   have to be CJK-capable, or CJK will vanish on some screens only.
3. **Bitmap only.** A `.fnt` is a fixed-size bitmap font, so each size the
   theme uses (13, 15 and 20) needs its own CJK build. There is no scaling.

## What the fonts are now

`rockbox/fonts/*-InterCJK-*.fnt` are the original Inter bitmaps with Noto Sans
CJK glyphs appended for the codepoints Inter lacks. Latin text renders
identically to upstream musicOS (the original glyph bytes are copied
unchanged); only the missing codepoints were added.

| Font | Inter size | CJK em | Height / ascent | Glyphs added | Size |
| --- | --- | --- | --- | --- | --- |
| `20-InterCJK-SemiBold.fnt` | 20 | 17 px | 22 / 17 | 34,044 | 6.9 MB |
| `15-InterCJK-Bold.fnt` | 15 | 13 px | 17 / 13 | 34,044 | 4.2 MB |
| `13-InterCJK-SemiBold.fnt` | 13 | 11 px | 14 / 11 | 34,044 | 3.0 MB |

Coverage: CJK Unified Ideographs (all 20,992), Hiragana, Katakana, Bopomofo,
Hangul syllables (all 11,172) and compatibility jamo, CJK punctuation,
radicals, enclosed/compatibility characters, compatibility ideographs and the
halfwidth/fullwidth forms block. CJK Extension A is off by default (rare in
tags, adds ~6.5k glyphs per font); enable with `EXT_A=1`.

The CJK em size is 0.85× the nominal Inter size so that ideographs fit inside
the existing ascent/descent (Rockbox cannot grow a font's line height without
re-rendering the Latin glyphs) and sit at about 1.25× the Latin cap height,
which is the usual mixed-script balance.

Large files are fine. Rockbox only loads a font fully into RAM when it is below
`MAX_FONT_SIZE` (60 KB on this target); anything bigger is read on demand
through a glyph cache, which is how Rockbox's own 16-GNU-Unifont works too.

## Rockbox settings that matter

- **Default Codepage** (Settings → General Settings → Display). ID3v2 and
  Vorbis/FLAC tags are Unicode and need nothing. ID3v1 tags and some old ID3v2
  tags carry no encoding, and Rockbox decodes those with this setting. Pick
  the one your tagger used: `gb2312` (Simplified Chinese), `big5`
  (Traditional Chinese), `sjis` (Japanese), `ksx1001` (Korean). In a `.cfg`
  the key is `default codepage:` and the accepted values are
  `iso8859-1, iso8859-7, iso8859-8, cp1251, iso8859-11, cp1256, iso8859-9,
  iso8859-2, cp1250, cp1252, sjis, gb2312, ksx1001, big5, utf-8`. The theme
  config leaves this alone (commented example inside) because it depends on
  your library, not on the theme.
- **Glyphs To Cache** (Settings → General Settings → System → Limits, cfg
  key `glyphs`). Number of unique glyphs kept in RAM per font, default 250.
  A screen of CJK tags uses far fewer than that, so the default is fine. A
  theme can override it per font with the optional third argument of
  `%Fl(id, file, glyphs)`.
- **Font filenames** must be at most 24 characters for Rockbox to load them
  at startup (manual 13.1.5). `20-InterCJK-SemiBold.fnt` is exactly 24.
- **Language** (Settings → General Settings → Language). With the CJK fonts in
  place you can also switch the Rockbox UI itself to Chinese, Japanese or
  Korean; the menu title in the `.sbs` uses the same fonts.

## Rebuilding the fonts

```
pip install freetype-py           # pillow too if you want previews
tools/build_fonts.sh              # Simplified Chinese forms (default)
CJK_LANG=jp tools/build_fonts.sh  # Japanese forms; also tc, kr
EXT_A=1 tools/build_fonts.sh      # include CJK Extension A
```

`tools/build_fonts.sh` downloads Noto Sans CJK (Medium for the SemiBold
fonts, Bold for the Bold font) into `build/srcfonts/` and runs
`tools/build_cjk_fonts.py` against the untouched upstream fonts in
`tools/base/`. To use a different CJK font, call the Python script directly:

```
python3 tools/build_cjk_fonts.py --in tools/base/20-Inter-SemiBold.fnt \
    --cjk /path/to/AnyCJK.ttf --px 17 --out rockbox/fonts/20-InterCJK-SemiBold.fnt
```

The script warns if glyphs were clipped vertically; lower `--px` if that
happens for characters you care about (the six clipped in the shipped build
are Chinese tone marks and vertical kana repeat marks).

Preview without a device:

```
python3 tools/preview_fnt.py --out preview.png --scale 3 \
    rockbox/fonts/20-InterCJK-SemiBold.fnt "周杰伦 晴天 Jay Chou"
```

## File format reference (RB12)

```
"RB12"
u16 maxwidth, u16 height, u16 ascent, u16 depth (1 = 4-bit antialiased)
u32 firstchar, u32 defaultchar, u32 size, u32 nbits, u32 noffset, u32 nwidth
glyph data     height rows × width pixels, 4 bits/pixel, two pixels per byte,
               low nibble first, 15 = blank, 0 = full ink
pad to 4 bytes u32 offset[size]      (u16 and pad to 2 when nbits < 0xFFDB)
u8 width[size]
```

Codepoints without a glyph point at the default glyph's offset and width.
Rockbox stores codepoints as 16-bit values, so only the Basic Multilingual
Plane is reachable.
