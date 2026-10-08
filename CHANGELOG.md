# Changelog

All notable changes to musicOS are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with
an `-alpha` suffix while the theme is in alpha. Each version has a matching
`v`-prefixed git tag (for example `v0.2.1-alpha`).

## [Unreleased]

## [0.2.2-alpha] - 2026-10-08

The theme files are unchanged from 0.2.1-alpha. This release reorganizes the
repository and fixes the release package.

### Added

- README with a project overview, a new musicOS logo and screenshots of every
  screen in both themes, rendered in the Rockbox simulator; plus `INSTALL.md`,
  `CREDITS.md` and `CONTRIBUTING.md`.
- The README documents how much of each Chinese, Japanese and Korean
  character set the fonts cover. Korean and Japanese are complete; Chinese is
  partial (85% of common Traditional and 64% of common Simplified characters).
- `scripts/font_coverage.py`, which measures that coverage for any Rockbox
  font.
- `scripts/check.py`, which checks that every file a theme or skin loads
  exists, that each bitmap is a BMP Rockbox can load, and that sprite sheets
  split evenly into their sub-images.
- `scripts/checkwps.sh`, which runs Rockbox's own skin parser (`checkwps`) on
  the skins and theme configs.
- `scripts/build.py`, which builds the release zip and takes its release
  notes from this changelog.
- GitHub Actions: every push and pull request is checked and gets a test
  package. Pushing a `v*` tag, or running the Release workflow from the
  Actions tab, publishes a GitHub release (a pre-release for `-alpha`
  versions) with the zip attached.
- A bug report form that asks for the iPod model, Rockbox version and musicOS
  version.

### Changed

- One `rockbox/` folder now holds the theme, replacing the per-release folders
  `musicOS_Alpha_1/` and `musicOS_Alpha_v0.2.0/`. Earlier versions remain
  available from their git tags and GitHub releases.
- This changelog replaces the separate `CHANGELOG.txt` and `CHANGELOG.md` files
  from the release folders.

### Fixed

- The release zip includes `FONT-LICENSE.txt` again. The 0.2.1-alpha zip
  shipped the Sunghyun Sans fonts without their license, which the SIL Open
  Font License requires to travel with the fonts.
- The `musicOS_Alpha_v0.2.0` folder held the 0.2.1-alpha Dark Mode files
  while its README and changelog still described 0.2.0.
- The install guide and file list described a hidden `.rockbox` folder and
  left out every Dark Mode file.
- Restored the credit to Christian Soffke's Interpod themes, which was in the
  Alpha 1 README but missing from later releases.

## [0.2.1-alpha] - 2026-09-10

### Added

- musicOS Dark Mode (`musicOS_v2_dark.cfg`). It is designed for the iPod
  display rather than being a background colour swap: the Now Playing screen,
  Home menu and Quick Screen have darker surfaces, redesigned assets and the
  same musicOS pink accent.
- Dark versions of the playback controls and indicators, progress and volume
  bars, album artwork overlays, Lossless indicator and other UI assets.

### Changed

- The light and dark themes ship in the same package.
- The release zip contains a `rockbox` folder whose contents go into the
  iPod's `.rockbox` folder.

Dark Mode was tested on a real iPod Video 5.5G.

## [0.2.0-alpha] - 2026-09-07

### Added

- Experimental Chinese, Japanese and Korean metadata support.
- Album name on the Now Playing screen, below the artist.
- Rounded corners on the Home Screen album artwork.
- Hold (lock) icon on the Home Screen.

### Changed

- Fonts switched from Inter to Sunghyun Sans Disambiguated SemiBold (14, 16,
  20 and 28 px), which covers far more characters while keeping the theme's
  rounded look.
- Menu selection is a rounded bar in the musicOS accent colour.
- The Home mini player drops its Previous and Next buttons, giving the title,
  album and artist more room.
- The Lossless indicator only appears while a lossless file is playing.
- Various UI refinements and fixes.

### Removed

- The Inter fonts.

## [0.1.0-alpha] - 2026-08-29

The first public alpha, released as "musicOS Alpha 1".

### Added

- Custom Home Screen with a dynamic mini player showing album art, title,
  album, artist and playback state.
- Apple Music-inspired Now Playing screen.
- Custom Quick Screen with volume and brightness sliders.
- Shuffle and Repeat controls drawn from sprite sheets.
- Battery percentage and a custom battery icon.
- Lossless indicator for supported formats.
- Pink musicOS menu selection and custom menu title.
- Inter typography.
- A separate "Classic Quick Screen" download for people who prefer the
  original Quick Screen design.

### Fixed

- The Home mini player no longer leaks into the Quick Screen during redraws.
- Switching between the Home and Quick Screen backdrops is stable.

### Known issues

- iPod Classic (6G/7G) support is experimental.
- The mini player album art is square; rounded artwork followed in 0.2.0.
- Some native Rockbox redraws can still show through on the Quick Screen.
- With the Classic Quick Screen download, Home Screen album art is cropped
  from the top-left.

[Unreleased]: https://github.com/rexarski/musicOS-CJK/compare/v0.2.2-alpha...HEAD
[0.2.2-alpha]: https://github.com/rexarski/musicOS-CJK/releases/tag/v0.2.2-alpha
[0.2.1-alpha]: https://github.com/federicoplg/musicOS/releases/tag/v0.2.1-alpha
[0.2.0-alpha]: https://github.com/federicoplg/musicOS/releases/tag/v0.2.0-alpha
[0.1.0-alpha]: https://github.com/federicoplg/musicOS/releases/tag/v0.1.0-alpha
