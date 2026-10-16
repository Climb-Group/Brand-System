"""Build the ClimbUK filming and photo release: a fillable A4 PDF that also prints. Every word, label and tooltip is in
release.copy.md (read through release_copy.py).

Usage: python3 build.py [--paid] [--brand-pack PATH]

Builds the free edited-video version, or with --paid the version that sells the
edited video, and writes release-text.md with every word on the form.
Needs: reportlab, pypdf.
"""
import argparse, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject, NameObject,
                           NumberObject, TextStringObject)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import release_copy as C  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--brand-pack", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
ap.add_argument("--paid", action="store_true",
                help="build the version where the edited video is sold for a fee")
ap.add_argument("--out")
args = ap.parse_args()
args.out = args.out or os.path.join(HERE, "ClimbUK_filming-and-photo-release%s.pdf"
                                    % ("_paid-video" if args.paid else ""))
CLAUSES = [(h, b.format(video=C.VIDEO_CLAUSE_PAID if args.paid else C.VIDEO_CLAUSE_FREE))
           for h, b in C.CLAUSES]
BP = args.brand_pack

# Tokens (tokens/brand.tokens.json): preset 1 White for the form, preset 3 Dark Brown header.
DARK_BROWN = HexColor("#1E0F05")
CHARCOAL = HexColor("#242322")
SLATE = HexColor("#4D5B7C")
ORANGE = HexColor("#E8712A")      # large only on white; any size on Dark Brown
ORANGE_TEXT = HexColor("#C55308")  # small orange text on white
TINT = HexColor("#F2AE86")
LIGHT_GREY = HexColor("#E9E9E9")
WHITE = HexColor("#FFFFFF")

for name, f in [("MB", "Montserrat-Bold"), ("MBk", "Montserrat-Black"),
                ("MBkI", "Montserrat-BlackItalic"), ("MXB", "Montserrat-ExtraBold"),
                ("OS", "OpenSans-Regular"), ("OSSB", "OpenSans-SemiBold"),
                ("OSB", "OpenSans-Bold")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(BP, "fonts/ttf", f + ".ttf")))
LOGO = os.path.join(BP, "logos/ClimbUK/PNG/ClimbUK_reversed-dark_1024.png")

W, H = A4
M = 42  # side margin
TMP = args.out + ".tmp"
c = canvas.Canvas(TMP, pagesize=A4)
c.setTitle(C.META_TITLE)
c.setAuthor(C.META_AUTHOR)
c.setSubject(C.META_SUBJECT)
c.setCreator(C.META_CREATOR)
c.setLang("en-GB") if hasattr(c, "setLang") else None
form = c.acroForm
SIG_FIELDS = []  # (page_index, name, rect)


def para(text, x, y_top, width, font="OS", size=9.5, leading=None, color=SLATE):
    st = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading or size * 1.45,
                        textColor=color)
    p = Paragraph(text, st)
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def section(title, y, num):
    c.setStrokeColor(ORANGE); c.setLineWidth(4); c.setLineCap(1)
    c.line(M + 2, y, M + 30, y)
    c.setFillColor(ORANGE_TEXT); c.setFont("MXB", 9)
    c.drawString(M, y - 16, num)
    c.setFillColor(CHARCOAL); c.setFont("MB", 13)
    c.drawString(M + 20, y - 16, title.upper())
    return y - 40


def field(name, label, x, y, w, h=28, hint=None, required=False, tooltip=None):
    c.setFillColor(CHARCOAL); c.setFont("OSSB", 8.5)
    c.drawString(x, y, label)
    if required or hint:
        lw = c.stringWidth(label, "OSSB", 8.5)
        c.setFillColor(SLATE); c.setFont("OS", 8)
        c.drawString(x + lw + 4, y, C.REQUIRED if required else hint)
    fy = y - 5 - h
    form.textfield(name=name, tooltip=tooltip or label, x=x, y=fy, width=w, height=h,
                   borderColor=SLATE, fillColor=WHITE, textColor=CHARCOAL,
                   borderWidth=1, borderStyle="solid", fontName="Helvetica", fontSize=10,
                   forceBorder=True, fieldFlags="required" if required else "")
    return fy - 16


def checkbox(name, label, x, y):
    form.checkbox(name=name, tooltip=label, x=x, y=y - 3, size=13, buttonStyle="check",
                  borderColor=SLATE, fillColor=WHITE, textColor=CHARCOAL, borderWidth=1,
                  forceBorder=True, checked=False)
    c.setFillColor(CHARCOAL); c.setFont("OS", 9.5)
    c.drawString(x + 20, y, label)
    return y - 22


