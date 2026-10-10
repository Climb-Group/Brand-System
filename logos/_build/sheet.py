#!/usr/bin/env python3
"""One contact sheet per brand: variants (columns) x backgrounds (rows), with contrast notes."""
import os, subprocess, base64
from build import OUT, VARIANTS, ORANGE, ORANGE_GREY, BROWN, CHAR, GREY, WHITE, ratio

BGS = [("White", WHITE), ("Light Grey", GREY), ("Dark Brown", BROWN), ("Charcoal", CHAR)]
CW, CH, LW, TH = 520, 300, 170, 110  # cell w/h, label column, header height


def note(key, bg):
    """Lowest contrast between the logo's marks and the background (3:1 graphic threshold)."""
    if key.startswith("icon"):
        return None  # self-contained tile; marks sit on Dark Brown (orange 6.06, white 18.65)
    c1, c2 = {k: (a, b) for k, _, a, b, _ in VARIANTS if not k.startswith("icon")}[key]
    r = min(ratio(c1, bg), ratio(c2, bg))
    return r


def main():
    for brand in ("ClimbUK", "ClimbGroup", "Climb27"):
        bdir = os.path.join(OUT, brand)
        W = LW + CW * len(VARIANTS)
        H = TH + CH * len(BGS) + 50
        parts = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
                 f'<text x="24" y="44" font-family="Open Sans" font-weight="700" font-size="28" fill="{BROWN}">{brand} - 2026 master logos</text>']
        for i, (key, label, *_rest) in enumerate(VARIANTS):
            parts.append(f'<text x="{LW + i * CW + CW / 2}" y="{TH - 10}" text-anchor="middle" font-family="Open Sans" '
                         f'font-weight="700" font-size="20" fill="{BROWN}">{label}</text>')
        for j, (bname, bg) in enumerate(BGS):
            y = TH + j * CH
            parts.append(f'<text x="20" y="{y + CH / 2 + 7}" font-family="Open Sans" font-weight="700" font-size="20" fill="{BROWN}">{bname}</text>')
            for i, (key, *_r) in enumerate(VARIANTS):
                x = LW + i * CW
                parts.append(f'<rect x="{x + 4}" y="{y + 4}" width="{CW - 8}" height="{CH - 8}" fill="{bg}" stroke="#bbbbbb" stroke-width="1"/>')
                png = os.path.join(bdir, "PNG", f"{brand}_{key}_1024.png")
                data = base64.b64encode(open(png, "rb").read()).decode()
                from PIL import Image
                iw, ih = Image.open(png).size
                maxw, maxh = (CH - 110, CH - 110) if key.startswith("icon") else (CW - 80, CH - 110)
                k = min(maxw / iw, maxh / ih)
                dw, dh = iw * k, ih * k
                parts.append(f'<image x="{x + (CW - dw) / 2:.1f}" y="{y + (CH - 40 - dh) / 2:.1f}" width="{dw:.1f}" height="{dh:.1f}" '
                             f'href="data:image/png;base64,{data}"/>')
                r = note(key, bg)
                txt = "tile (orange 6.06:1 on Dark Brown)" if r is None else f"min contrast {r:.2f}:1 - {'PASS' if r >= 3 else 'FAIL'}"
                col = "#888888" if bg in (WHITE, GREY) else "#BBBBBB"
                if r is not None and r < 3:
                    col = "#C00000" if bg in (WHITE, GREY) else "#FF6B6B"
                parts.append(f'<text x="{x + CW / 2}" y="{y + CH - 18}" text-anchor="middle" font-family="Open Sans" font-size="16" fill="{col}">{txt}</text>')
        parts.append(f'<text x="24" y="{H - 18}" font-family="Open Sans" font-size="16" fill="#666666">'
                     f'Orange {ORANGE} (was #EC752A); on-grey orange {ORANGE_GREY}; wordmark dark {CHAR}; tiles {BROWN}. WCAG 1.4.11 graphic threshold 3:1. '
                     f'FAIL cells show where a variant must not be used.</text>')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">' + "".join(parts) + "</svg>"
        out = os.path.join(bdir, f"{brand}_contact-sheet.png")
        subprocess.run(["rsvg-convert", "-o", out], input=svg.encode(), check=True)
        print(out)


if __name__ == "__main__":
    main()
