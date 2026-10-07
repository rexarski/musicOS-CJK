#!/usr/bin/env python3
"""Build the musicOS release package.

Runs scripts/check.py, then writes:
  dist/musicOS-<version>.zip   the rockbox/ theme folder plus the user docs
  dist/RELEASE_NOTES.md        the CHANGELOG.md section for <version>, if any

Usage: python3 scripts/build.py [--version VERSION] [--release]

VERSION defaults to `git describe --tags --always --dirty`. With --release
the build fails unless CHANGELOG.md has a section for VERSION; the release
workflow uses this so every published release has notes.
"""

import argparse
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

ROOT = check.ROOT
DIST = ROOT / "dist"
DOCS = ("INSTALL.md", "CHANGELOG.md", "CREDITS.md", "FONT-LICENSE.txt")
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}

INSTALL_NOTES = """
## Install

1. Download `{zip_name}` below and extract it.
2. Copy the contents of its `rockbox` folder (`fonts`, `themes`, `wps`) into the
   `.rockbox` folder on your iPod and merge them. Do not replace or delete your
   existing `.rockbox` folder.
3. On the iPod, open **Settings → Theme Settings → Browse Theme Files** and pick
   `musicOS_v2` (light) or `musicOS_v2_dark` (Dark Mode).

Full instructions are in `INSTALL.md` inside the zip.
"""


def git(*args):
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def source_date():
    """Timestamp for zip entries, so identical sources give identical zips."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH") or git("log", "-1", "--format=%ct")
    return time.gmtime(int(epoch) if epoch else time.time())[:6]


def changelog_section(version):
    """Return the body of the '## [version]' section of CHANGELOG.md, or None."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    if not match:
        return None
    # Drop the link reference definitions that close the file.
    body = re.sub(r"^\[[^\]]+\]: \S+\n?", "", match.group(1), flags=re.M)
    return body.strip()


def package_files():
    """Yield (path on disk, path inside the package) pairs."""
    for path in sorted((ROOT / "rockbox").rglob("*")):
        if path.is_file() and path.name not in JUNK and not path.name.startswith("._"):
            yield path, path.relative_to(ROOT).as_posix()
    for name in DOCS:
        yield ROOT / name, name


def write_zip(zip_path, prefix, date):
    entries = list(package_files())
    folders = {prefix + "/"}
    for _, arcname in entries:
        parts = arcname.split("/")[:-1]
        folders.update(prefix + "/" + "/".join(parts[: i + 1]) + "/" for i in range(len(parts)))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for folder in sorted(folders):
            info = zipfile.ZipInfo(folder, date)
            info.external_attr = (0o40755 << 16) | 0x10
            archive.writestr(info, b"")
        for path, arcname in entries:
            info = zipfile.ZipInfo(f"{prefix}/{arcname}", date)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return len(entries)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", help="version to build, e.g. v0.2.1-alpha")
    parser.add_argument(
        "--release", action="store_true", help="require a CHANGELOG.md section for the version"
    )
    args = parser.parse_args(argv)

    if check.main([]) != 0:
        print("build: fix the errors above first", file=sys.stderr)
        return 1

    version = args.version or git("describe", "--tags", "--always", "--dirty") or "dev"
    notes = changelog_section(version.removeprefix("v"))
    if args.release and notes is None:
        print(f"build: CHANGELOG.md has no '## [{version.removeprefix('v')}]' section", file=sys.stderr)
        return 1

    DIST.mkdir(exist_ok=True)
    name = f"musicOS-{version}"
    zip_path = DIST / f"{name}.zip"
    count = write_zip(zip_path, name, source_date())
    print(f"built {zip_path.relative_to(ROOT)} ({count} files, {zip_path.stat().st_size:,} bytes)")

    notes_path = DIST / "RELEASE_NOTES.md"
    if notes is None:
        notes_path.unlink(missing_ok=True)
        print(f"no CHANGELOG.md section for {version}; skipped release notes")
    else:
        notes_path.write_text(
            notes + "\n" + INSTALL_NOTES.format(zip_name=zip_path.name), encoding="utf-8"
        )
        print(f"wrote {notes_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
