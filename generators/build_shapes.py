"""Write the motif families as website background shapes for the climb_website_brand module.

    python3 generators/build_shapes.py

The website editor recolours a shape by swapping its five placeholder colours (#3AADAA, #7C6576, #F6F6F6, #FFFFFF, #383E45) for
the colours the editor picks. These shapes use placeholder 1 (#3AADAA, Climb Orange by default) for the one
marker and placeholder 4 (#FFFFFF, White by default) for the quiet lines, so on a dark preset they look exactly like
the asset catalogue, and on a light preset the editor can switch colour 4 to Charcoal.
"""
import pathlib
import re

import motifs as M

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "illustrations" / "shapes"
C1, C4 = "#3AADAA", "#FFFFFF"


def placeholders(svg):
    svg = re.sub(M.ORANGE, C1, svg, flags=re.I)
    svg = re.sub(M.TINT, C1, svg, flags=re.I)
    return svg


def wrap(w, h, body, align="xMaxYMax slice"):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="%s">%s</svg>\n'
            % (w, h, align, placeholders(body)))


def shapes():
    w, h = 1920, 1080
    yield "01", wrap(w, h, M.contours(w, h, seed=11, rings=12, cx=0.86, cy=0.8))
    yield "02", wrap(w, h, M.stage_light(w, h, seed=12, uid="climb-sl"), "xMidYMin slice")
    yield "03", wrap(w, h, M.connections(w, h, seed=13, region=(0.55, 0.05, 0.98, 0.95)))
    yield "04", wrap(w, h, M.ascent(w, h, w * 0.66, h, h * 0.42, steps=5), "xMaxYMax meet")
    # A low divider band: rising chevrons along the bottom edge.
    yield "05", wrap(1920, 160, M.ascent(1920, 160, 1600, 150, 120, steps=5, kind="chevrons"), "xMaxYMax meet")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in shapes():
        (OUT / ("%s.svg" % name)).write_text(svg, encoding="utf-8")
    print("[shapes] wrote %d shapes to %s" % (len(list(OUT.glob("*.svg"))), OUT))


if __name__ == "__main__":
    main()
