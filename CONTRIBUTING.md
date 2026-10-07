# Contributing to musicOS

Bug reports and pull requests are welcome. musicOS is alpha software, so a
screenshot or photo of a problem helps a lot.

## Reporting a bug

Open an issue with the **Bug report** form. It asks for the iPod model,
Rockbox version (System → Rockbox Info on the iPod), musicOS version and theme
variant. For text that renders wrongly, paste the exact title, artist or album.

## How the theme fits together

| Path                                 | What it is                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------- |
| `rockbox/themes/musicOS_v2.cfg`      | The light theme. Selecting it loads the skins and font and sets colours.  |
| `rockbox/wps/musicOS_v2.wps`         | The Now Playing screen (WPS).                                              |
| `rockbox/wps/musicOS_v2.sbs`         | The status bar skin, which draws the Home Screen and the custom Quick Screen. |
| `rockbox/wps/musicOS_v2/`            | Bitmaps for both skins. A skin loads images from the folder named after it. |
| `rockbox/fonts/`                     | Rockbox bitmap fonts, loaded with `%Fl` in the skins.                      |
| `…_dark.cfg`, `…_dark.wps`, `…_dark/` | The Dark Mode copies of the above.                                        |

The light and dark skins load the same bitmap names and differ only in
colours and artwork, so change both together. `scripts/check.py` warns when
they drift apart.

The skin language is documented in the
[Rockbox manual](https://www.rockbox.org/manual.shtml) (appendix "Theme Tags")
and on the [CustomWPS wiki page](https://www.rockbox.org/wiki/CustomWPS).
Bitmaps must be BMP files: 24-bit, or 32-bit when they need transparency.

## Making a change

1. Edit the files in `rockbox/`.
2. Try the change on an iPod, or in the Rockbox simulator for the iPod Video,
   by copying the contents of `rockbox/` into its `.rockbox` folder.
3. Run the checks:

   ```sh
   python3 scripts/check.py   # missing or broken files, sprite sheet sizes
   scripts/checkwps.sh        # Rockbox's own skin parser
   ```

   `checkwps.sh` builds Rockbox's `checkwps` tool on first use, which needs
   git, a C compiler, make and the SDL2 development files
   (`apt install libsdl2-dev` or `brew install sdl2`).
4. Add a line to the `[Unreleased]` section of `CHANGELOG.md`.
5. Open a pull request. CI runs the same checks and attaches a test package
   to the run, ready to copy onto an iPod.

If you change the fonts, `python3 scripts/font_coverage.py` shows how much of
each Chinese, Japanese and Korean character set they cover.

## Versioning

musicOS uses [Semantic Versioning](https://semver.org) with a pre-release
suffix while the theme is in alpha:

- **patch** (0.2.1 → 0.2.2) for fixes and packaging changes;
- **minor** (0.2 → 0.3) for new screens, features or visible redesigns;
- the `-alpha` suffix stays until the theme leaves alpha. If one version
  needs several alphas, number them: `0.3.0-alpha.1`, `0.3.0-alpha.2`.

Git tags carry a `v` prefix: `v0.2.1-alpha`.

## Releasing

1. In `CHANGELOG.md`, rename `[Unreleased]` to the new version and date, for
   example `## [0.2.2-alpha] - 2026-10-07`, start a new empty `[Unreleased]`
   section above it, and update the comparison links at the bottom.
2. Commit that change on `main`, then tag and push:

   ```sh
   git tag v0.2.2-alpha
   git push origin v0.2.2-alpha
   ```

3. The **Release** workflow builds `musicOS-v0.2.2-alpha.zip` and publishes a
   GitHub release with that version's changelog section as its notes. A tag
   with a suffix such as `-alpha`, `-beta` or `-rc.1` becomes a pre-release.

To build the package locally, run `python3 scripts/build.py`; the zip is
written to `dist/`.
