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
from xl_copy import W
import catalog as K
import copy_io
import excel_books as XB
import xl_copy as XC
from xl import (BODY_FONT, EYEBROW_FONT, GBP, HEAD_FILL, HEAD_FONT, TITLE_FONT, banner, finish, sheet, summary_chart)


def budget(wb, b):
    cats = [
        W("budget.venue-and-production"),
        W("budget.stage-and-av"),
        W("budget.speakers"),
        W("budget.catering"),
        W("budget.marketing"),
        W("budget.print-and-signage"),
        W("budget.staff-and-crew"),
        W("budget.contingency"),
    ]
    rows = []
    for i, c in enumerate(cats):
        r = 8 + i
        rows.append([c, W("budget.item-2"), W("budget.supplier-2"), 0, 0, "=D%d-E%d" % (r, r), W("budget.planned"), ""])
    ws, t, hr, last = sheet(
        wb,
        b,
        "Budget",
        W("budget.budget"),
        W("budget.event-budget"),
        W("budget.one-line-per-cost"),
        [
            W("budget.category"),
            W("budget.item"),
            W("budget.supplier"),
            W("budget.budget"),
            W("budget.actual"),
            W("budget.variance"),
            W("budget.status"),
            W("budget.notes"),
        ],
        rows,
        validations=[
            (
                "G",
                [W("budget.planned"), W("budget.quoted"), W("budget.booked"), W("budget.invoiced"), W("budget.paid")],
                W("budget.where-this-cost-is"),
            )
        ],
        widths=[24, 28, 22, 14, 14, 14, 14, 36],
        totals=[4, 5, 6],
        number_cols=(4, 5, 6),
        first=True,
    )
    ws.conditional_formatting.add("F%d:F%d" % (hr + 1, last + 200),
                                  CellIsRule(operator="lessThan", formula=["0"],
                                             font=Font(color=B.ORANGE_DEEP, bold=True)))
    s = wb.create_sheet("Summary")
    s.sheet_view.showGridLines = False
    for c, w in zip("ABCD", (28, 14, 14, 14)):
        s.column_dimensions[c].width = w
    banner(s, b, 8)
    s["A3"], s["A4"] = W("budget.summary"), W("budget.budget-by-category")
    s["A3"].font, s["A4"].font = EYEBROW_FONT, TITLE_FONT
    for j, h in enumerate((W("budget.category"), W("budget.budget"), W("budget.actual"), W("budget.variance")), 1):
        c = s.cell(6, j, h)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    for i, c in enumerate(cats, 7):
        s.cell(i, 1, c).font = BODY_FONT
        for j, col in ((2, W("budget.budget")), (3, W("budget.actual")), (4, W("budget.variance"))):
            cell = s.cell(i, j, "=SUMIFS(Budget[%s],Budget[Category],$A%d)" % (col, i))
            cell.number_format, cell.font = GBP, BODY_FONT
    summary_chart(s, W("budget.budget-by-category-2"), Reference(s, min_col=1, min_row=7, max_row=6 + len(cats)),
                  Reference(s, min_col=2, min_row=6, max_row=6 + len(cats)), "F6")


def pipeline(wb, b):
    stages = [
        W("pipeline.lead"),
        W("pipeline.contacted"),
        W("pipeline.proposal-sent"),
        W("pipeline.negotiating"),
        W("pipeline.signed"),
        W("pipeline.lost"),
    ]
    rows = [
        [
            W("pipeline.company"),
            W("pipeline.name"),
            W("pipeline.email"),
            W("pipeline.package"),
            0,
            W("pipeline.lead"),
            W("pipeline.owner"),
            W("pipeline.next-step"),
            None,
        ]
        for _ in range(6)
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Pipeline",
        W("pipeline.partners"),
        W("pipeline.partner-pipeline"),
        W("pipeline.one-row-per-company"),
        [
            W("pipeline.company-2"),
            W("pipeline.contact"),
            W("pipeline.email-2"),
            W("pipeline.package-2"),
            W("pipeline.value"),
            W("pipeline.stage"),
            W("pipeline.owner-2"),
            W("pipeline.next-step-2"),
            W("pipeline.next-date"),
        ],
        rows,
        validations=[("F", stages, W("pipeline.where-this-conversation-is"))],
        widths=[24, 20, 26, 18, 12, 16, 14, 30, 16],
        totals=[5],
        number_cols=(5,),
        date_cols=(9,),
        first=True,
    )
    ws.conditional_formatting.add("A%d:I%d" % (hr + 1, last + 200),
                                  FormulaRule(formula=['$F%d="Signed"' % (hr + 1)],
                                              fill=PatternFill("solid", fgColor=B.GREY),
                                              font=Font(color=B.CHARCOAL, bold=True)))
    s = wb.create_sheet("Summary")
    s.sheet_view.showGridLines = False
    for c, w in zip("ABC", (22, 12, 14)):
        s.column_dimensions[c].width = w
    banner(s, b, 8)
    s["A3"], s["A4"] = W("pipeline.summary"), W("pipeline.pipeline-by-stage")
    s["A3"].font, s["A4"].font = EYEBROW_FONT, TITLE_FONT
    for j, h in enumerate((W("pipeline.stage"), W("pipeline.companies"), W("pipeline.value")), 1):
        c = s.cell(6, j, h)
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    for i, st in enumerate(stages, 7):
        s.cell(i, 1, st).font = BODY_FONT
        s.cell(i, 2, "=COUNTIFS(Pipeline[Stage],$A%d)" % i).font = BODY_FONT
        c = s.cell(i, 3, "=SUMIFS(Pipeline[Value],Pipeline[Stage],$A%d)" % i)
        c.number_format, c.font = GBP, BODY_FONT
    summary_chart(s, W("pipeline.value-by-stage"), Reference(s, min_col=1, min_row=7, max_row=6 + len(stages)),
                  Reference(s, min_col=3, min_row=6, max_row=6 + len(stages)), "E6")


