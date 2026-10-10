"""Climb Fusion titles for DaVinci Resolve, v2.

Builds, per brand (ClimbUK, ClimbGroup, Climb27), five Edit-page Fusion titles:
Lower Third, Lower Third Festival, Title Card, End Card and Sticker. Each is a 3840x2160 macro that
animates in (brand rise curve) from the first frame and out (exit curve) over the last frames of the
clip, whatever length the clip is, because the timing is an expression on comp.RenderEnd.

Colours come only from Brand-System/tokens/brand.tokens.json. Every title has a "Colour variant"
control (the brand presets Dark Brown, Charcoal and Climb Orange), and its text, plus colour pickers
where the brand allows a choice.

Install: run video/Install Climb Titles (Resolve).command, or double-click the .drfx and copy the logo PNGs from
setting-files/ to Fusion/Templates/Edit/Titles/<Brand>/ (Resolve cannot load images from inside a .drfx).

python3 resolve_build.py [Brand ...]
"""
import json
import os
import shutil
import sys
import zipfile

import brand as B

W, H = 3840, 2160
FPS = 25

# Fusion Text+ Size is relative to the image width, and sets the font's line height (ascent plus descent), not its
# em size, at 0.8 of Size x width. LINE_HEIGHT is each font's line height in ems (hhea), measured against the brand
# stills in Resolve 21: Montserrat renders at 0.656 and Open Sans at 0.587 of the CSS size without it.
LINE_HEIGHT = {"Montserrat": 1.219, "Open Sans": 1.362}

BRANDS = {
    "ClimbUK": dict(url="CLIMB-UK.COM", line="FIND YOUR PEOPLE",
                    title=("FIND YOUR", "PEOPLE.")),
    "ClimbGroup": dict(url="CLIMB-GROUP.COM", line="FIND YOUR PEOPLE",
                       title=("BUILT FOR UK", "GROWTH.")),
    "Climb27": dict(url="CLIMB-UK.COM", line="30 JUNE AND 1 JULY 2027",
                    title=("YOUR BIGGER", "STAGE.")),
}


# ----------------------------------------------------------------------------------------------- tokens

def load_tokens(root):
    d = json.load(open(os.path.join(root, "tokens", "brand.tokens.json")))
    c = d["color"]

    def v(node):
        return node.get("$value", node.get("value"))

    hexes = {
        "orange": v(c["brand"]["orange"]), "dark_brown": v(c["brand"]["dark-brown"]),
        "light_grey": v(c["brand"]["light-grey"]), "white": v(c["brand"]["white"]),
        "charcoal": v(c["brand"]["charcoal"]), "tint": v(c["orange"]["tint"]),
    }
    return {k: tuple(round(int(h[i:i + 2], 16) / 255, 6) for i in (1, 3, 5)) for k, h in hexes.items()}


# ----------------------------------------------------------------------------------------------- writer

