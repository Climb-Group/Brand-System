#!/bin/bash
# Remove the Climb templates and fonts from Linux. As root it removes them for everyone;
# as a normal user, just for you. CLIMB_TEST_ROOT prefixes target paths (testing).

set -uo pipefail

ROOT="${CLIMB_TEST_ROOT:-}"
BRANDS="ClimbUK ClimbGroup Climb27"

clean_user() {
  local home="$1"
  for b in $BRANDS; do
    rm -rf "$home/.config/libreoffice/4/user/template/$b"
    rm -f "$home/.local/share/DaVinciResolve/Fusion/Templates/${b}_Titles.drfx"
    rm -rf "$home/.local/share/DaVinciResolve/Fusion/Templates/Edit/Titles/$b"
  done
}

if [ -n "$ROOT" ] || [ "$(id -u)" -eq 0 ]; then
  for home in "$ROOT"/home/* "$ROOT/etc/skel"; do
    [ -d "$home" ] && clean_user "$home"
  done
  rm -rf "$ROOT/usr/local/share/fonts/climb" "$ROOT/opt/climb-templates" "$ROOT/opt/resolve/LUT/Climb"
  [ -z "$ROOT" ] && command -v fc-cache >/dev/null && fc-cache -f >/dev/null
else
  clean_user "$HOME"
  rm -rf "$HOME/.local/share/fonts/climb"
  command -v fc-cache >/dev/null && fc-cache -f >/dev/null
fi
echo "Climb templates removed"
exit 0
