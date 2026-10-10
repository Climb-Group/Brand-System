"""Build the Excel templates (.xltx) for each brand: event budget, partner pipeline, run sheet and content calendar.

Each sheet: the brand banner, a title, an Excel table with a Dark Brown header row (White text, 18.65:1), banded rows,
drop-down lists for status columns, formulas for totals and variance, frozen header, and print setup (A4 landscape,
fit to width, header row repeated). A Summary sheet charts the totals in Climb Orange.

python3 excel_build.py [Brand ...]
"""
import os
import sys
import zipfile
from datetime import date, time, timedelta

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

import brand as B
import ooxml_theme as T

ART = os.path.join(B.OUT, "_art")
GBP = '"\u00a3"#,##0;-"\u00a3"#,##0'
GBP_PLAIN = '"\u00a3"#,##0'

HEAD_FILL = PatternFill("solid", fgColor=B.DARK)
HEAD_FONT = Font(name=B.DISPLAY, size=9, bold=True, color=B.WHITE)
BODY_FONT = Font(name=B.BODY, size=10, color=B.SLATE)
TITLE_FONT = Font(name=B.DISPLAY_XB, size=20, color=B.CHARCOAL)
SUB_FONT = Font(name=B.BODY, size=10.5, color=B.SLATE)
EYEBROW_FONT = Font(name=B.BODY, size=9, bold=True, color=B.ORANGE_TEXT)
TOTAL_FONT = Font(name=B.DISPLAY, size=10, bold=True, color=B.CHARCOAL)
THIN = Side(style="thin", color=B.GREY)
TOTAL_TOP = Side(style="medium", color=B.ORANGE)


def banner(ws, b, cols):
    img = XLImage(os.path.join(ART, "xl_banner_%s.png" % b))
    width_px = sum((ws.column_dimensions[get_column_letter(c)].width or 10) * 7.2 for c in range(1, cols + 1))
    img.width = int(width_px)
    img.height = int(width_px / 10)
    ws.add_image(img, "A1")
    ws.row_dimensions[1].height = img.height * 0.75
    return img