def num(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    s = ("%.6f" % x).rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def q(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def val(x):
    if isinstance(x, tuple):
        return "{ %s }" % ", ".join(num(a) for a in x)
    if isinstance(x, str):
        return q(x)
    return num(x)


class Expr:
    """An input driven by a Fusion expression; `default` is what Resolve shows before evaluating."""

    def __init__(self, expr, default=0):
        self.expr, self.default = expr, default


class Link:
    def __init__(self, op, source="Output"):
        self.op, self.source = op, source


class Raw:
    def __init__(self, s):
        self.s = s


def inp(x):
    if isinstance(x, Expr):
        return "Input { Value = %s, Expression = %s, }" % (val(x.default), q(x.expr))
    if isinstance(x, Link):
        return 'Input { SourceOp = "%s", Source = "%s", }' % (x.op, x.source)
    if isinstance(x, Raw):
        return x.s
    return "Input { Value = %s, }" % val(x)


class Macro:
    def __init__(self, name):
        self.name = name
        self.tools = []      # (name, text)
        self.controls = []   # InstanceInput lines
        self.output = None

    def tool(self, name, kind, inputs, extra=""):
        body = "".join("\t\t\t\t\t\t%s = %s,\n" % (k, inp(v)) for k, v in inputs.items())
        self.tools.append((name, "\t\t\t\t%s = %s {\n%s\t\t\t\t\tInputs = {\n%s\t\t\t\t\t},\n\t\t\t\t},\n"
                           % (name, kind, extra, body)))
        return name

    def control(self, op, source, name=None, group=None, default=None, page=None):
        bits = ['SourceOp = "%s"' % op, 'Source = "%s"' % source]
        if name:
            bits.append("Name = %s" % q(name))
        if group is not None:
            bits.append("ControlGroup = %d" % group)
        if default is not None:
            bits.append("Default = %s" % val(default))
        if page:
            bits.append("Page = %s" % q(page))
        self.controls.append(bits)

    def colour_control(self, op, name, rgb, prefix="", group=None):
        g = group or (100 + len(self.controls))
        for ch, d in zip(("Red", "Green", "Blue"), rgb):
            self.control(op, "%s%s" % (ch, prefix), name if ch == "Red" else None, g, d)

    def render(self):
        ctrl = "".join("\t\t\t\tInput%d = InstanceInput { %s, },\n" % (i + 1, ", ".join(b))
                       for i, b in enumerate(self.controls))
        tools = "".join(t for _, t in self.tools)
        return ("{\n\tTools = ordered() {\n\t\t%s = MacroOperator {\n\t\t\tCtrlWZoom = false,\n\t\t\tNameSet = true,\n"
                "\t\t\tInputs = ordered() {\n%s\t\t\t},\n"
                "\t\t\tOutputs = {\n\t\t\t\tMainOutput1 = InstanceOutput { SourceOp = \"%s\", Source = \"Output\", },\n\t\t\t},\n"
                "\t\t\tViewInfo = GroupInfo { Pos = { 0, 0 } },\n"
                "\t\t\tTools = ordered() {\n%s\t\t\t},\n\t\t},\n\t},\n\tActiveTool = \"%s\"\n}\n"
                % (self.name, ctrl, self.output, tools, self.name))


# ----------------------------------------------------------------------------------------------- motion

IN = 18     # 700ms stage entrance, rounded to frames at 25fps
OUT = 10    # exit at roughly two thirds of the entrance
RISE = 48 / H   # rise-large travel (48px)
DROP = 16 / H   # exit travel (rise)


def p_in(delay, n=IN):
    return "min(max((time-%s)/%d,0),1)" % (num(delay), n)


def e_in(delay, n=IN):
    # brand rise curve, cubic-bezier(0.16, 1, 0.3, 1), approximated by ease-out quart
    return "(1-(1-%s)^4)" % p_in(delay, n)


def q_out(n=OUT):
    # 0 until the exit starts, 1 on the last frame
    return "(1-min(max((comp.RenderEnd-time)/%d,0),1))" % n


def e_out(n=OUT):
    # exit curve, cubic-bezier(0.4, 0, 1, 1): accelerating, approximated by ease-in quad
    return "(%s^2)" % q_out(n)


def opacity(delay):
    return "%s*(1-%s)" % (e_in(delay), e_out())


def rise_point(delay, x=0.5, y=0.5, rise=RISE):
    return "Point(%s, %s-%s*(1-%s)-%s*%s)" % (num(x), num(y), num(rise), e_in(delay), num(DROP), e_out())


# ----------------------------------------------------------------------------------------------- parts

VARIANT_NAMES = ("Dark Brown", "Charcoal", "Climb Orange")


def variant_user_control(names=VARIANT_NAMES):
    items = "".join("\t\t\t\t\t\t\t{ CCS_AddString = %s, },\n" % q(n) for n in names)
    return ("\t\t\t\t\tUserControls = ordered() {\n\t\t\t\t\t\tVariant = {\n"
            "\t\t\t\t\t\t\tLINKID_DataType = \"Number\",\n\t\t\t\t\t\t\tINPID_InputControl = \"ComboControl\",\n"
            "\t\t\t\t\t\t\tINP_Integer = true,\n\t\t\t\t\t\t\tINP_Default = 0,\n\t\t\t\t\t\t\tINP_MinScale = 0,\n"
            "\t\t\t\t\t\t\tINP_MaxScale = %d,\n\t\t\t\t\t\t\tCC_LabelPosition = \"Horizontal\",\n"
            "\t\t\t\t\t\t\tICS_ControlPage = \"Controls\",\n\t\t\t\t\t\t\tLINKS_Name = \"Colour variant\",\n%s"
            "\t\t\t\t\t\t},\n\t\t\t\t\t},\n" % (len(names) - 1, items))


def pick(values):
    """Expression choosing values[Canvas.Variant]."""
    expr = num(values[-1])
    for i in range(len(values) - 2, -1, -1):
        expr = "iif(Canvas.Variant == %d, %s, %s)" % (i, num(values[i]), expr)
    return expr


def colour_inputs(per_variant, alpha=None, prefix="TopLeft"):
    """per_variant: list of rgb tuples, one per variant. Returns Background colour inputs driven by the variant."""
    out = {}
    for i, ch in enumerate(("Red", "Green", "Blue")):
        vals = [c[i] for c in per_variant]
        out[prefix + ch] = Expr(pick(vals), vals[0]) if len(set(vals)) > 1 else vals[0]
    if alpha is not None:
        out[prefix + "Alpha"] = Expr(pick(alpha), alpha[0]) if len(set(alpha)) > 1 else alpha[0]
    return out


def canvas(m, variants=VARIANT_NAMES, ground=None):
    """Full-frame base. ground: per-variant rgb (with alpha list) for a full-frame card, or None for transparent."""
    ins = {"Width": W, "Height": H, "UseFrameFormatSettings": 0, "Variant": 0}
    if ground:
        rgbs, alphas = ground
        ins.update(colour_inputs(rgbs, alphas))
    else:
        ins.update({"TopLeftRed": 0, "TopLeftGreen": 0, "TopLeftBlue": 0, "TopLeftAlpha": 0})
    m.tool("Canvas", "Background", ins, extra=variant_user_control(variants))
    m.control("Canvas", "Variant", "Colour variant", default=0)
    return "Canvas"


def block(m, name, w, h, rgbs, alphas):
    ins = {"Width": w, "Height": h, "UseFrameFormatSettings": 0}
    ins.update(colour_inputs(rgbs, alphas))
    return m.tool(name, "Background", ins)


def text(m, name, s, font, style, px, rgb, x, y, frame=(W, H), anchor="left", tracking=1.0, var_rgb=None):
    """x, y: left (or centre) edge and vertical centre of the text, in pixels from the top left of the frame."""
    fw, fh = frame
    ins = {"Width": fw, "Height": fh, "UseFrameFormatSettings": 0, "StyledText": s, "Font": font, "Style": style,
           "Size": round(px * LINE_HEIGHT[font] / (0.8 * fw), 6), "CharacterSpacing": tracking,
           "Center": (round(x / fw, 6), round(1 - y / fh, 6)),
           "HorizontalLeftCenterRight": -1 if anchor == "left" else 0,
           "HorizontalJustificationNew": 3 if anchor == "left" else 0,
           "VerticalTopCenterBottom": 0, "VerticalJustificationNew": 3}
    if var_rgb:
        ins.update(colour_inputs(var_rgb, prefix=""))
        ins = {("%s1" % k if k in ("Red", "Green", "Blue") else k): v for k, v in ins.items()}
    else:
        ins.update({"Red1": rgb[0], "Green1": rgb[1], "Blue1": rgb[2]})
    ins["Alpha1"] = 1
    return m.tool(name, "TextPlus", ins)


def merge(m, name, bg, fg, center=None, blend=None, size=None, angle=None):
    ins = {"Background": Link(bg), "Foreground": Link(fg)}
    if center is not None:
        ins["Center"] = center
    if size is not None:
        ins["Size"] = size
    if angle is not None:
        ins["Angle"] = angle
    if blend is not None:
        ins["Blend"] = blend
    return m.tool(name, "Merge", ins)


def rise_in(m, name, bg, fg, delay, x=0.5, y=0.5, rise=RISE):
    """Merge fg (a full-frame or positioned layer) over bg, rising into (x, y) and fading in, then out."""
    return merge(m, name, bg, fg, center=Expr(rise_point(delay, x, y, rise), (x, y)), blend=Expr(opacity(delay), 1))


def loader(m, name, path):
    extra = ("\t\t\t\t\tClips = {\n\t\t\t\t\t\tClip {\n\t\t\t\t\t\t\tID = \"Clip1\",\n\t\t\t\t\t\t\tFilename = %s,\n"
             "\t\t\t\t\t\t\tFormatID = \"PNGFormat\",\n\t\t\t\t\t\t\tStartFrame = -1,\n\t\t\t\t\t\t\tLengthSetManually = true,\n"
             "\t\t\t\t\t\t\tTrimIn = 0,\n\t\t\t\t\t\t\tTrimOut = 0,\n\t\t\t\t\t\t\tExtendFirst = 0,\n\t\t\t\t\t\t\tExtendLast = 0,\n"
             "\t\t\t\t\t\t\tLoop = 1,\n\t\t\t\t\t\t\tAspectMode = 0,\n\t\t\t\t\t\t\tDepth = 0,\n\t\t\t\t\t\t\tTimeCode = 0,\n"
             "\t\t\t\t\t\t\tGlobalStart = -2000000000,\n\t\t\t\t\t\t\tGlobalEnd = 2000000000\n\t\t\t\t\t\t}\n\t\t\t\t\t},\n"
             % q(path))
    return m.tool(name, "Loader", {}, extra=extra)


def scaled(m, name, src, scale):
    return m.tool(name, "Transform", {"Input": Link(src), "Size": scale})


# ----------------------------------------------------------------------------------------------- titles

def lower_third(T, brand):
    m = Macro("Climb_LowerThird")
    canvas(m)
    bar_w, bar_h, left, bottom = 1720, 300, 192, 2160 - 1636 - 300   # bar top at y 1636, inside 5% title safe
    bar_y = 1636 + bar_h / 2
    block(m, "Bar", bar_w, bar_h, [T["dark_brown"], T["charcoal"], T["orange"]], [0.85, 0.85, 1.0])
    rise_in(m, "MergeBar", "Canvas", "Bar", 0, (left + bar_w / 2) / W, 1 - bar_y / H, rise=16 / H)
    block(m, "Rule", 12, bar_h, [T["orange"], T["orange"], T["white"]], [1, 1, 1])
    rise_in(m, "MergeRule", "MergeBar", "Rule", 2, (left + 6) / W, 1 - bar_y / H, rise=16 / H)
    text(m, "NameText", "First name Last name", "Montserrat", "Bold", 104, T["white"], 264, 1746)
    rise_in(m, "MergeName", "MergeRule", "NameText", 4)
    text(m, "RoleText", "Role, Company", "Open Sans", "Regular", 60, None, 266, 1854,
         var_rgb=[T["light_grey"], T["light_grey"], T["white"]])
    rise_in(m, "MergeRole", "MergeName", "RoleText", 6)
    m.output = "MergeRole"
    m.control("NameText", "StyledText", "Name", default="First name Last name")
    m.control("RoleText", "StyledText", "Role and company", default="Role, Company")
    m.colour_control("NameText", "Name colour", T["white"], prefix="1")
    m.control("Bar", "Width", "Bar width", default=bar_w)
    return m


def lower_third_festival(T, brand, logo):
    m = Macro("Climb_LowerThird_Festival")
    canvas(m)
    pw, ph, px, py = 2000, 560, 192, 1592      # panel top-left
    block(m, "Panel", pw, ph, [T["dark_brown"], T["charcoal"], T["orange"]], [1, 1, 1])
    rise_in(m, "MergePanel", "Canvas", "Panel", 0, (px + pw / 2) / W, 1 - (py + ph / 2) / H, rise=16 / H)
    block(m, "Slab", 420, 44, [T["orange"], T["orange"], T["dark_brown"]], [1, 1, 1])
    rise_in(m, "MergeSlab", "MergePanel", "Slab", 2, (px + 210) / W, 1 - (py + ph + 22 - 44) / H, rise=16 / H)
    # brand mark: the reversed master on dark grounds, mono white on Climb Orange
    loader(m, "MarkColour", logo["reversed"])
    loader(m, "MarkWhite", logo["mono"])
    m.tool("MarkPick", "Dissolve", {"Background": Link("MarkColour"), "Foreground": Link("MarkWhite"),
                                    "Mix": Expr("iif(Canvas.Variant == 2, 1, 0)", 0)})
    mark_w = 480
    scaled(m, "MarkSize", "MarkPick", round(mark_w / 2048, 6))
    rise_in(m, "MergeMark", "MergeSlab", "MarkSize", 3, (px + pw - 60 - mark_w / 2) / W, 1 - (py + 80) / H, rise=16 / H)
    text(m, "FirstName", "FIRST NAME", "Montserrat", "Black", 132, T["white"], 282, 1665)
    rise_in(m, "MergeFirst", "MergeMark", "FirstName", 5)
    text(m, "LastName", "LAST NAME", "Montserrat", "Black", 132, T["white"], 282, 1795)
    rise_in(m, "MergeLast", "MergeFirst", "LastName", 7)
    text(m, "RoleText", "Role, Company", "Open Sans", "SemiBold Italic", 58, None, 284, 1940,
         var_rgb=[T["tint"], T["tint"], T["white"]])
    rise_in(m, "MergeRole", "MergeLast", "RoleText", 9)
    m.output = "MergeRole"
    m.control("FirstName", "StyledText", "First name", default="FIRST NAME")
    m.control("LastName", "StyledText", "Last name", default="LAST NAME")
    m.control("RoleText", "StyledText", "Role and company", default="Role, Company")
    m.colour_control("FirstName", "First name colour", T["white"], prefix="1")
    m.colour_control("LastName", "Last name colour", T["white"], prefix="1")
    return m


def title_card(T, brand):
    m = Macro("Climb_TitleCard")
    names = VARIANT_NAMES + ("Over footage",)
    canvas(m, names, ground=([T["dark_brown"], T["charcoal"], T["orange"], T["dark_brown"]], [1, 1, 1, 0]))
    l1, l2 = BRANDS[brand]["title"]
    block(m, "Rule", 256, 24, [T["orange"], T["orange"], T["white"], T["orange"]], [1, 1, 1, 1])
    rise_in(m, "MergeRule", "Canvas", "Rule", 0, (256 + 128) / W, 1 - 612 / H, rise=16 / H)
    text(m, "Line1", l1, "Montserrat", "Black", 260, T["white"], 252, 830)
    rise_in(m, "MergeLine1", "MergeRule", "Line1", 3)
    # the one orange word (brand rule: one orange word per headline); white on the Climb Orange ground
    text(m, "Line2", l2, "Montserrat", "Black", 260, None, 252, 1100,
         var_rgb=[T["orange"], T["orange"], T["white"], T["orange"]])
    rise_in(m, "MergeLine2", "MergeLine1", "Line2", 6)
    m.output = "MergeLine2"
    m.control("Line1", "StyledText", "Line 1", default=l1)
    m.control("Line2", "StyledText", "Line 2 (one orange word)", default=l2)
    m.colour_control("Line1", "Line 1 colour", T["white"], prefix="1")
    return m


def end_card(T, brand, logo):
    m = Macro("Climb_EndCard")
    canvas(m, ground=([T["dark_brown"], T["charcoal"], T["orange"]], [1, 1, 1]))
    info = BRANDS[brand]
    lw = 1920
    loader(m, "LogoColour", logo["lockup"])
    loader(m, "LogoWhite", logo["mono"])
    # Climb Orange ground: mono white wordmark (no tagline lockup in mono, so the tagline is set in type below)
    m.tool("LogoPick", "Dissolve", {"Background": Link("LogoColour"), "Foreground": Link("LogoWhite"),
                                    "Mix": Expr("iif(Canvas.Variant == 2, 1, 0)", 0)})
    m.tool("LogoSize", "Transform", {"Input": Link("LogoPick"),
                                     "Size": Expr("iif(Canvas.Variant == 2, %s, %s)" % (num(round(lw / 2048 * 0.92, 6)),
                                                                                           num(round(lw / 2048, 6))),
                                                  round(lw / 2048, 6))})
    rise_in(m, "MergeLogo", "Canvas", "LogoSize", 0, 0.5, 1 - (648 + 260) / H)
    text(m, "Tagline", "The Festival for Business Growth", "Montserrat", "Bold", 92, T["white"], W / 2, 1110,
         anchor="centre")
    m.tool("TaglineShow", "Merge", {"Background": Link("MergeLogo"), "Foreground": Link("Tagline"),
                                    "Center": Expr(rise_point(1), (0.5, 0.5)),
                                    "Blend": Expr("iif(Canvas.Variant == 2, 1, 0)*%s" % opacity(1), 0)})
    text(m, "Line", info["line"], "Montserrat", "Black", 100, T["white"], W / 2, 1390, anchor="centre")
    rise_in(m, "MergeLine", "TaglineShow", "Line", 3)
    block(m, "Pill", 1100 if len(info["url"]) > 12 else 920, 180, [T["orange"], T["orange"], T["white"]], [1, 1, 1])
    m.tool("PillRound", "RectangleMask", {"Width": 1.0, "Height": 1.0, "CornerRadius": 1.0})
    m.tools[-2] = (m.tools[-2][0], m.tools[-2][1].replace("Inputs = {\n", "Inputs = {\n\t\t\t\t\t\tEffectMask = Input { SourceOp = \"PillRound\", Source = \"Mask\", },\n", 1))
    # the mask must exist before the pill references it
    m.tools[-1], m.tools[-2] = m.tools[-2], m.tools[-1]
    rise_in(m, "MergePill", "MergeLine", "Pill", 5, 0.5, 1 - 1645 / H)
    text(m, "Url", info["url"], "Montserrat", "Black", 80, None, W / 2, 1645, anchor="centre",
         var_rgb=[T["white"], T["white"], T["orange"]])
    rise_in(m, "MergeUrl", "MergePill", "Url", 5)
    m.output = "MergeUrl"
    m.control("Line", "StyledText", "Line", default=info["line"])
    m.control("Url", "StyledText", "Web address", default=info["url"])
    m.control("Pill", "Width", "Button width", default=1100 if len(info["url"]) > 12 else 920)
    return m


def sticker(T, brand):
    m = Macro("Climb_Sticker")
    canvas(m, ("Climb Orange", "Dark Brown"))
    tw, th = 900, 170
    block(m, "Tag", tw, th, [T["orange"], T["dark_brown"]], [1, 1])
    text(m, "Label", "MAIN STAGE", "Montserrat", "Black", 96, None, tw / 2, th / 2, frame=(tw, th), anchor="centre",
         var_rgb=[T["dark_brown"], T["white"]])
    m.tool("TagLabel", "Merge", {"Background": Link("Tag"), "Foreground": Link("Label")})
    # pop on with the spring curve, cubic-bezier(0.34, 1.56, 0.64, 1), approximated by ease-out back
    p = p_in(0, 10)
    spring = "(1+2.70158*(%s-1)^3+1.70158*(%s-1)^2)" % (p, p)
    m.tool("Pop", "Transform", {"Input": Link("TagLabel"), "Angle": 4,
                                "Size": Expr("(0.6+0.4*%s)*(1-0.04*%s)" % (spring, e_out()), 1)})
    merge(m, "MergeTag", "Canvas", "Pop", center=(0.21094, 0.82176),
          blend=Expr("min(max(time/3,0),1)*(1-%s)" % e_out(), 1))
    m.output = "MergeTag"
    m.control("Label", "StyledText", "Sticker text", default="MAIN STAGE")
    m.control("Tag", "Width", "Sticker width", default=tw)
    m.control("MergeTag", "Center", "Position", default=(0.21094, 0.82176))
    return m


# ----------------------------------------------------------------------------------------------- build

def build(root, brands):
    T = load_tokens(root)
    for brand in brands:
        out = os.path.join(B.OUT, "video", brand, "davinci-resolve")
        d = os.path.join(out, "setting-files")
        if os.path.isdir(d):
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
        os.makedirs(d, exist_ok=True)
        png = os.path.join(root, "logos", brand, "PNG")
        files = {"reversed": "%s_reversed-dark_2048.png" % brand, "mono": "%s_mono-white_2048.png" % brand,
                 "lockup": "%s_tagline-lockup-reversed_2048.png" % brand}
        for f in files.values():
            shutil.copy(os.path.join(png, f), d)
        logo = {k: "Templates:/Edit/Titles/%s/%s" % (brand, f) for k, f in files.items()}
        titles = {
            "%s Lower Third" % brand: lower_third(T, brand),
            "%s Lower Third Festival" % brand: lower_third_festival(T, brand, logo),
            "%s Title Card" % brand: title_card(T, brand),
            "%s End Card" % brand: end_card(T, brand, logo),
            "%s Sticker" % brand: sticker(T, brand),
        }
        for name, m in titles.items():
            m.name = name.replace(" ", "_")
            with open(os.path.join(d, name + ".setting"), "w") as fh:
                fh.write(m.render())
        drfx = os.path.join(out, "%s_Titles.drfx" % brand)
        with zipfile.ZipFile(drfx, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(d)):
                z.write(os.path.join(d, f), "Edit/Titles/%s/%s" % (brand, f))
        print(drfx)


if __name__ == "__main__":
    build(B.REPO, sys.argv[1:] or list(BRANDS))
