"""The Office theme (colours and fonts) shared by the Word, Excel and PowerPoint templates and the .thmx file."""
import brand as B

COLOURS = [  # (slot, hex, name used in Office's colour picker tooltips)
    ("dk1", B.DARK, "Dark Brown"),
    ("lt1", B.WHITE, "White"),
    ("dk2", B.CHARCOAL, "Charcoal"),
    ("lt2", B.GREY, "Light Grey"),
    ("accent1", B.ORANGE, "Climb Orange"),
    ("accent2", B.ORANGE_TEXT, "Orange Text"),
    ("accent3", B.TINT, "Orange Tint"),
    ("accent4", B.ORANGE_DEEP, "Orange Deep"),
    ("accent5", B.SLATE, "Body Slate"),
    ("accent6", B.ORANGE_TEXT_GREY, "Orange Text on Grey"),
]


def clr_scheme(name="ClimbUK", hlink=B.ORANGE_DEEP, fol=B.ORANGE_DEEP):
    out = ['<a:clrScheme name="%s">' % name]
    for slot, hexv, _ in COLOURS:
        if slot in ("dk1", "lt1"):
            out.append('<a:%s><a:srgbClr val="%s"/></a:%s>' % (slot, hexv, slot))
        else:
            out.append('<a:%s><a:srgbClr val="%s"/></a:%s>' % (slot, hexv, slot))
    out.append('<a:hlink><a:srgbClr val="%s"/></a:hlink><a:folHlink><a:srgbClr val="%s"/></a:folHlink>' % (hlink, fol))
    out.append('</a:clrScheme>')
    return "".join(out)


def font_scheme(name="ClimbUK"):
    return ('<a:fontScheme name="%s"><a:majorFont><a:latin typeface="%s"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
            '<a:minorFont><a:latin typeface="%s"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>'
            % (name, B.DISPLAY, B.BODY))


FMT_SCHEME = """<a:fmtScheme name="ClimbUK"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="12700" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln><a:ln w="19050" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln><a:ln w="38100" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:miter lim="800000"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst><a:outerShdw blurRad="152400" dist="38100" dir="5400000" algn="t" rotWithShape="0"><a:srgbClr val="1E0F05"><a:alpha val="18000"/></a:srgbClr></a:outerShdw></a:effectLst></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>"""


def theme_xml(name="ClimbUK", hlink=B.ORANGE_DEEP):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="%s"><a:themeElements>%s%s%s'
            '</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
            % (name, clr_scheme(name, hlink, hlink), font_scheme(name), FMT_SCHEME))
