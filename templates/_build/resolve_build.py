"""DaVinci Resolve Fusion Title templates (.setting macros packed as a .drfx bundle) for each brand.

Install: double-click the .drfx (Resolve 18 and later), or drag it onto the Fusion page. The titles then appear in the
Edit page under Effects > Titles > Fusion Titles > <Brand>. Each title is a 4K (3840x2160) comp; Resolve fits it to the
timeline. Text fields are exposed in the Inspector.

python3 resolve_build.py [Brand ...]
"""
import os
import sys
import zipfile

import brand as B

W, H = 3840, 2160


def hexf(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lua(v, ind=0):
    pad = "\t" * ind
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return ("%.6f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return '"%s"' % v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    if isinstance(v, Raw):
        return v.s
    if isinstance(v, tuple):
        return "{ %s }" % ", ".join(lua(x) for x in v)
    if isinstance(v, dict):
        inner = ",\n".join("%s\t%s = %s" % (pad, k, lua(x, ind + 1)) for k, x in v.items())
        return "{\n%s,\n%s}" % (inner, pad)
    raise TypeError(v)


class Raw:
    def __init__(self, s):
        self.s = s


def inp(value):
    return Raw("Input { Value = %s, }" % lua(value))


def link(op, source="Output"):
    return Raw('Input { SourceOp = "%s", Source = "%s", }' % (op, source))


def tool(kind, inputs, extra=""):
    body = ",\n".join("\t\t\t\t\t%s = %s" % (k, v.s if isinstance(v, Raw) else lua(v)) for k, v in inputs.items())
    return Raw("%s {%s\n\t\t\t\tInputs = {\n%s,\n\t\t\t\t},\n\t\t\t}" % (kind, extra, body))


def spline(keys):
    """keys: [(frame, value)], eased like the brand rise curve (fast out, slow in)."""
    parts = []
    for i, (f, v) in enumerate(keys):
        bits = ["%s" % lua(float(v))]
        if i < len(keys) - 1:
            nf, nv = keys[i + 1]
            bits.append("RH = { %s, %s }" % (lua(f + (nf - f) * 0.16), lua(v + (nv - v) * 1.0)))
        if i > 0:
            pf, pv = keys[i - 1]
            bits.append("LH = { %s, %s }" % (lua(f - (f - pf) * 0.7), lua(v)))
        parts.append("[%d] = { %s }" % (f, ", ".join(bits)))
    return Raw("BezierSpline {\n\t\t\t\tSplineColor = { Red = 232, Green = 113, Blue = 42 },\n\t\t\t\tKeyFrames = {\n\t\t\t\t\t%s\n\t\t\t\t}\n\t\t\t}"
               % ",\n\t\t\t\t\t".join(parts))


def canvas():
    return tool("Background", {"Width": inp(W), "Height": inp(H), "UseFrameFormatSettings": inp(0),
                               "TopLeftRed": inp(0.0), "TopLeftGreen": inp(0.0), "TopLeftBlue": inp(0.0),
                               "TopLeftAlpha": inp(0.0)})


def block(w, h, colour, alpha=1.0):
    r, g, b = hexf(colour)
    return tool("Background", {"Width": inp(int(w)), "Height": inp(int(h)), "UseFrameFormatSettings": inp(0),
                               "TopLeftRed": inp(r * alpha), "TopLeftGreen": inp(g * alpha), "TopLeftBlue": inp(b * alpha),
                               "TopLeftAlpha": inp(alpha)})


def text(value, font, style, size_px, colour, cx, cy, caps=False, tracking=1.0):
    r, g, b = hexf(colour)
    return tool("TextPlus", {
        "Width": inp(W), "Height": inp(H), "UseFrameFormatSettings": inp(0),
        "StyledText": inp(value.upper() if caps else value),
        "Font": inp(font), "Style": inp(style),
        "Size": inp(round(size_px / H, 5)),
        "CharacterSpacing": inp(tracking),
        "Center": inp((round(cx / W, 5), round(1 - cy / H, 5))),
        "HorizontalLeftCenterRight": inp(-1), "HorizontalJustificationNew": inp(3),
        "VerticalTopCenterBottom": inp(0), "VerticalJustificationNew": inp(3),
        "Red1": inp(r), "Green1": inp(g), "Blue1": inp(b), "Alpha1": inp(1.0),
    })


class Macro:
    def __init__(self, name):
        self.name = name
        self.tools = []
        self.inputs = []
        self.last = None

    def add(self, name, t):
        self.tools.append((name, t))
        return name

    def merge(self, name, fg, cx=None, cy=None, blend=None, angle=None):
        ins = {"Background": link(self.last), "Foreground": link(fg)}
        if cx is not None:
            ins["Center"] = inp((round(cx / W, 5), round(1 - cy / H, 5)))
        if blend:
            sp = name + "Blend"
            self.tools.append((sp, spline(blend)))
            ins["Blend"] = link(sp, "Value")
        self.add(name, tool("Merge", ins))
        self.last = name

    def rise(self, name, src, start, px=32, dur=18):
        """A Transform whose Y offset rises px pixels into place, with the brand rise curve."""
        xs, ys = name + "X", name + "Y"
        self.tools.append((xs, spline([(0, 0.5), (start + dur, 0.5)])))
        self.tools.append((ys, spline([(start, 0.5 - px / H), (start + dur, 0.5)])))
        self.tools.append((name + "Path", Raw('XYPath {\n\t\t\t\tShowKeyPoints = false,\n\t\t\t\tDrawMode = "ModifyOnly",\n'
                                              '\t\t\t\tInputs = {\n\t\t\t\t\tX = Input { SourceOp = "%s", Source = "Value", },\n'
                                              '\t\t\t\t\tY = Input { SourceOp = "%s", Source = "Value", },\n\t\t\t\t},\n\t\t\t}'
                                              % (xs, ys))))
        self.add(name, tool("Transform", {"Input": link(src), "Center": link(name + "Path", "Value")}))
        return name

    def expose(self, label, op, source="StyledText", default=None):
        self.inputs.append((label, op, source, default))

    def text(self):
        ins = []
        for i, (label, op, source, default) in enumerate(self.inputs, 1):
            d = (", Default = %s" % lua(default)) if default is not None else ""
            ins.append('\t\t\t\tInput%d = InstanceInput { SourceOp = "%s", Source = "%s", Name = "%s"%s, },' % (i, op, source, label, d))
        tools = ",\n".join("\t\t\t\t%s = %s" % (n, t.s) for n, t in self.tools)
        return ("{\n\tTools = ordered() {\n\t\t%s = MacroOperator {\n\t\t\tCtrlWZoom = false,\n\t\t\tNameSet = true,\n"
                "\t\t\tInputs = ordered() {\n%s\n\t\t\t},\n\t\t\tOutputs = {\n\t\t\t\tMainOutput1 = InstanceOutput { "
                'SourceOp = "%s", Source = "Output", },\n\t\t\t},\n\t\t\tViewInfo = GroupInfo { Pos = { 0, 0 } },\n'
                "\t\t\tTools = ordered() {\n%s\n\t\t\t},\n\t\t},\n\t},\n\tActiveTool = \"%s\"\n}\n"
                % (self.name, "\n".join(ins), self.last, tools, self.name))


def lower_third_classic():
    m = Macro("Climb_LowerThird_Classic")
    m.last = m.add("Canvas", canvas())
    bx, by, bw, bh = 192, 1640, 1720, 300
    m.add("Bar", block(bw, bh, B.DARK, 0.85))
    m.merge("MergeBar", "Bar", bx + bw / 2, by + bh / 2, blend=[(0, 0), (10, 1)])
    m.add("Rule", block(12, bh, B.ORANGE))
    m.merge("MergeRule", "Rule", bx + 6, by + bh / 2, blend=[(2, 0), (12, 1)])
    m.add("NameText", text("First name Last name", "Montserrat", "Bold", 104, B.WHITE, bx + 72, by + 106))
    m.rise("NameRise", "NameText", 4)
    m.merge("MergeName", "NameRise", blend=[(4, 0), (16, 1)])
    m.add("RoleText", text("Role, Company", "Open Sans", "Regular", 60, B.GREY, bx + 74, by + 214))
    m.rise("RoleRise", "RoleText", 6)
    m.merge("MergeRole", "RoleRise", blend=[(6, 0), (18, 1)])
    m.expose("Name", "NameText", default="First name Last name")
    m.expose("Role and company", "RoleText", default="Role, Company")
    m.expose("Bar width", "Bar", "Width")
    return m


def lower_third_festival(b):
    m = Macro("Climb_LowerThird_Festival")
    m.last = m.add("Canvas", canvas())
    px, py, pw, ph = 192, 1420, 2000, 560
    m.add("Panel", block(pw, ph, B.DARK))
    m.merge("MergePanel", "Panel", px + pw / 2, py + ph / 2, blend=[(0, 0), (10, 1)])
    m.add("Slab", block(420, 44, B.ORANGE))
    m.merge("MergeSlab", "Slab", px + 210, py + ph + 22, blend=[(3, 0), (13, 1)])
    m.add("Pill", block(520, 30, B.ORANGE))
    m.merge("MergePill", "Pill", px + 90 + 260, py + 197, blend=[(4, 0), (14, 1)])
    m.add("FirstName", text("First name", "Montserrat", "Black", 132, B.WHITE, px + 90, py + 135, caps=True))
    m.rise("FirstRise", "FirstName", 5)
    m.merge("MergeFirst", "FirstRise", blend=[(5, 0), (17, 1)])
    m.add("LastName", text("Last name", "Montserrat", "Black", 132, B.WHITE, px + 90, py + 265, caps=True))
    m.rise("LastRise", "LastName", 7)
    m.merge("MergeLast", "LastRise", blend=[(7, 0), (19, 1)])
    m.add("RoleText", text("Role, Company", "Open Sans", "SemiBold Italic", 58, B.TINT, px + 92, py + 450))
    m.rise("RoleRise", "RoleText", 9)
    m.merge("MergeRole", "RoleRise", blend=[(9, 0), (21, 1)])
    m.add("Mark", text(b, "Montserrat", "ExtraBold", 64, B.ORANGE, px + pw - 470, py + 82))
    m.merge("MergeMark", "Mark", blend=[(8, 0), (20, 1)])
    m.expose("First name", "FirstName", default="First name")
    m.expose("Last name", "LastName", default="Last name")
    m.expose("Role and company", "RoleText", default="Role, Company")
    m.expose("Brand mark", "Mark", default=b)
    return m


def title_two_line(b):
    m = Macro("Climb_Title")
    m.last = m.add("Canvas", canvas())
    m.add("Rule", block(256, 24, B.ORANGE))
    m.merge("MergeRule", "Rule", 192 + 64 + 128, 612, blend=[(0, 0), (10, 1)])
    lines = {"ClimbUK": ("Not a conference.", "A festival."), "ClimbGroup": ("Business growth", "with a party."),
             "Climb27": ("Your business.", "Bigger stage.")}[b]
    m.add("Line1", text(lines[0], "Montserrat", "Black", 260, B.WHITE, 252, 830, caps=True))
    m.rise("Line1Rise", "Line1", 3, px=96)
    m.merge("MergeLine1", "Line1Rise", blend=[(3, 0), (15, 1)])
    m.add("Line2", text(lines[1], "Montserrat", "Black", 260, B.ORANGE, 252, 1100, caps=True))
    m.rise("Line2Rise", "Line2", 7, px=96)
    m.merge("MergeLine2", "Line2Rise", blend=[(7, 0), (19, 1)])
    m.expose("Line 1 (White)", "Line1", default=lines[0].upper())
    m.expose("Line 2 (Climb Orange)", "Line2", default=lines[1].upper())
    return m


def sticker():
    m = Macro("Climb_Sticker")
    m.last = m.add("Canvas", canvas())
    m.add("Tag", block(900, 170, B.ORANGE))
    m.add("Label", tool("TextPlus", {
        "Width": inp(900), "Height": inp(170), "UseFrameFormatSettings": inp(0), "StyledText": inp("MAIN STAGE"),
        "Font": inp("Montserrat"), "Style": inp("Black"), "Size": inp(round(96 / 170, 4)),
        "Red1": inp(1.0), "Green1": inp(1.0), "Blue1": inp(1.0), "Alpha1": inp(1.0)}))
    m.add("TagLabel", tool("Merge", {"Background": link("Tag"), "Foreground": link("Label")}))
    m.tools.append(("PopSize", spline([(0, 0.6), (4, 1.06), (10, 1.0)])))
    m.add("Pop", tool("Transform", {"Input": link("TagLabel"), "Angle": inp(4.0), "Size": link("PopSize", "Value")}))
    m.merge("MergeTag", "Pop", 360 + 450, 300 + 85, blend=[(0, 0), (3, 1)])
    m.expose("Sticker text", "Label", default="MAIN STAGE")
    m.expose("Sticker width", "Tag", "Width")
    m.expose("Position", "MergeTag", "Center")
    return m


def build(b):
    d = os.path.join(B.OUT, "video", b, "davinci-resolve")
    os.makedirs(d, exist_ok=True)
    macros = {
        "%s Lower Third Classic" % b: lower_third_classic(),
        "%s Lower Third Festival" % b: lower_third_festival(b),
        "%s Title" % b: title_two_line(b),
        "%s Sticker" % b: sticker(),
    }
    out = os.path.join(d, "%s_Titles.drfx" % b)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, m in macros.items():
            z.writestr("Edit/Titles/%s/%s.setting" % (b, name), m.text())
    # Loose copies too, for manual install into the Fusion Templates folder.
    loose = os.path.join(d, "setting-files")
    os.makedirs(loose, exist_ok=True)
    for name, m in macros.items():
        open(os.path.join(loose, name + ".setting"), "w").write(m.text())
    print(out)


if __name__ == "__main__":
    for b in sys.argv[1:] or list(B.BRANDS):
        build(b)