def ascent(x, y, color, alpha):
    """The Ascent motif: rising rungs, drawn as stacked chevrons."""
    c.saveState()
    c.setStrokeColor(Color(color.red, color.green, color.blue, alpha=alpha))
    c.setLineWidth(10); c.setLineCap(1); c.setLineJoin(1)
    for i in range(5):
        cy = y + i * 26
        # One path per chevron: two separate lines overlap at the tip and the
        # doubled transparency shows as a dot.
        pth = c.beginPath(); pth.moveTo(x - 34, cy - 20); pth.lineTo(x, cy); pth.lineTo(x + 34, cy - 20)
        c.drawPath(pth, stroke=1, fill=0)
    c.restoreState()


def header(page_label):
    hh = 148 if page_label == 1 else 70
    c.setFillColor(DARK_BROWN); c.rect(0, H - hh, W, hh, stroke=0, fill=1)
    c.saveState(); pth = c.beginPath(); pth.rect(0, H - hh, W, hh); c.clipPath(pth, stroke=0, fill=0)
    ascent(W - 70, H - hh + 18, ORANGE, 0.22 if page_label == 1 else 0.16)
    c.restoreState()
    logo_h = 22 if page_label == 1 else 16
    c.drawImage(LOGO, M, H - 30 - logo_h, width=logo_h * 1024 / 190, height=logo_h, mask="auto")
    if page_label == 1:
        c.setFillColor(TINT); c.setFont("MB", 9)
        c.drawString(M, H - 76, " ".join(C.EYEBROW))  # tracked eyebrow
        x = M; y = H - 115
        for text, style in C.HEADLINE:
            font = "MBkI" if style == "italic" else "MBk"
            c.setFillColor(ORANGE if style == "orange" else WHITE)
            c.setFont(font, 34); c.drawString(x, y, text)
            x += c.stringWidth(text, font, 34)
        c.setStrokeColor(ORANGE); c.setLineWidth(6); c.setLineCap(1)
        c.line(M + 3, y - 15, M + 60, y - 15)
    else:
        c.setFillColor(TINT); c.setFont("MB", 9)
        c.drawRightString(W - 120, H - 41, " ".join(C.EYEBROW))
    return H - hh


def footer(n):
    c.setStrokeColor(LIGHT_GREY); c.setLineWidth(1); c.line(M, 46, W - M, 46)
    c.setFillColor(SLATE); c.setFont("OS", 7.5)
    para(C.FOOTER, M, 40, W - 2 * M - 70, size=7.5, leading=10)
    c.setFillColor(SLATE); c.setFont("OS", 7.5)
    c.drawRightString(W - M, 31, C.PAGE.replace("{page}", str(n)))


# ---------- Page 1: details ----------
y = header(1) - 26
y = para(C.INTRO, M, y, W - 2 * M - 190, size=10, color=SLATE)
# Summary card on the right
cx, cw, ctop = W - M - 172, 172, H - 148 - 20
def summary(draw):
    sy = ctop - 32
    for line in C.SUMMARY:
        if draw:
            c.setFillColor(ORANGE); c.circle(cx + 17, sy - 6, 2.2, stroke=0, fill=1)
            sy = para(line, cx + 26, sy, cw - 38, size=8.5, color=CHARCOAL) - 5
        else:
            st = ParagraphStyle("m", fontName="OS", fontSize=8.5, leading=8.5 * 1.45)
            sy -= Paragraph(line, st).wrap(cw - 38, 1000)[1] + 5
    return sy
ch = ctop - summary(False) + 10
c.setFillColor(LIGHT_GREY); c.roundRect(cx, ctop - ch, cw, ch, 8, stroke=0, fill=1)
c.setFillColor(CHARCOAL); c.setFont("MXB", 9); c.drawString(cx + 14, ctop - 22, C.SUMMARY_TITLE)
summary(True)
y = min(y, ctop - ch) - 14

y = section(C.DETAILS_TITLE, y, "01")
full = W - 2 * M; half = (full - 16) / 2
y = field("full_name", C.FULL_NAME, M, y, full, required=True)
third = (full - 32) / 3
field("email", C.EMAIL, M, y, third, required=True)
field("phone", C.PHONE, M + third + 16, y, third, hint=C.OPTIONAL)
y = field("event_location", C.EVENT, M + 2 * (third + 16), y, third,
          hint=C.OPTIONAL, tooltip=C.EVENT_TOOLTIP)

