#!/bin/bash
# Add the Climb templates to the ONLYOFFICE Desktop Editors Templates list, or remove them.
#
#   climb-onlyoffice.sh [add] [SOURCE]   SOURCE is the folder holding <Brand>/*.dotx .xltx .potx;
#                                        by default the installed copy, or payload/office
#                                        when run from the unzipped package
#   climb-onlyoffice.sh ensure SOURCE   add only where they are missing (after an update)
#   climb-onlyoffice.sh remove
#
# ONLYOFFICE lists every file under converter/templates/<language>/ inside the app, so the
# templates go in a Climb/<Brand> folder inside each language folder. Run as root.
# An ONLYOFFICE update replaces the app and drops them; the LaunchDaemon that
# install-climb-templates.sh sets up runs this again whenever the app changes.
# On macOS 13 and later, changing another app needs App Management permission:
# grant it to the Jamf agent (or your MDM's agent) with a PPPC profile if the copy fails.
# CLIMB_TEST_ROOT prefixes the ONLYOFFICE path (testing only).

set -uo pipefail

ROOT="${CLIMB_TEST_ROOT:-}"
ACTION="${1:-add}"
SRC="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "$ACTION" != remove ] && [ -z "$SRC" ]; then
  for c in "$ROOT/Library/Application Support/Climb/Templates/Office" "$HERE/Office" "$HERE/../payload/office"; do
    if [ -d "$c/ClimbUK" ]; then SRC="$c"; break; fi
  done
fi
case "$ACTION" in add|ensure|remove) ;; *) echo "Usage: $0 [add|ensure|remove] [SOURCE]" >&2; exit 2 ;; esac
if [ "$ACTION" != remove ] && ! ls "$SRC"/*/*.dotx >/dev/null 2>&1; then
  echo "No templates found in '${SRC:-(none)}'. Give the folder that holds ClimbUK, ClimbGroup and Climb27." >&2
  exit 2
fi
FOUND=0
STATUS=0

APPS=("$ROOT/Applications/ONLYOFFICE.app/Contents/Resources")
for app in "${APPS[@]}"; do
  tpl="$app/converter/templates"
  [ -d "$app/converter" ] || continue
  FOUND=1
  mkdir -p "$tpl" 2>/dev/null || { echo "ONLYOFFICE: cannot write to $tpl" >&2; continue; }
  # one target per language folder, or the templates folder itself when it has none
  targets=()
  for d in "$tpl"/*/; do
    [ -d "$d" ] && [ "$(basename "$d")" != Climb ] && targets+=("${d%/}")
  done
  [ ${#targets[@]} -eq 0 ] && targets=("$tpl")
  for t in "${targets[@]}"; do
    [ "$ACTION" = ensure ] && [ -d "$t/Climb" ] && continue
    rm -rf "${t:?}/Climb"
    [ "$ACTION" = remove ] && continue
    for b in "$SRC"/*/; do
      if ! { mkdir -p "$t/Climb/$(basename "$b")" &&
        cp "$b"*.dotx "$b"*.xltx "$b"*.potx "$t/Climb/$(basename "$b")/"; }; then
        echo "ONLYOFFICE: could not copy into $t" >&2
        STATUS=1
      fi
    done
    chmod -R a+rX "$t/Climb" 2>/dev/null
  done
  if [ "$ACTION" = remove ]; then echo "ONLYOFFICE: templates removed from $tpl"; else echo "ONLYOFFICE: templates in $tpl"; fi
done

[ "$FOUND" -eq 0 ] && echo "ONLYOFFICE Desktop Editors not found; skipped"
exit "$STATUS"
