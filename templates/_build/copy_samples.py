"""The example slides of every PowerPoint template, read from the template's copy file, and the helpers that place them.

The words live in office/<Brand>/powerpoint/<Brand>_<Name>.copy.md (or external/): one marker per slide naming its
layout (<!-- @slide-3 layout="Big numbers" -->), then one section per placeholder (slide-3.title, slide-3.number-1,
slide-3.photo name=band_stage box=full for a photo and its alt text). SLOTS names the placeholders.

Rich text in the builders: {word} is Climb Orange, _word_ is italic. A new line starts a new paragraph.
"""
import re
from xml.sax.saxutils import escape

from PIL import Image

import brand as B
import copy_io


def runs(text, base_colour=None, orange=B.ORANGE, sz=None):
    out = []
    for tok in re.split(r"(\{[^}]+\}|_[^_]+_)", text):
        if not tok:
            continue
        colour, ital = base_colour, None
        if tok.startswith("{"):
            tok, colour = tok[1:-1], orange
        elif tok.startswith("_") and tok.endswith("_") and len(tok) > 2:
            tok, ital = tok[1:-1], 1
        attrs = ' lang="en-GB"' + (' i="1"' if ital else "") + (' sz="%d"' % (sz * 100) if sz else "")
        fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % colour if colour else ""
        out.append('<a:r><a:rPr%s dirty="0">%s</a:rPr><a:t>%s</a:t></a:r>' % (attrs, fill, escape(tok)))
    return "".join(out)


def paras(text, **kw):
    lines = text if isinstance(text, list) else text.split("\n")
    return "".join('<a:p>%s</a:p>' % runs(l, **kw) for l in lines)


def _layout_ph(t, typ, idx):
    ph = t.layout.phs.get((typ, idx))
    if ph is None:
        raise KeyError("layout has no placeholder %s %s" % (typ, idx))
    return ph


def sph(t, typ, idx, text, **kw):
    """A slide placeholder linked to its layout. Position and text styles are repeated on the slide so apps that only
    partly read layouts (LibreOffice, Google Slides, Keynote) still show the sample as designed."""
    ph = _layout_ph(t, typ, idx)
    ty = ' type="%s"' % typ if typ else ""
    ix = ' idx="%d"' % idx if idx is not None else ""
    t.items.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s %s"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
                   '<p:nvPr><p:ph%s%s/></p:nvPr></p:nvSpPr><p:spPr>%s</p:spPr><p:txBody>%s<a:lstStyle>%s</a:lstStyle>%s'
                   '</p:txBody></p:sp>'
                   % (t.nid(), typ or "body", idx, ty, ix, ph["sppr"], ph["bodypr"], ph["lst"], paras(text, **kw)))


def sphoto(t, idx, photo, box, descr):
    """Fill a picture placeholder, cropping the photo to the box (x, y, w, h in inches)."""
    path = B.photo(photo)
    iw, ih = Image.open(path).size
    _, _, bw, bh = box
    ia, ba = iw / ih, bw / bh
    if ia > ba:
        cut = (1 - ba / ia) / 2
        src = '<a:srcRect l="%d" r="%d"/>' % (cut * 100000, cut * 100000)
    else:
        cut = (1 - ia / ba) / 2
        src = '<a:srcRect t="%d" b="%d"/>' % (cut * 100000, cut * 100000)
    rid = t.media(path)
    ph = _layout_ph(t, "pic", idx)
    t.items.append('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="Photo %d" descr="%s"/><p:cNvPicPr><a:picLocks noGrp="1" '
                   'noChangeAspect="1"/></p:cNvPicPr><p:nvPr><p:ph type="pic" idx="%d"/></p:nvPr></p:nvPicPr><p:blipFill>'
                   '<a:blip r:embed="%s"/>%s<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>%s</p:spPr></p:pic>'
                   % (t.nid(), idx, escape(descr), idx, rid, src, ph["sppr"]))


W, H = 13.333, 7.5
# Where a photo sits on its layout (x, y, w, h in inches): box= in a copy file's photo section.
BOXES = {"full": (0, 0, W, H - 1.55), "title": (6.2, 0, W - 6.2, H), "wall-1": (5.0, 0, 5.0, H),
         "wall-2": (10.08, 0, W - 10.08, H / 2), "wall-3": (10.08, H / 2, W - 10.08, H / 2)}
# A copy file's slot names and the placeholder (type, idx) each fills.
SLOTS = {"eyebrow": ("body", 13), "title": ("title", None), "sub": ("subTitle", 1), "body": (None, 1),
         "body-2": (None, 2), "line": ("body", 1), "column-1": ("body", 16), "column-2": ("body", 17),
         "date": ("body", 14), "times": ("body", 19), "role": ("body", 18), "number-1": ("body", 20),
         "number-2": ("body", 21), "number-3": ("body", 22), "label-1": ("body", 23), "label-2": ("body", 24),
         "label-3": ("body", 25), "sticker": ("body", 30), "time": ("body", 14), "stage": ("body", 15),
         "host": ("body", 14), "contact": ("body", 13)}


def resolve(slot, phs):
    """The placeholder a slot fills on a layout: the title is the centred title on the title layouts, and the same slot
    is a body or an object placeholder, by layout."""
    typ, idx = SLOTS[slot]
    if slot == "title" and ("title", None) not in phs and ("ctrTitle", None) in phs:
        return ("ctrTitle", None)
    if (typ, idx) not in phs:
        for alt in ((None, idx), ("body", idx)):
            if alt in phs:
                typ, idx = alt
    return typ, idx


def section_text(s):
    """A section's words as the builders' rich text, one paragraph per list item or line break."""
    lines = copy_io.items(s) if s.text.lstrip().startswith(("- ", "* ")) else s.text.split("\n")
    return [copy_io.rich(x) for x in lines]


def fill_from(sections, extra=None):
    """The fill for one slide from its copy file sections, in order."""
    def fill(t, spec):
        for s in sections:
            slot = s.path.split(".", 1)[1]
            if slot == "photo":
                sphoto(t, int(s.get("slot", 15)), s["name"], BOXES[s["box"]], s.text)
            elif slot.startswith("org-"):
                continue
            else:
                typ, idx = resolve(slot, t.layout.phs)
                sph(t, typ, idx, section_text(s))
        if extra:
            extra(t, sections)
    return fill


def slides(path, fills=None):
    """[(layout name, fill(tree, spec)), ...] for the example slides in a copy file. A slide marker names its layout
    (layout=) and may name a special fill (fill=org-chart) from fills."""
    doc = copy_io.load(path)
    out = []
    for s in doc.sections:
        if "." not in s.path:
            parts = [x for x in doc.sections if x.path.startswith(s.path + ".")]
            out.append((s["layout"], fill_from(parts, (fills or {}).get(s.get("fill")))))
    return out
