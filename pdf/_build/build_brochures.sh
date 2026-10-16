#!/usr/bin/env bash
# Rebuilds the Climb27 exhibitor and partner brochures and the Who was there pack (pdf/brochures/).
# Needs Python 3 with Pillow, numpy and segno, and Node with Playwright (Chromium). Run from anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PACK="$(cd "$HERE/../.." && pwd)"
cd "$HERE"
rm -rf assets && mkdir -p assets/fonts assets/logos assets/photos assets/illus assets/brochure assets/wwt
cp "$PACK"/fonts/*.woff2 "$PACK"/generators/fonts/*.woff2 fonts/*.woff2 assets/fonts/
for b in ClimbUK Climb27; do mkdir -p "assets/logos/$b"; cp "$PACK/logos/$b"/*.svg "assets/logos/$b/"; done
cp "$PACK"/photos/*.jpg "$PACK"/photos/candid/*.jpg assets/photos/
cp "$PACK"/pdf/brochures/_build/img/*.jpg assets/brochure/
cp "$PACK"/pdf/brochures/_build/logos/* assets/wwt/
# Pages are 1920px wide, so photos are sized to 2200px on the long edge to keep the PDFs small.
python3 -c 'import glob
from PIL import Image
for f in glob.glob("assets/photos/*.jpg"):
    im=Image.open(f); im.thumbnail((2200,2200)); im.convert("RGB").save(f,quality=84,optimize=True,progressive=True)'
cp "$PACK"/illustrations/*.svg assets/illus/
python3 brochures.py
python3 who_was_there.py
# Every printed word through the climb-voice checker.
python3 "$PACK/.agents/skills/climb-voice/scripts/check_copy.py" brochures_printed.txt
# WCAG 2.2 AA: measure every run of text against what is behind it before printing.
CHK=$(mktemp -d)
node contrast.cjs "$CHK" ./climb27_*.html
python3 contrast.py "$CHK"
# Every price in a row of cards on one line, inside its card.
node align.cjs ./climb27_*.html
rm -rf "$CHK"
node render.cjs ./climb27_*.html
mkdir -p ../brochures
for f in climb27_*.pdf; do mv "$f" ../brochures/; done
[ -n "${KEEP_HTML:-}" ] || rm -f ./climb27_*.html brochures_printed.txt
[ -n "${KEEP_HTML:-}" ] || rm -rf assets __pycache__
echo "PDFs written to pdf/brochures"
