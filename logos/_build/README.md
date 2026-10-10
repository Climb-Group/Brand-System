# Rebuilding the logo files

These scripts regenerate every SVG, PNG and contact sheet in the parent folder from the normalised vector
sources (`vc_*.svg`):

```bash
python3 build.py && python3 sheet.py
```

Needs `rsvg-convert`, `lxml`, `Pillow` and `fontTools`. The tagline is set from `Montserrat-Bold.ttf` (SIL Open Font
License, see `OFL.txt`) and converted to outlines, so the output files need no fonts.
