#!/usr/bin/env bash
# Rebuilds the one-page key rules and the guidelines book for each brand.
# Needs Python 3 and Node with Playwright (Chromium). Run from anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PACK="$(cd "$HERE/../.." && pwd)"
cd "$HERE"
rm -rf assets && mkdir -p assets/fonts assets/logos assets/photos assets/illus assets/social
cp "$PACK"/fonts/*.woff2 "$PACK"/generators/fonts/*.woff2 fonts/*.woff2 assets/fonts/
for b in ClimbUK ClimbGroup Climb27; do mkdir -p "assets/logos/$b"; cp "$PACK/logos/$b"/*.svg "assets/logos/$b/"; done
cp "$PACK"/photos/*.jpg assets/photos/
# Pages are 1920px wide, so photos are sized to 2560px on the long edge to keep the PDFs small.
python3 -c 'import glob,sys
from PIL import Image
for f in glob.glob("assets/photos/*.jpg"):
    im=Image.open(f); im.thumbnail((2560,2560)); im.convert("RGB").save(f,quality=84,optimize=True,progressive=True)'
cp "$PACK"/illustrations/*.svg assets/illus/
cp "$PACK"/generators/social-icons/glyphs/*.svg assets/social/
cp "$PACK"/generators/motifs.py .
python3 book.py
python3 keyrules.py
node render.cjs ./*.html
mkdir -p ../one-page ../guidelines
for f in *_key-rules.pdf; do mv "$f" ../one-page/; done
for f in *_brand-guidelines.pdf; do mv "$f" ../guidelines/; done
rm -f ./*.html motifs.py
rm -rf assets __pycache__
echo "PDFs written to pdf/one-page and pdf/guidelines"
