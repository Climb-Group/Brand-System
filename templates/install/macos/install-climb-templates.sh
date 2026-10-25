#!/bin/bash
# Install the ClimbUK, ClimbGroup and Climb27 templates, fonts and themes on macOS.
#
# Run as root: a Jamf policy script, the postinstall of the .pkg from build-pkg.sh,
# or `sudo ./install-climb-templates.sh` from the unzipped package.
#
#   Fonts      -> /Library/Fonts
#   Office     -> /Library/Application Support/Microsoft/Office365/User Content.localized/
#                 Templates.localized and Themes.localized (all users, Office 16.x)
#   ONLYOFFICE -> templates added to the Desktop Editors Templates list, plus a LaunchDaemon
#                 that adds them back after an ONLYOFFICE update
#   Everything -> /Library/Application Support/Climb/Templates (incl. LibreOffice and video kit)
#   Video      -> DaVinci Resolve titles and LUT, Premiere Pro LUT (skip with --skip-video,
#                 or put skip-video in Jamf parameter 4)
#   Skip fonts -> --skip-fonts (or skip-fonts in any Jamf parameter) leaves out the fonts, for a
#                 device manager that installs them with a script of their own
#
# Re-running is safe. CLIMB_TEST_ROOT prefixes every target path (for testing only).

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$HERE/.." && pwd)"
PAYLOAD="$PKG/payload"
ROOT="${CLIMB_TEST_ROOT:-}"
VERSION="$(head -n1 "$PKG/VERSION" 2>/dev/null || echo "@VERSION@")"

SKIP_VIDEO=0
SKIP_FONTS=0
for arg in "$@"; do
  case "$arg" in
    --skip-video|skip-video) SKIP_VIDEO=1 ;;
    --skip-fonts|skip-fonts) SKIP_FONTS=1 ;;
  esac
done

if [ ! -d "$PAYLOAD" ]; then
  echo "Payload not found at $PAYLOAD" >&2
  exit 1
fi
if [ -z "$ROOT" ] && [ "$(id -u)" -ne 0 ]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

DEST="$ROOT/Library/Application Support/Climb/Templates"
MSO="$ROOT/Library/Application Support/Microsoft/Office365/User Content.localized"
FONTS="$ROOT/Library/Fonts"

copy_tree() { # copy_tree FROM TO
  [ -d "$1" ] || return 0
  mkdir -p "$2"
  cp -R "$1/." "$2/"
}

echo "Installing Climb templates $VERSION"

# Fonts, and their reference copy (the uninstaller removes the fonts listed there)
if [ "$SKIP_FONTS" -eq 0 ]; then
  mkdir -p "$FONTS"
  cp "$PAYLOAD"/fonts/*.ttf "$FONTS/"
  chmod 644 "$FONTS"/Montserrat-*.ttf "$FONTS"/OpenSans-*.ttf
  copy_tree "$PAYLOAD/fonts" "$DEST/Fonts"
else
  # drop a reference copy left by an earlier full install, so uninstalling keeps the fonts
  rm -rf "$DEST/Fonts"
  echo "Fonts: skipped (--skip-fonts)"
fi

# Full copy for reference, LibreOffice and video import
copy_tree "$PAYLOAD/office" "$DEST/Office"
copy_tree "$PAYLOAD/themes" "$DEST/Themes"
copy_tree "$PAYLOAD/libreoffice" "$DEST/LibreOffice"
copy_tree "$PAYLOAD/defaults" "$DEST/Defaults"
cp "$HERE/set-climb-defaults.sh" "$DEST/"
chmod 755 "$DEST/set-climb-defaults.sh"

# Office for Mac: shared templates and themes for every user
mkdir -p "$MSO/Templates.localized" "$MSO/Themes.localized/Theme Colors" "$MSO/Themes.localized/Theme Fonts"
for brand in "$PAYLOAD"/office/*/; do
  cp "$brand"* "$MSO/Templates.localized/"
done
cp "$PAYLOAD"/themes/*.thmx "$MSO/Themes.localized/"
cp "$PAYLOAD/themes/Theme Colors/"*.xml "$MSO/Themes.localized/Theme Colors/"
cp "$PAYLOAD/themes/Theme Fonts/"*.xml "$MSO/Themes.localized/Theme Fonts/"

# ONLYOFFICE Desktop Editors: add now, and again whenever the app is replaced by an update
cp "$HERE/climb-onlyoffice.sh" "$DEST/"
chmod 755 "$DEST/climb-onlyoffice.sh"
"$DEST/climb-onlyoffice.sh" add "$DEST/Office" || echo "ONLYOFFICE step skipped" >&2
DAEMON="$ROOT/Library/LaunchDaemons/com.climb-uk.templates.onlyoffice.plist"
mkdir -p "$(dirname "$DAEMON")"
cat > "$DAEMON" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.climb-uk.templates.onlyoffice</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Library/Application Support/Climb/Templates/climb-onlyoffice.sh</string>
    <string>ensure</string>
    <string>/Library/Application Support/Climb/Templates/Office</string>
  </array>
  <key>WatchPaths</key><array><string>/Applications/ONLYOFFICE.app</string></array>
  <key>RunAtLoad</key><true/>
</dict>
</plist>
PLIST
chmod 644 "$DAEMON"
if [ -z "$ROOT" ]; then
  chown root:wheel "$DAEMON"
  launchctl bootout system "$DAEMON" >/dev/null 2>&1 || true
  launchctl bootstrap system "$DAEMON" || echo "Could not load the ONLYOFFICE LaunchDaemon" >&2
fi

# Video
if [ "$SKIP_VIDEO" -eq 0 ] && [ -d "$PAYLOAD/video" ]; then
  copy_tree "$PAYLOAD/video" "$DEST/Video"
  RESOLVE="$ROOT/Library/Application Support/Blackmagic Design/DaVinci Resolve"
  mkdir -p "$RESOLVE/Fusion/Templates" "$RESOLVE/LUT/Climb" "$ROOT/Library/Application Support/Adobe/Common/LUTs/Creative"
  cp "$PAYLOAD"/video/resolve/*.drfx "$RESOLVE/Fusion/Templates/"
  # the logo titles load their PNGs from Templates:/Edit/Titles/<Brand>/ (Resolve cannot read images inside a .drfx)
  for d in "$PAYLOAD"/video/resolve/*/; do
    b="$(basename "$d")"
    mkdir -p "$RESOLVE/Fusion/Templates/Edit/Titles/$b"
    cp "$d"*.png "$RESOLVE/Fusion/Templates/Edit/Titles/$b/"
  done
  cp "$PAYLOAD"/video/luts/*.cube "$RESOLVE/LUT/Climb/"
  cp "$PAYLOAD"/video/luts/*.cube "$ROOT/Library/Application Support/Adobe/Common/LUTs/Creative/"
  echo "Video: Resolve titles, Resolve LUT and Premiere LUT installed"
fi

cp "$HERE/uninstall-climb-templates.sh" "$DEST/" 2>/dev/null || true
echo "$VERSION" > "$DEST/VERSION"
if [ -z "$ROOT" ]; then
  chmod -R a+rX "$DEST" "$MSO"
fi

echo "Done. Quit and reopen Office to see the templates under File, New from Template."
echo "In ONLYOFFICE: Templates on the start screen."
exit 0
