#!/bin/bash
# Install the ClimbUK, ClimbGroup and Climb27 templates, fonts and themes on Linux.
#
# As root (all users):
#   Fonts      -> /usr/local/share/fonts/climb (then fc-cache)
#   Everything -> /opt/climb-templates (Office files, themes, LibreOffice, video kit)
#   LibreOffice: a folder per brand linked into each person's template folder
#                (~/.config/libreoffice/4/user/template) for every home in /home,
#                and in /etc/skel for new accounts
#   ONLYOFFICE -> templates added to the Desktop Editors Templates list (deb/rpm install)
#   Resolve    -> titles into each person's ~/.local/share/DaVinciResolve/Fusion/Templates,
#                 LUT into /opt/resolve/LUT/Climb when Resolve is installed
# As a normal user (just you): fonts in ~/.local/share/fonts/climb, templates copied
# into your LibreOffice template folder, Resolve titles into your Fusion templates.
#
# Options: --skip-video. Re-running is safe. CLIMB_TEST_ROOT prefixes target paths (testing).

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$HERE/.." && pwd)"
PAYLOAD="$PKG/payload"
ROOT="${CLIMB_TEST_ROOT:-}"
VERSION="$(head -n1 "$PKG/VERSION" 2>/dev/null || echo "@VERSION@")"
BRANDS="ClimbUK ClimbGroup Climb27"

SKIP_VIDEO=0
for arg in "$@"; do
  case "$arg" in
    --skip-video) SKIP_VIDEO=1 ;;
  esac
done
[ -d "$PAYLOAD" ] || { echo "Payload not found at $PAYLOAD" >&2; exit 1; }

copy_tree() { # copy_tree FROM TO
  [ -d "$1" ] || return 0
  mkdir -p "$2"
  cp -R "$1/." "$2/"
}

# setup_user HOME OWNER MODE: wire LibreOffice and Resolve for one person.
# MODE "link" points at /opt/climb-templates, "copy" copies the files in.
setup_user() {
  local home="$1" owner="$2" mode="$3" src="$4"
  local lo="$home/.config/libreoffice/4/user/template"
  mkdir -p "$lo"
  for b in $BRANDS; do
    rm -rf "${lo:?}/$b"
    if [ "$mode" = link ]; then
      ln -s "$src/LibreOffice/$b" "$lo/$b"
    else
      copy_tree "$PAYLOAD/libreoffice/$b" "$lo/$b"
    fi
  done
  if [ "$SKIP_VIDEO" -eq 0 ]; then
    local fusion="$home/.local/share/DaVinciResolve/Fusion/Templates"
    mkdir -p "$fusion"
    cp "$PAYLOAD"/video/resolve/*.drfx "$fusion/"
    # the logo titles load their PNGs from Templates:/Edit/Titles/<Brand>/
    for d in "$PAYLOAD"/video/resolve/*/; do
      mkdir -p "$fusion/Edit/Titles/$(basename "$d")"
      cp "$d"*.png "$fusion/Edit/Titles/$(basename "$d")/"
    done
  fi
  if [ -n "$owner" ]; then
    chown -R "$owner" "$home/.config/libreoffice" 2>/dev/null || true
    [ "$SKIP_VIDEO" -eq 0 ] && chown -R "$owner" "$home/.local/share/DaVinciResolve" 2>/dev/null || true
  fi
}

echo "Installing Climb templates $VERSION"

if [ -n "$ROOT" ] || [ "$(id -u)" -eq 0 ]; then
  DEST="$ROOT/opt/climb-templates"
  FONTS="$ROOT/usr/local/share/fonts/climb"
  mkdir -p "$FONTS"
  cp "$PAYLOAD"/fonts/*.ttf "$PAYLOAD"/fonts/*.txt "$FONTS/"
  chmod 644 "$FONTS"/*
  copy_tree "$PAYLOAD/office" "$DEST/Office"
  copy_tree "$PAYLOAD/themes" "$DEST/Themes"
  copy_tree "$PAYLOAD/libreoffice" "$DEST/LibreOffice"
  copy_tree "$PAYLOAD/fonts" "$DEST/Fonts"
  if [ "$SKIP_VIDEO" -eq 0 ]; then
    copy_tree "$PAYLOAD/video" "$DEST/Video"
    if [ -d "$ROOT/opt/resolve" ]; then
      mkdir -p "$ROOT/opt/resolve/LUT/Climb"
      cp "$PAYLOAD"/video/luts/*.cube "$ROOT/opt/resolve/LUT/Climb/"
    fi
  fi
  cp "$HERE/uninstall-climb-templates.sh" "$HERE/climb-onlyoffice.sh" "$DEST/"
  "$HERE/climb-onlyoffice.sh" add "$DEST/Office" || echo "ONLYOFFICE step skipped" >&2
  echo "$VERSION" > "$DEST/VERSION"
  chmod -R a+rX "$DEST"
  # Every existing person, and new accounts through /etc/skel
  for home in "$ROOT"/home/*; do
    [ -d "$home" ] || continue
    owner="$(stat -c '%U:%G' "$home")"
    setup_user "$home" "$owner" link "/opt/climb-templates"
    echo "Set up $(basename "$home")"
  done
  mkdir -p "$ROOT/etc/skel"
  setup_user "$ROOT/etc/skel" "" link "/opt/climb-templates"
  [ -z "$ROOT" ] && command -v fc-cache >/dev/null && fc-cache -f "$FONTS" >/dev/null
else
  FONTS="$HOME/.local/share/fonts/climb"
  mkdir -p "$FONTS"
  cp "$PAYLOAD"/fonts/*.ttf "$PAYLOAD"/fonts/*.txt "$FONTS/"
  setup_user "$HOME" "" copy ""
  command -v fc-cache >/dev/null && fc-cache -f "$FONTS" >/dev/null
fi

echo "Done. In LibreOffice: File, New, Templates, then pick a brand folder."
echo "In ONLYOFFICE: Templates on the start screen (as root install only)."
exit 0
