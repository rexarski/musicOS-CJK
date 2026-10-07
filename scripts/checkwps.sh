#!/bin/sh
# Validate the musicOS skins and theme configs with Rockbox's own parser.
#
# Usage: scripts/checkwps.sh [ROCKBOX_REF]
#
# Fetches Rockbox at ROCKBOX_REF (a tag, branch or commit; default
# v4.0-final) into .cache/, builds the checkwps tool for the iPod Video and
# runs it on every .wps, .sbs and .cfg file in rockbox/.
#
# Needs git, a C compiler, make and the SDL2 development files, which the
# Rockbox configure script looks for (Debian/Ubuntu: apt install libsdl2-dev,
# macOS: brew install sdl2).
set -eu

ref=${1:-v4.0-final}
target=ipodvideo
root=$(cd "$(dirname "$0")/.." && pwd)
cache=$root/.cache/rockbox-$ref
checkwps=$cache/build/checkwps.$target

if [ ! -x "$checkwps" ]; then
    echo "Building checkwps.$target from Rockbox $ref..."
    rm -rf "$cache"
    mkdir -p "$cache/src" "$cache/build"
    git -C "$cache/src" init -q
    git -C "$cache/src" fetch -q --depth 1 https://github.com/Rockbox/rockbox "$ref"
    git -C "$cache/src" checkout -q FETCH_HEAD
    cd "$cache/build"
    if ! ../src/tools/configure --target=$target --type=C --ram=32 > build.log 2>&1 ||
       ! make -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" >> build.log 2>&1; then
        tail -n 25 build.log >&2
        echo "Building checkwps failed; full log: $cache/build/build.log" >&2
        exit 1
    fi
fi

# checkwps resolves the /.rockbox/ paths in .cfg files against the working
# directory, so run it next to a .rockbox link to the theme tree.
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
ln -s "$root/rockbox" "$work/.rockbox"
cd "$work"
set -- .rockbox/wps/*.wps .rockbox/wps/*.sbs
# Rockbox 4.0's checkwps predates .cfg support; newer builds list it in --help.
if "$checkwps" --help | grep -q cfg; then
    set -- "$@" .rockbox/themes/*.cfg
fi
"$checkwps" "$@"
