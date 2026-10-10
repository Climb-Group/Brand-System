#!/bin/bash
# Installs the Climb title packs, their logo files and the Climb grade LUT for DaVinci Resolve.
# Double-click it with Resolve closed, then open Resolve.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
R="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve"
mkdir -p "$R/Fusion/Templates" "$R/LUT/Climb"
for b in ClimbUK ClimbGroup Climb27; do
    cp "$HERE/$b/davinci-resolve/${b}_Titles.drfx" "$R/Fusion/Templates/"
    # the logo titles read their PNGs from here (Resolve cannot load images from inside a .drfx)
    mkdir -p "$R/Fusion/Templates/Edit/Titles/$b"
    cp "$HERE/$b/davinci-resolve/setting-files/"*.png "$R/Fusion/Templates/Edit/Titles/$b/"
done
cp "$HERE/_shared/luts/Climb_Grade_v1.cube" "$R/LUT/Climb/"
echo "Climb titles installed. Open DaVinci Resolve."
