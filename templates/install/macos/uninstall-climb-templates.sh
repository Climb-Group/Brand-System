#!/bin/bash
# Remove the Climb templates, fonts, themes and video files from macOS. Run as root.
# CLIMB_TEST_ROOT prefixes every target path (for testing only).

set -uo pipefail

ROOT="${CLIMB_TEST_ROOT:-}"
if [ -z "$ROOT" ] && [ "$(id -u)" -ne 0 ]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

DEST="$ROOT/Library/Application Support/Climb/Templates"
MSO="$ROOT/Library/Application Support/Microsoft/Office365/User Content.localized"
RESOLVE="$ROOT/Library/Application Support/Blackmagic Design/DaVinci Resolve"

for f in "$DEST"/Fonts/*.ttf; do
  [ -e "$f" ] && rm -f "$ROOT/Library/Fonts/$(basename "$f")"
done
for b in ClimbUK ClimbGroup Climb27; do
  rm -f "$MSO/Templates.localized/${b}_"* "$MSO/Themes.localized/$b.thmx" "$RESOLVE/Fusion/Templates/${b}_Titles.drfx"
  rm -rf "$RESOLVE/Fusion/Templates/Edit/Titles/$b"
done
rm -f "$MSO/Themes.localized/Theme Colors/Climb.xml" "$MSO/Themes.localized/Theme Fonts/Climb.xml"
rm -rf "$RESOLVE/LUT/Climb"
rm -f "$ROOT/Library/Application Support/Adobe/Common/LUTs/Creative/Climb_Grade_v1.cube"
rm -rf "$ROOT/Library/Application Support/Climb"
if [ -z "$ROOT" ]; then
  pkgutil --forget com.climb-uk.templates >/dev/null 2>&1 || true
fi
echo "Climb templates removed"
exit 0
