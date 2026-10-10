"""Contact sheet of the video stills per brand. Transparent graphics are shown over a real event photo, as they would
sit over footage.

python3 video_previews.py
"""
import glob
import os

from PIL import Image

import brand as B
from previews_build import sheet

FOOTAGE = B.photo("crowd_wide")


def over_footage(path):
    im = Image.open(path)
    if im.mode != "RGBA":
        return im.convert("RGB")
    w, h = im.size
    bg = Image.open(FOOTAGE).convert("RGBA")
    scale = max(w / bg.width, h / bg.height)
    bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - w) // 2, (bg.height - h) // 2, (bg.width - w) // 2 + w, (bg.height - h) // 2 + h))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    dest = os.path.join(B.OUT, "video", "previews")
    os.makedirs(dest, exist_ok=True)
    shared = sorted(glob.glob(os.path.join(B.OUT, "video", "_shared", "stills", "*_16x9_4K.*")) +
                    glob.glob(os.path.join(B.OUT, "video", "_shared", "stills", "LowerThird*")) +
                    glob.glob(os.path.join(B.OUT, "video", "_shared", "stills", "Sticker_*")))
    for b in B.BRANDS:
        own = sorted(f for f in glob.glob(os.path.join(B.OUT, "video", b, "stills", "*")) if "9x16" not in f)
        ims = [over_footage(f) for f in own + shared]
        ims = [im.resize((960, int(im.height * 960 / im.width)), Image.LANCZOS) for im in ims]
        sheet(ims, 3, 640).save(os.path.join(dest, "%s_Video.jpg" % b), quality=86)
        print(b, len(ims))


if __name__ == "__main__":
    main()