def sheet(wb, b, name, eyebrow, title, sub, columns, rows, validations=(), widths=None, totals=None, number_cols=(),
          date_cols=(), time_cols=(), first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = name
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = B.ORANGE
    for i, w in enumerate(widths or [18] * len(columns), 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    banner(ws, b, len(columns))
    ws["A3"], ws["A4"], ws["A5"] = eyebrow.upper(), title.upper(), sub
    ws["A3"].font, ws["A4"].font, ws["A5"].font = EYEBROW_FONT, TITLE_FONT, SUB_FONT
    ws.row_dimensions[4].height = 30
    hr = 7
    for j, c in enumerate(columns, 1):
        cell = ws.cell(hr, j, c)
        cell.fill, cell.font = HEAD_FILL, HEAD_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[hr].height = 26
    for i, row in enumerate(rows, hr + 1):
        for j, v in enumerate(row, 1):
            cell = ws.cell(i, j, v)
            cell.font = BODY_FONT
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if j in number_cols:
                cell.number_format = GBP
            if j in date_cols:
                cell.number_format = "ddd d mmm yyyy"
            if j in time_cols:
                cell.number_format = "hh:mm"
    last = hr + len(rows)
    ref = "A%d:%s%d" % (hr, get_column_letter(len(columns)), last)
    t = Table(displayName=name.replace(" ", ""), ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True, showColumnStripes=False)
    ws.add_table(t)
    for col_letter, options, prompt in validations:
        dv = DataValidation(type="list", formula1='"%s"' % ",".join(options), allow_blank=True,
                            promptTitle="Pick one", prompt=prompt, showInputMessage=True, showErrorMessage=True,
                            errorTitle="Not on the list", error="Pick a value from the list.")
        dv.add("%s%d:%s%d" % (col_letter, hr + 1, col_letter, last + 200))
        ws.add_data_validation(dv)
    if totals:
        tr = last + 2
        ws.cell(tr, 1, "Total").font = TOTAL_FONT
        for col in totals:
            cl = get_column_letter(col)
            c = ws.cell(tr, col, "=SUBTOTAL(109,%s[%s])" % (t.displayName, columns[col - 1]))
            c.font, c.number_format = TOTAL_FONT, GBP
        for col in range(1, len(columns) + 1):
            ws.cell(tr, col).border = Border(top=TOTAL_TOP)
    ws.freeze_panes = "A%d" % (hr + 1)
    ws.print_title_rows = "%d:%d" % (hr, hr)
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.left.text = B.BRANDS[b]["url"]
    ws.oddFooter.right.text = "Page &P of &N"
    ws.oddFooter.left.font = ws.oddFooter.right.font = B.BODY
    return ws, t, hr, last


def summary_chart(ws, title, cats_ref, vals_ref, anchor, y_title="\u00a3"):
    ch = BarChart()
    ch.type = "bar"
    ch.style = 10
    ch.title = title
    ch.y_axis.title = y_title
    ch.legend = None
    ch.add_data(vals_ref, titles_from_data=True)
    ch.set_categories(cats_ref)
    s = ch.series[0]
    s.graphicalProperties.solidFill = B.ORANGE
    s.graphicalProperties.line.solidFill = B.ORANGE
    ch.width, ch.height = 18, 9
    ws.add_chart(ch, anchor)


def budget(wb, b):
    cats = ["Venue and production", "Stage and AV", "Speakers", "Catering", "Marketing", "Print and signage", "Staff and crew",
            "Contingency"]
    rows = []
    for i, c in enumerate(cats):
        r = 8 + i
        rows.append([c, "[Item]", "[Supplier]", 0, 0, "=D%d-E%d" % (r, r), "Planned", ""])
    ws, t, hr, last = sheet(wb, b, "Budget", "Budget", "Event budget",
                            "One line per cost. Variance is budget minus actual: negative means over budget.",
                            ["Category", "Item", "Supplier", "Budget", "Actual", "Variance", "Status", "Notes"], rows,
                            validations=[("G", ["Planned", "Quoted", "Booked", "Invoiced", "Paid"], "Where this cost is up to")],
                            widths=[24, 28, 22, 14, 14, 14, 14, 36], totals=[4, 5, 6], number_cols=(4, 5, 6), first=True)
    ws.conditional_formatting.add("F%d:F%d" % (hr + 1, last + 200),
                                  CellIsRule(operator="lessThan", formula=["0"],
                                             font=Font(color=B.ORANGE_DEEP, bold=True)))
    s = wb.create_sheet("Summary")
    s.sheet_view.showGridLines = False
    for c, w in zip("ABCD", (28, 14, 14, 14)):
        s.column_dimensions[c].width = w
    banner(s, b, 8)
    s["A3"], s["A4"] = "SUMMARY", "BUDGET BY CATEGORY"
    s["A3"].font, s["A4"].font = EYEBROW_FONT, TITLE_FONT
    for j, h in enumerate(("Category", "Budget", "Actual", "Variance"), 1):
        c = s.cell(6, j, h)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    for i, c in enumerate(cats, 7):
        s.cell(i, 1, c).font = BODY_FONT
        for j, col in ((2, "Budget"), (3, "Actual"), (4, "Variance")):
            cell = s.cell(i, j, "=SUMIFS(Budget[%s],Budget[Category],$A%d)" % (col, i))
            cell.number_format, cell.font = GBP, BODY_FONT
    summary_chart(s, "Budget by category", Reference(s, min_col=1, min_row=7, max_row=6 + len(cats)),
                  Reference(s, min_col=2, min_row=6, max_row=6 + len(cats)), "F6")


def pipeline(wb, b):
    stages = ["Lead", "Contacted", "Proposal sent", "Negotiating", "Signed", "Lost"]
    rows = [["[Company]", "[Name]", "[email]", "[Package]", 0, "Lead", "[Owner]", "[Next step]", None] for _ in range(6)]
    ws, t, hr, last = sheet(wb, b, "Pipeline", "Partners", "Partner pipeline",
                            "One row per company. Keep the next step and its date current.",
                            ["Company", "Contact", "Email", "Package", "Value", "Stage", "Owner", "Next step", "Next date"],
                            rows, validations=[("F", stages, "Where this conversation is up to")],
                            widths=[24, 20, 26, 18, 12, 16, 14, 30, 16], totals=[5], number_cols=(5,), date_cols=(9,),
                            first=True)
    ws.conditional_formatting.add("A%d:I%d" % (hr + 1, last + 200),
                                  FormulaRule(formula=['$F%d="Signed"' % (hr + 1)],
                                              fill=PatternFill("solid", fgColor=B.GREY),
                                              font=Font(color=B.CHARCOAL, bold=True)))
    s = wb.create_sheet("Summary")
    s.sheet_view.showGridLines = False
    for c, w in zip("ABC", (22, 12, 14)):
        s.column_dimensions[c].width = w
    banner(s, b, 8)
    s["A3"], s["A4"] = "SUMMARY", "PIPELINE BY STAGE"
    s["A3"].font, s["A4"].font = EYEBROW_FONT, TITLE_FONT
    for j, h in enumerate(("Stage", "Companies", "Value"), 1):
        c = s.cell(6, j, h)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    for i, st in enumerate(stages, 7):
        s.cell(i, 1, st).font = BODY_FONT
        s.cell(i, 2, "=COUNTIFS(Pipeline[Stage],$A%d)" % i).font = BODY_FONT
        c = s.cell(i, 3, "=SUMIFS(Pipeline[Value],Pipeline[Stage],$A%d)" % i)
        c.number_format, c.font = GBP, BODY_FONT
    summary_chart(s, "Value by stage", Reference(s, min_col=1, min_row=7, max_row=6 + len(stages)),
                  Reference(s, min_col=3, min_row=6, max_row=6 + len(stages)), "E6")


def run_sheet(wb, b):
    d = date(2027, 6, 30) if b == "Climb27" else None
    plan = [("09:00", "09:30", "Doors open, coffee and badges", "Foyer"), ("09:30", "10:15", "Opening on the main stage", "Main stage"),
            ("10:30", "11:15", "Roundtables, round one", "Roundtable room"), ("11:30", "12:15", "Workshop", "Studio"),
            ("13:00", "14:00", "Lunch on the expo floor", "Expo"), ("15:00", "16:00", "Investor speed networking", "Lounge"),
            ("18:00", "19:00", "ClimbAwards", "Main stage"), ("19:00", "23:00", "After party", "Main stage")]
    rows = []
    for i, (a, z, what, where) in enumerate(plan):
        r = 8 + i
        h1, m1 = map(int, a.split(":"))
        h2, m2 = map(int, z.split(":"))
        rows.append([d or "[Date]", time(h1, m1), time(h2, m2), "=IF(AND(ISNUMBER(B%d),ISNUMBER(C%d)),C%d-B%d,\"\")" % (r, r, r, r),
                     what, where, "[Name]", "[Owner]", "[Mics, slides, walk-on music]", "Draft"])
    ws, t, hr, last = sheet(wb, b, "Run sheet", "Run sheet", "How the day runs",
                            "One row per moment. Times in 24 hours; duration works itself out.",
                            ["Day", "Start", "End", "Duration", "Session", "Where", "Lead", "Owner", "AV and stage notes", "Status"],
                            rows, validations=[("J", ["Draft", "Confirmed", "Briefed", "Live", "Done"], "Where this session is up to")],
                            widths=[16, 9, 9, 10, 32, 18, 18, 14, 34, 12], date_cols=(1,), time_cols=(2, 3, 4), first=True)
    ws.conditional_formatting.add("J%d:J%d" % (hr + 1, last + 200),
                                  CellIsRule(operator="equal", formula=['"Live"'], fill=PatternFill("solid", fgColor=B.ORANGE),
                                             font=Font(color=B.WHITE, bold=True, size=12)))


def content_calendar(wb, b):
    channels = ["LinkedIn", "Instagram", "TikTok", "X", "Bluesky", "Email", "Website"]
    start = date(2026, 11, 2)
    rows = []
    for i in range(10):
        r = 8 + i
        dd = start + timedelta(days=i * 2)
        rows.append([dd, "=_xlfn.ISOWEEKNUM(A%d)" % r, channels[i % len(channels)], "[Campaign]", "[The one line this post says]",
                     "[Link to the asset]", "[Owner]", "Idea"])
    ws, t, hr, last = sheet(wb, b, "Calendar", "Content", "Content calendar",
                            "One row per post. Write the line in the brand voice; link the asset once it is made.",
                            ["Date", "Week", "Channel", "Campaign", "Message", "Asset", "Owner", "Status"], rows,
                            validations=[("C", channels, "Where it goes out"),
                                         ("H", ["Idea", "Writing", "Design", "Approved", "Scheduled", "Live"], "Where it is up to")],
                            widths=[16, 8, 12, 18, 44, 26, 14, 12], date_cols=(1,), first=True)


BOOKS = {"Event-budget": budget, "Partner-pipeline": pipeline, "Run-sheet": run_sheet, "Content-calendar": content_calendar}


def finish(path, b, template=True):
    """Swap in the brand theme and mark the package as a template."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "xl/theme/theme1.xml":
                data = T.theme_xml(b).encode()
            elif item.filename == "[Content_Types].xml" and template:
                data = data.replace(b"spreadsheetml.sheet.main+xml", b"spreadsheetml.template.main+xml")
            elif item.filename == "[Content_Types].xml":
                data = data.replace(b"spreadsheetml.template.main+xml", b"spreadsheetml.sheet.main+xml")
            zout.writestr(item, data)
    os.replace(tmp, path)


def main():
    brands = sys.argv[1:] or list(B.BRANDS)
    for b in brands:
        d = os.path.join(B.OUT, "office", b, "excel")
        os.makedirs(d, exist_ok=True)
        for name, fn in BOOKS.items():
            for template in (True, False):
                wb = Workbook()
                wb._named_styles["Normal"].font = Font(name=B.BODY, size=10, color=B.SLATE)
                fn(wb, b)
                wb.properties.title = "%s %s" % (b, name.replace("-", " ").lower())
                wb.properties.creator = b
                wb.properties.language = "en-GB"
                if template:
                    wb.template = True
                    p = os.path.join(d, "%s_%s.xltx" % (b, name))
                else:
                    p = os.path.join(B.OUT, "_preview", "%s_%s.xlsx" % (b, name))
                wb.save(p)
                finish(p, b, template)
            print(os.path.join(d, "%s_%s.xltx" % (b, name)))


if __name__ == "__main__":
    main()