y = section(C.HANDLES_TITLE, y + 2, "02")
c.setFillColor(SLATE); c.setFont("OS", 9); c.drawString(M, y + 4, C.HANDLES_NOTE + " " + C.ALL_OPTIONAL)
y -= 18
handles = C.HANDLES
for i, (k, label, hint) in enumerate(handles):
    col = i % 3
    x = M + col * (third + 16)
    ny = field("social_" + k, label, x, y, third, hint="(" + hint + ")",
               tooltip=C.HANDLE_TOOLTIP.replace("{label}", label).replace("{hint}", hint))
    if col == 2 or i == len(handles) - 1:
        y = ny
y = checkbox("tag_consent", C.TAG_CONSENT, M, y - 2)

y = section(C.CHOICES_TITLE, y + 2, "03")
y -= 4
y = checkbox("newsletter", C.NEWSLETTER, M, y)
y = checkbox("affiliate_invite", C.AFFILIATE, M, y)
if args.paid:
    vy = y
    checkbox("edited_video_paid", C.VIDEO_PAID, M, vy)
    px = M + 20 + c.stringWidth(C.VIDEO_PAID, "OS", 9.5) + 6
    c.setFillColor(CHARCOAL); c.setFont("OS", 9.5); c.drawString(px, vy, C.CURRENCY)
    bx = px + c.stringWidth(C.CURRENCY, "OS", 9.5) + 4
    form.textfield(name="edited_video_fee", tooltip=C.FEE_TOOLTIP,
                   x=bx, y=vy - 5, width=60, height=17, borderColor=SLATE, fillColor=WHITE,
                   textColor=CHARCOAL, borderWidth=1, fontName="Helvetica", fontSize=9.5,
                   forceBorder=True)
    c.setFillColor(CHARCOAL); c.setFont("OS", 9.5)
    c.drawString(bx + 66, vy, C.VIDEO_PAID_AFTER)
    y = vy - 22
else:
    y = checkbox("edited_video", C.VIDEO_FREE, M, y)
c.setFillColor(SLATE); c.setFont("OS", 9)
c.drawString(M, y - 4, C.NEXT + " " + C.COPY_NOTE)
footer(1)
c.showPage()

# ---------- Page 2: release and signature ----------
y = header(2) - 24
y = section(C.RELEASE_TITLE, y, "04")
colw = (W - 2 * M - 20) / 2
split = (len(CLAUSES) + 1) // 2
cols = [CLAUSES[:split], CLAUSES[split:]]
bottoms = []
for ci, clauses in enumerate(cols):
    cy = y
    x = M + ci * (colw + 20)
    for j, (head, body) in enumerate(clauses):
        n = ci * split + j + 1
        cy = para("<font name='OSB' color='#242322'>%d. %s.</font> %s" % (n, head, body),
                  x, cy, colw, size=8.5, leading=11.9, color=SLATE) - 7
    bottoms.append(cy)
y = min(bottoms) - 8

y = section(C.SIGN_TITLE, y, "05")
c.setFillColor(SLATE); c.setFont("OS", 9); c.drawString(M, y + 4, C.SIGN_LEAD); y -= 18


def sign_row(prefix, y, required):
    sw = 230
    c.setFillColor(CHARCOAL); c.setFont("OSSB", 8.5); c.drawString(M, y, C.SIGNATURE)
    if required:
        c.setFillColor(SLATE); c.setFont("OS", 8)
        c.drawString(M + c.stringWidth(C.SIGNATURE, "OSSB", 8.5) + 4, y, C.REQUIRED)
    box_h = 40
    c.setStrokeColor(SLATE); c.setLineWidth(1); c.setFillColor(WHITE)
    c.rect(M, y - 5 - box_h, sw, box_h, stroke=1, fill=1)
    c.setStrokeColor(LIGHT_GREY); c.line(M + 10, y - 5 - box_h + 12, M + sw - 10, y - 5 - box_h + 12)
    SIG_FIELDS.append((1, prefix + "signature", (M, y - 5 - box_h, M + sw, y - 5)))
    rx = M + sw + 16; rw = W - M - rx; nw = rw - 110
    field(prefix + "print_name", C.PRINT_NAME, rx, y, nw, required=required)
    field(prefix + "date", C.DATE, rx + nw + 10, y, 100, hint=C.DATE_HINT,
          required=False, tooltip=C.DATE_TOOLTIP)
    return y - 5 - box_h - 16


y = sign_row("", y, True)
c.setFillColor(CHARCOAL); c.setFont("MB", 9.5); c.drawString(M, y, C.GUARDIAN_TITLE.upper()); y -= 16
y = sign_row("guardian_", y, False)
y = field("filmed_by", C.TEAM_LABEL, M, y, (W - 2 * M) / 2, hint=C.TEAM_HINT)
footer(2)
c.showPage()
c.save()

