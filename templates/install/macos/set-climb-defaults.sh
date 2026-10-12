#!/bin/bash
# Make a Climb brand the default in Word, Excel and PowerPoint for each person on this Mac:
#   Word        new blank document opens on the brand letterhead (Normal.dotm)
#   Excel       new blank workbook uses the brand theme and Open Sans (Start-up/Excel/Book.xltx)
#   PowerPoint  new blank presentation uses the brand colours and fonts (Themes/Default Theme.thmx)
#
# Run as root after install-climb-templates.sh:
#   sudo "/Library/Application Support/Climb/Templates/set-climb-defaults.sh" [--brand ClimbGroup] [--user NAME] [--force]
#
# Each person is set once per package version and brand, so a later change they make to their
# own Normal template stays until a new package or brand is rolled out (or --force). Their old
# Normal.dotm is kept as Normal-before-Climb.dotm the first time. A person whose Word is open,
# or who has never opened Office, is skipped and picked up on the next run.
# CLIMB_TEST_ROOT prefixes every path (for testing only).

set -uo pipefail

ROOT="${CLIMB_TEST_ROOT:-}"
BRAND="ClimbGroup"
ONLY_USER=""
FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --brand) BRAND="${2:-}"; shift 2 ;;
    --user) ONLY_USER="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    *) echo "Unknown option $1" >&2; exit 2 ;;
  esac
done
case "$BRAND" in ClimbUK|ClimbGroup|Climb27) ;; *) echo "Brand must be ClimbUK, ClimbGroup or Climb27" >&2; exit 2 ;; esac
if [ -z "$ROOT" ] && [ "$(id -u)" -ne 0 ]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

DEST="$ROOT/Library/Application Support/Climb/Templates"
SRC="$DEST/Defaults/$BRAND"
VERSION="$(head -n1 "$DEST/VERSION" 2>/dev/null || echo unknown)"
STAMP="$VERSION $BRAND"
for f in Normal.dotm Book.xltx "Default Theme.thmx"; do
  [ -f "$SRC/$f" ] || { echo "Missing $SRC/$f: install the Climb templates 1.4.0 or later first" >&2; exit 1; }
done

# pick the folder Office already uses; for a new one, follow its parent's naming
pick() { # pick BASE NAME -> BASE/NAME.localized or BASE/NAME
  if [ -d "$1/$2.localized" ]; then echo "$1/$2.localized"
  elif [ -d "$1/$2" ]; then echo "$1/$2"
  elif [ "$(basename "$1")" = "User Content" ]; then echo "$1/$2"
  else echo "$1/$2.localized"; fi
}

place() { # place SOURCE TARGET OWNER
  mkdir -p "$(dirname "$2")"
  cp "$1" "$2.climb-new" && mv -f "$2.climb-new" "$2"
  chown "$3" "$2"
  chmod 644 "$2"
}

set_user() { # set_user NAME HOME
  local user="$1" home="$2"
  local group="$home/Library/Group Containers/UBF8T346G9.Office"
  local marker="$home/Library/Application Support/Climb/office-defaults"
  if [ ! -d "$group" ]; then
    echo "$user: Office has not been opened yet; skipped"
    return 0
  fi
  if [ "$FORCE" -eq 0 ] && [ -f "$marker" ] && [ "$(head -n1 "$marker")" = "$STAMP" ]; then
    echo "$user: already set ($STAMP)"
    return 0
  fi
  if [ -z "$ROOT" ] && pgrep -u "$user" -x "Microsoft Word" >/dev/null 2>&1; then
    echo "$user: Word is open; skipped until the next run"
    return 0
  fi
  local owner content templates startup themes
  if [ "$(uname)" = Darwin ]; then owner="$(stat -f '%Su:%Sg' "$home")"; else owner="$(stat -c '%U:%G' "$home")"; fi
  content="$(pick "$group" "User Content")"
  templates="$(pick "$content" Templates)"
  startup="$(pick "$content" Startup)/Excel"
  themes="$(pick "$content" Themes)"

  if [ -f "$templates/Normal.dotm" ] && [ ! -f "$templates/Normal-before-Climb.dotm" ]; then
    cp -p "$templates/Normal.dotm" "$templates/Normal-before-Climb.dotm"
  fi
  place "$SRC/Normal.dotm" "$templates/Normal.dotm" "$owner"
  place "$SRC/Book.xltx" "$startup/Book.xltx" "$owner"
  place "$SRC/Default Theme.thmx" "$themes/Default Theme.thmx" "$owner"
  mkdir -p "$(dirname "$marker")"
  echo "$STAMP" > "$marker"
  chown "$owner" "$marker" "$(dirname "$marker")"
  echo "$user: $BRAND set as the Word, Excel and PowerPoint default"
}

for home in "$ROOT"/Users/*; do
  [ -d "$home/Library" ] || continue
  user="$(basename "$home")"
  case "$user" in Shared|Guest|.localized) continue ;; esac
  [ -n "$ONLY_USER" ] && [ "$user" != "$ONLY_USER" ] && continue
  set_user "$user" "$home"
done
exit 0