def run_sheet(wb, b):
    d = date(2027, 6, 30) if b == "Climb27" else None
    plan = [
        ("09:00", "09:30", W("run-sheet.doors-open-coffee-and"), W("run-sheet.foyer")),
        ("09:30", "10:15", W("run-sheet.opening-on-the-main"), W("run-sheet.main-stage")),
        ("10:30", "11:15", W("run-sheet.roundtables-round-one"), W("run-sheet.roundtable-room")),
        ("11:30", "12:15", W("run-sheet.workshop"), W("run-sheet.studio")),
        ("13:00", "14:00", W("run-sheet.lunch-on-the-expo"), W("run-sheet.expo")),
        ("15:00", "16:00", W("run-sheet.investor-speed-networking"), W("run-sheet.lounge")),
        ("18:00", "19:00", W("run-sheet.climbawards"), W("run-sheet.main-stage")),
        ("19:00", "23:00", W("run-sheet.after-party"), W("run-sheet.main-stage")),
    ]
    rows = []
    for i, (a, z, what, where) in enumerate(plan):
        r = 8 + i
        h1, m1 = map(int, a.split(":"))
        h2, m2 = map(int, z.split(":"))
        rows.append(
            [
                d or W("run-sheet.date"),
                time(h1, m1),
                time(h2, m2),
                "=IF(AND(ISNUMBER(B%d),ISNUMBER(C%d)),C%d-B%d,\"\")" % (r, r, r, r),
                what,
                where,
                W("run-sheet.name"),
                W("run-sheet.owner-2"),
                W("run-sheet.mics-slides-walk-on"),
                W("run-sheet.draft"),
            ]
        )
    ws, t, hr, last = sheet(
        wb,
        b,
        "Run sheet",
        W("run-sheet.run-sheet"),
        W("run-sheet.how-the-day-runs"),
        W("run-sheet.one-row-per-moment"),
        [
            W("run-sheet.day"),
            W("run-sheet.start"),
            W("run-sheet.end"),
            W("run-sheet.duration"),
            W("run-sheet.session"),
            W("run-sheet.where"),
            W("run-sheet.lead"),
            W("run-sheet.owner"),
            W("run-sheet.av-and-stage-notes"),
            W("run-sheet.status"),
        ],
        rows,
        validations=[
            (
                "J",
                [
                    W("run-sheet.draft"),
                    W("run-sheet.confirmed"),
                    W("run-sheet.briefed"),
                    W("run-sheet.live"),
                    W("run-sheet.done"),
                ],
                W("run-sheet.where-this-session-is"),
            )
        ],
        widths=[16, 9, 9, 10, 32, 18, 18, 14, 34, 12],
        date_cols=(1,),
        time_cols=(2, 3, 4),
        first=True,
    )
    ws.conditional_formatting.add("J%d:J%d" % (hr + 1, last + 200),
                                  CellIsRule(operator="equal", formula=['"Live"'], fill=PatternFill("solid", fgColor=B.ORANGE),
                                             font=Font(color=B.WHITE, bold=True, size=12)))


def content_calendar(wb, b):
    channels = [
        W("content-calendar.linkedin"),
        W("content-calendar.instagram"),
        W("content-calendar.tiktok"),
        W("content-calendar.x"),
        W("content-calendar.bluesky"),
        W("content-calendar.email"),
        W("content-calendar.website"),
    ]
    start = date(2026, 11, 2)
    rows = []
    for i in range(10):
        r = 8 + i
        dd = start + timedelta(days=i * 2)
        rows.append(
            [
                dd,
                "=_xlfn.ISOWEEKNUM(A%d)" % r,
                channels[i % len(channels)],
                W("content-calendar.campaign-2"),
                W("content-calendar.the-one-line-this"),
                W("content-calendar.link-to-the-asset"),
                W("content-calendar.owner-2"),
                W("content-calendar.idea"),
            ]
        )
    ws, t, hr, last = sheet(
        wb,
        b,
        "Calendar",
        W("content-calendar.content"),
        W("content-calendar.content-calendar"),
        W("content-calendar.one-row-per-post"),
        [
            W("content-calendar.date"),
            W("content-calendar.week"),
            W("content-calendar.channel"),
            W("content-calendar.campaign"),
            W("content-calendar.message"),
            W("content-calendar.asset"),
            W("content-calendar.owner"),
            W("content-calendar.status"),
        ],
        rows,
        validations=[
            ("C", channels, W("content-calendar.where-it-goes-out")),
            (
                "H",
                [
                    W("content-calendar.idea"),
                    W("content-calendar.writing"),
                    W("content-calendar.design"),
                    W("content-calendar.approved"),
                    W("content-calendar.scheduled"),
                    W("content-calendar.live"),
                ],
                W("content-calendar.where-it-is-up"),
            ),
        ],
        widths=[16, 8, 12, 18, 44, 26, 14, 12],
        date_cols=(1,),
        first=True,
    )


def copy_path(b, row):
    """The copy file with the words of one workbook."""
    return copy_io.path(K.copy_file(b, row))


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
            XC.use(copy_path(b, row))
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