# ---------- Add signature fields (reportlab has no /Sig widget) ----------
r = PdfReader(TMP)
w = PdfWriter(clone_from=r)
acro = w._root_object["/AcroForm"]
for page_i, name, (x0, y0, x1, y1) in SIG_FIELDS:
    page = w.pages[page_i]
    sig = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/FT"): NameObject("/Sig"),
        NameObject("/T"): TextStringObject(name),
        NameObject("/TU"): TextStringObject(C.SIGNATURE if name == "signature"
                                            else C.GUARDIAN_SIGNATURE),
        NameObject("/Rect"): ArrayObject([FloatObject(v) for v in (x0, y0, x1, y1)]),
        NameObject("/F"): NumberObject(4),
        NameObject("/P"): page.indirect_reference,
    })
    ref = w._add_object(sig)
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page["/Annots"].append(ref)
    acro["/Fields"].append(ref)
acro[NameObject("/NeedAppearances")] = __import__("pypdf").generic.BooleanObject(True)
w._root_object[NameObject("/Lang")] = TextStringObject("en-GB")
w._root_object[NameObject("/ViewerPreferences")] = DictionaryObject(
    {NameObject("/DisplayDocTitle"): __import__("pypdf").generic.BooleanObject(True)})
with open(args.out, "wb") as fh:
    w.write(fh)
os.remove(TMP)
print("wrote", args.out)


def write_text(path):
    """Every word on both versions, as Markdown, for review and for e-signature set-up."""
    q = lambda t: t.replace('\\"', '"')
    lines = ["# " + C.TEXT_TITLE, "",
             C.TEXT_LEAD, "",
             "## " + C.TEXT_PAGE_1, "", "**" + C.EYEBROW + "**", "",
             "**" + "".join(t for t, _ in C.HEADLINE) + "**", "", C.INTRO, "",
             "### " + C.SUMMARY_TITLE.capitalize(), ""]
    lines += ["- " + s for s in C.SUMMARY] + ["",
              "### 01 " + C.DETAILS_TITLE, "",
              "- %s %s" % (C.FULL_NAME, C.REQUIRED), "- %s %s" % (C.EMAIL, C.REQUIRED),
              "- %s %s" % (C.PHONE, C.OPTIONAL), "- %s %s" % (C.EVENT, C.OPTIONAL), "",
              "### 02 " + C.HANDLES_TITLE, "", C.HANDLES_NOTE + " " + C.ALL_OPTIONAL, ""]
    lines += ["- %s (%s)" % (label, hint) for _, label, hint in C.HANDLES]
    lines += ["- [ ] " + C.TAG_CONSENT, "",
              "### 03 " + C.CHOICES_TITLE, "",
              "- [ ] " + C.NEWSLETTER, "- [ ] " + C.AFFILIATE,
              "- [ ] " + C.VIDEO_FREE + " " + C.TEXT_FREE,
              "- [ ] %s %s %s. %s %s" % (C.VIDEO_PAID, C.CURRENCY, C.TEXT_AMOUNT, C.VIDEO_PAID_AFTER, C.TEXT_PAID), "",
              C.NEXT + " " + C.COPY_NOTE, "",
              "## " + C.TEXT_PAGE_2, "", "### 04 " + C.RELEASE_TITLE, ""]
    for n, (head, body) in enumerate(C.CLAUSES, 1):
        if "{video}" in body:
            lines.append("%d. **%s.** %s" % (n, head, body.format(video=C.VIDEO_CLAUSE_FREE)))
            lines.append("")
            lines.append("   " + C.TEXT_PAID_INSTEAD + " " + C.VIDEO_CLAUSE_PAID)
        else:
            lines.append("%d. **%s.** %s" % (n, head, body))
        lines.append("")
    lines += ["### 05 " + C.SIGN_TITLE, "", C.SIGN_LEAD, "",
              "- %s %s, %s %s, %s %s" % (C.SIGNATURE, C.REQUIRED, C.PRINT_NAME, C.REQUIRED, C.DATE, C.DATE_HINT), "",
              "**" + C.GUARDIAN_TITLE + "**", "",
              "- %s, %s, %s %s" % (C.SIGNATURE, C.PRINT_NAME, C.DATE, C.DATE_HINT), "",
              "- " + C.TEAM_LABEL + " " + C.TEAM_HINT, "", "---", "", C.FOOTER, ""]
    with open(path, "w") as fh:
        fh.write(q("\n".join(lines)))


write_text(os.path.join(HERE, "release-text.md"))
