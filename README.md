# musicOS-CJK

An Apple Music-inspired Rockbox theme for the iPod Video 5th / 5.5th generation
(320×240), with Chinese, Japanese and Korean text support.

This is a fork of [federicoplg/musicOS](https://github.com/federicoplg/musicOS) (Alpha 1). The only change
from upstream is the fonts: the three Inter fonts now also contain the CJK
glyphs from Noto Sans CJK, so tags, file names and menus written in Chinese,
Japanese or Korean render instead of showing up blank. See
[CJK-SUPPORT.md](CJK-SUPPORT.md) for how that works and how to rebuild the
fonts.

## Status

Alpha. Core Home, Now Playing and Quick Screen functionality is working, but
bugs may still exist.

## Compatibility

Primary target: iPod Video 5G / 5.5G (320×240). 6G / 7G compatibility should
be considered experimental until validated on hardware.

## Installation

1. Make sure Rockbox is already installed on your iPod.
2. Back up anything important before installing an alpha theme.
3. Copy the contents of the `rockbox/` folder in this repository into the
   `.rockbox` folder on the root of the iPod, merging with what is there
   (`fonts/`, `themes/`, `wps/`).
4. In Rockbox, open Settings → Theme Settings → Browse Theme Files.
5. Select `musicOS_v2.cfg`.

Do not replace or delete your entire existing `.rockbox` folder to install
this theme.

If your tags come from ID3v1 or otherwise non-Unicode files, also set
Settings → General Settings → Display → Default Codepage to the encoding your
tagger used (GB 2312, Big5, Shift-JIS or KS X 1001). See CJK-SUPPORT.md.

## Repository layout

| Path | What it is |
| --- | --- |
| `rockbox/` | Files to merge into `/.rockbox` on the player |
| `rockbox/fonts/` | Inter + Noto Sans CJK fonts (`*-InterCJK-*.fnt`) |
| `rockbox/themes/musicOS_v2.cfg` | Theme config |
| `rockbox/wps/` | Now Playing (`.wps`), base skin (`.sbs`) and bitmaps |
| `tools/` | Font build scripts and the original Latin-only Inter fonts |
| `CJK-SUPPORT.md` | Notes on Rockbox fonts, codepages and the font build |
| `CHANGELOG.txt` | Release notes |

## Highlights

- Custom musicOS Home screen.
- Dynamic mini-player with album art, title, album/artist and playback state.
- Apple Music-inspired Now Playing screen.
- Custom Quick Screen with volume and brightness sliders.
- Shuffle and Repeat controls with sprite-based states.
- Battery percentage and custom battery icon.
- Lossless indicator on supported formats.
- Pink musicOS menu selection and custom menu title.
- Inter-based typography, now with CJK coverage.

## Known limitations

- Alpha: not exhaustively tested across every Rockbox screen or state.
- 6G / 7G support is experimental.
- Mini-player album artwork is square; rounded dynamic artwork is deferred.
- Some Rockbox-native redraw behaviour may still be visible in the Quick
  Screen.
- The bundled fonts use Simplified Chinese glyph forms for characters shared
  between Chinese and Japanese. Rebuild with `CJK_LANG=jp` (or `tc`, `kr`) if
  you prefer the other conventions.
- Only the Unicode Basic Multilingual Plane can be shown; Rockbox stores
  codepoints in 16 bits, so CJK Extension B and later are not possible.

## Credits

- Built for Rockbox and the iPod Video platform.
- musicOS theme by federicoplg (upstream Alpha 1).
- Inter typeface by Rasmus Andersson (SIL Open Font License 1.1).
- Noto Sans CJK by Google / Adobe (SIL Open Font License 1.1).
- musicOS was developed with reference to / adaptation of ideas from the
  Interpod family of Rockbox themes by Christian Soffke. Preserve upstream
  attribution when redistributing derivative material.

Before submitting to an official theme catalogue, verify and preserve the
exact upstream licensing and attribution requirements for any adapted Interpod
assets or code.
