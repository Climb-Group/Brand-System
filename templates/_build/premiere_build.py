"""A ready-made 4K 25fps Premiere Pro sequence (Final Cut Pro 7 XML, which Premiere and Resolve both import) that lays
out every motion graphic in the kit on its own track, so editors copy what they need into their own timelines.

Import: File > Import > <Brand>_Graphics_4K25.xml. Premiere asks to locate the first file; point it at the kit's
video folder and it relinks the rest.

python3 premiere_build.py [Brand ...]
"""
import os
import sys
from xml.sax.saxutils import escape

import brand as B

FPS = 25
W, H = 3840, 2160


def rate():
    return "<rate><timebase>%d</timebase><ntsc>FALSE</ntsc></rate>" % FPS


class Seq:
    def __init__(self, name):
        self.name = name
        self.tracks = {}
        self.files = {}
        self.n = 0

    def clip(self, track, rel, start_s, dur_s, w=W, h=H, alpha=True):
        self.n += 1
        fid = self.files.setdefault(rel, "file-%d" % (len(self.files) + 1))
        first = len([1 for t in self.tracks.values() for c in t if fid in c]) == 0
        start, end = int(start_s * FPS), int((start_s + dur_s) * FPS)
        name = os.path.basename(rel)
        if first:
            fx = ('<file id="%s"><name>%s</name><pathurl>file://localhost/%s</pathurl>%s<duration>%d</duration>'
                  '<media><video><samplecharacteristics>%s<width>%d</width><height>%d</height>'
                  '<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video></media></file>'
                  % (fid, escape(name), escape(rel), rate(), end - start, rate(), w, h))
        else:
            fx = '<file id="%s"/>' % fid
        item = ('<clipitem id="clip-%d"><name>%s</name><duration>%d</duration>%s<start>%d</start><end>%d</end><in>0</in>'
                '<out>%d</out>%s%s</clipitem>'
                % (self.n, escape(name), end - start, rate(), start, end, end - start, fx,
                   "<alphatype>straight</alphatype>" if alpha else ""))
        self.tracks.setdefault(track, []).append(item)

    def xml(self):
        total = 0
        for t in self.tracks.values():
            for c in t:
                e = int(c.split("<end>")[1].split("<")[0])
                total = max(total, e)
        tracks = "".join("<track>%s</track>" % "".join(self.tracks[k]) for k in sorted(self.tracks))
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="seq-1">'
                '<name>%s</name><duration>%d</duration>%s<media><video><format><samplecharacteristics>%s<width>%d</width>'
                '<height>%d</height><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance>'
                '</samplecharacteristics></format>%s</video><audio/></media></sequence></xmeml>\n'
                % (escape(self.name), total, rate(), rate(), W, H, tracks))


def build(b):
    s = Seq("%s graphics kit 4K 25p" % b)
    sh = "video/_shared/motion/"
    me = "video/%s/motion/" % b
    # V1 grounds and full-frame cards.
    s.clip(1, sh + "Background_StageLight_Loop_16x9_4K25.mp4", 0, 8, alpha=False)
    s.clip(1, me + "%s_TitleCard_4K25.mp4" % b, 8, 5, alpha=False)
    s.clip(1, sh + "Background_StageLight_Loop_16x9_4K25.mp4", 13, 8, alpha=False)
    s.clip(1, me + "%s_EndCard_Sting_16x9_4K25.mp4" % b, 21, 8, alpha=False)
    # V2 lower thirds.
    s.clip(2, sh + "LowerThird_Classic_4K25.mov", 0.5, 6)
    s.clip(2, me + "%s_LowerThird_Festival_4K25.mov" % b, 13.5, 6)
    # V3 plates to type over (Essential Graphics text on V4).
    s.clip(3, sh + "LowerThird_Classic_Plate_4K25.mov", 0.5, 6)
    s.clip(3, me + "%s_LowerThird_Festival_Plate_4K25.mov" % b, 13.5, 6)
    # V5 stickers and the wipe.
    s.clip(5, sh + "Sticker_Mainstage_4K25.mov", 3, 3)
    s.clip(5, sh + "Transition_SlabWipe_4K25.mov", 7.5, 1)
    s.clip(5, sh + "Sticker_ClimbAwards_4K25.mov", 16, 3)
    s.clip(5, sh + "Transition_SlabWipe_4K25.mov", 20.5, 1)
    d = os.path.join(B.OUT, "video", b, "premiere-pro")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "%s_Graphics_4K25.xml" % b)
    open(p, "w").write(s.xml())
    print(p)


if __name__ == "__main__":
    for b in sys.argv[1:] or list(B.BRANDS):
        build(b)
