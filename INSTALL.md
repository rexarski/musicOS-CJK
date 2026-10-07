# Installing musicOS

musicOS is a theme for [Rockbox](https://www.rockbox.org), so Rockbox needs to
be installed on the iPod first.

## Compatibility

- **iPod Video 5th / 5.5th generation (320×240):** the model musicOS is
  designed and tested on.
- **iPod Classic 6th / 7th generation:** experimental. Alpha 1 was tested on a
  6th generation Classic; later versions have not been.
- **Rockbox:** 4.0 or a newer development build is recommended.

## Install

1. Download the latest `musicOS-<version>.zip` from the
   [releases page](https://github.com/federicoplg/musicOS/releases) and extract
   it.
2. Connect the iPod to your computer. In Rockbox, plugging in the USB cable
   puts the iPod into disk mode.
3. Open the iPod drive and find the `.rockbox` folder at its top level. Names
   starting with a dot are hidden by default:
   - macOS Finder: press <kbd>Command</kbd> + <kbd>Shift</kbd> + <kbd>.</kbd>
   - Windows File Explorer: **View → Show → Hidden items**
   - Linux file managers: usually <kbd>Ctrl</kbd> + <kbd>H</kbd>
4. Copy the **contents** of the extracted `rockbox` folder (the `fonts`,
   `themes` and `wps` folders) into the iPod's `.rockbox` folder, and choose
   to merge folders when asked.

   > Do not replace or delete the iPod's `.rockbox` folder: Rockbox itself
   > lives there.
5. Eject the iPod safely.
6. On the iPod, open **Settings → Theme Settings → Browse Theme Files** and
   choose a theme:

   | Theme file        | Look      |
   | ----------------- | --------- |
   | `musicOS_v2`      | Light     |
   | `musicOS_v2_dark` | Dark Mode |

You can switch between the two at any time the same way.

## Updating

Install the new version over the old one with the same steps; files with the
same name are replaced. Then select the theme again in **Browse Theme Files**
so Rockbox reloads it.

## Uninstalling

Select another theme in **Browse Theme Files**. To remove the musicOS files as
well, delete these from the iPod's `.rockbox` folder:

- `themes/musicOS_v2.cfg` and `themes/musicOS_v2_dark.cfg`
- `wps/musicOS_v2.wps`, `wps/musicOS_v2.sbs` and the `wps/musicOS_v2` folder
- `wps/musicOS_v2_dark.wps`, `wps/musicOS_v2_dark.sbs` and the
  `wps/musicOS_v2_dark` folder
- `fonts/*-SunghyunSansDisambiguated-SemiBold.fnt` and
  `fonts/UI_Vectors.fnticons`, unless another theme uses them

## Troubleshooting

- **Missing images or a half-drawn screen:** the `wps` folder was not copied
  completely. Copy the `rockbox` folder's contents again and merge.
- **Blank spaces instead of text:** check that the four
  `SunghyunSansDisambiguated` fonts are in `.rockbox/fonts`. If only some
  Chinese characters are blank, the fonts do not include them yet: Korean and
  Japanese are fully covered, Chinese only partly. Please
  [report](https://github.com/federicoplg/musicOS/issues) characters that do
  not display, together with the exact text.
- **No album art:** Rockbox only reads artwork embedded in MP3 (ID3v2) and
  MP4/M4A files, and cannot decode progressive JPEGs. For FLAC and other
  formats, put a baseline JPEG named `cover.jpg` in the album's folder. The
  Album Art appendix of the [Rockbox manual](https://www.rockbox.org/manual.shtml)
  lists every name and location Rockbox looks for.
- **The previous theme still shows:** select `musicOS_v2` or
  `musicOS_v2_dark` again in **Browse Theme Files**.

## Older versions

Every release, including the Alpha 1 "Classic Quick Screen" variant, stays
available on the [releases page](https://github.com/federicoplg/musicOS/releases).
