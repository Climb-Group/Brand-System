"""Build the Excel templates (.xltx) for each brand: the first set (event budget, partner pipeline, run sheet and content
calendar, hand-written below) and every workbook in catalog.py, built by excel_books.py on the helpers in xl.py.

Each sheet: the brand banner, a title, an Excel table with a Dark Brown header row (White text, 18.65:1), banded rows,
drop-down lists for status columns, formulas for totals and variance, frozen header, and print setup (A4 landscape,
fit to width, header row repeated). A Summary sheet charts the totals in Climb Orange.

python3 excel_build.py [Brand ...]          build every template for the brands given (default: all)
python3 excel_build.py --only Invoice ...  build only the named templates
python3 excel_build.py --copy              print every string a reader sees, for check_copy.py
"""
import os
import sys
from datetime import date, time, timedelta

from openpyxl import Workbook
from openpyxl.chart import Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Font, PatternFill

import brand as B
import catalog as K
import excel_books as XB
from xl import (BODY_FONT, EYEBROW_FONT, GBP, HEAD_FILL, HEAD_FONT, TITLE_FONT, banner, finish, sheet, summary_chart)


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


ORIGINAL = {"Event-budget": budget, "Partner-pipeline": pipeline, "Run-sheet": run_sheet, "Content-calendar": content_calendar}


def main():
    args = sys.argv[1:]
    if args[:1] == ["--copy"]:
        print("\n".join(XB.all_copy()))
        return
    only = None
    if args[:1] == ["--only"]:
        only, args = args[1:], []
    brands = args or list(B.BRANDS)
    for b in brands:
        for row in K.rows("excel", b):
            if only and row["name"] not in only:
                continue
            stem = K.stem(b, row)
            d = os.path.join(B.OUT, "office", K.folder(b, row))
            os.makedirs(d, exist_ok=True)
            os.makedirs(os.path.join(B.OUT, "_preview"), exist_ok=True)
            fn = ORIGINAL.get(row["name"]) if row["original"] else XB.BOOKS[row["name"]]
            for template in (True, False):
                wb = Workbook()
                wb._named_styles["Normal"].font = Font(name=B.BODY, size=10, color=B.SLATE)
                fn(wb, b)
                wb.properties.title = "%s %s" % (b, row["title"].lower())
                wb.properties.creator = b
                wb.properties.language = "en-GB"
                if template:
                    wb.template = True
                    p = os.path.join(d, stem + ".xltx")
                else:
                    p = os.path.join(B.OUT, "_preview", stem + ".xlsx")
                wb.save(p)
                finish(p, b, template)
            print(os.path.join(d, stem + ".xltx"))


if __name__ == "__main__":
    main()
