"""Climb grade v1: a starting-point 33-point 3D LUT (.cube) for Rec.709 footage, built to guidelines/video.md.

Rich blacks that lean Dark Brown (shadows lifted a touch toward warm), skin tones kept close to true, orange saturated
but rolled off before it clips, gentle contrast. Apply after a normal technical grade (exposure and white balance),
then check it on real footage from the edition before sharing it with crews.

python3 lut_build.py  ->  video/_shared/luts/Climb_Grade_v1.cube and a before/after preview
"""
import colorsys
import math
import os

import numpy as np
from PIL import Image

import brand as B
import copy_io as C

N = 33
COPY = "video/_shared/luts/luts.copy.md"


def grade(rgb):
    r, g, b = rgb
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # Gentle S-curve around the mid grey.
    def s(v):
        return v + 0.10 * math.sin(2 * math.pi * (v - 0.5)) * -0.25 * 4 * v * (1 - v)
    r, g, b = s(r), s(g), s(b)
    # Warm lift in the shadows toward Dark Brown (#1E0F05 = 0.118, 0.059, 0.020).
    w = (1 - min(1, y / 0.45)) ** 2
    r, g, b = r + 0.030 * w, g + 0.014 * w, b + 0.003 * w
    # Saturation: a little more overall, more on oranges, less on skin-like hues so faces stay true.
    h, l, sat = colorsys.rgb_to_hls(min(max(r, 0), 1), min(max(g, 0), 1), min(max(b, 0), 1))
    deg = h * 360
    boost = 1.05
    if 15 <= deg <= 40:          # Climb Orange and stage light
        boost = 1.14
    if 8 <= deg <= 30 and 0.35 <= l <= 0.8 and sat < 0.55:   # skin
        boost = 1.0
    sat = min(1.0, sat * boost)
    r, g, b = colorsys.hls_to_rgb(h, l, sat)
    # Soft roll-off above 0.9 so saturated orange never hard-clips.
    def roll(v):
        return v if v < 0.9 else 0.9 + 0.1 * (1 - math.exp(-(v - 0.9) / 0.1))
    return tuple(min(1.0, max(0.0, roll(v))) for v in (r, g, b))


def write_cube(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        words = C.load(COPY)
        f.write('TITLE "%s"\n' % words.one("cube.title").text)
        f.write("".join("# %s\n" % line for line in C.items(words.one("cube.comment"))))
        f.write("LUT_3D_SIZE %d\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n" % N)
        for bi in range(N):
            for gi in range(N):
                for ri in range(N):
                    out = grade((ri / (N - 1), gi / (N - 1), bi / (N - 1)))
                    f.write("%.6f %.6f %.6f\n" % out)


def apply(path_in, cube_vals):
    im = np.asarray(Image.open(path_in).convert("RGB")).astype(np.float32) / 255
    idx = np.clip(np.rint(im * (N - 1)).astype(int), 0, N - 1)
    out = cube_vals[idx[..., 2], idx[..., 1], idx[..., 0]]
    return Image.fromarray((out * 255).clip(0, 255).astype(np.uint8))


def main():
    d = os.path.join(B.OUT, "video", "_shared", "luts")
    p = os.path.join(d, "Climb_Grade_v1.cube")
    write_cube(p)
    vals = np.loadtxt(p, skiprows=6).reshape(N, N, N, 3)
    src = B.photo("band_stage")
    before = Image.open(src).convert("RGB")
    after = apply(src, vals)
    w, h = before.size
    sheet = Image.new("RGB", (w * 2, h))
    sheet.paste(before, (0, 0))
    sheet.paste(after, (w, 0))
    sheet.save(os.path.join(d, "Climb_Grade_v1_before-after.jpg"), quality=88)
    print(p)


if __name__ == "__main__":
    main()
