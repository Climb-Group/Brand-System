"""The Excel workbooks added after the first set, built on the helpers in xl.py.

Every workbook: the brand banner, a title block, Dark Brown header rows (White text, 18.65:1), Open Sans body in Body
Slate, drop-down lists where a column has a fixed set of values, formulas for every total, A4 print setup. Money is
GBP; VAT is an editable rate cell (20 percent by default) on every form that charges it. Numbers in the samples are
zero or obvious examples, never real figures.

BOOKS maps the catalogue name to a builder taking (wb, brand).
"""
from datetime import date, timedelta

from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import brand as B
import copy_io as C
from xl_copy import W
from xl import (BODY_FONT, EYEBROW_FONT, GBP, HEAD_FILL, HEAD_FONT, SUB_FONT, THIN, TITLE_FONT, TOTAL_FONT, TOTAL_TOP,
                banner, sheet, summary_chart)

VAT_NUMBER = W("shared.vat-number")
LABEL_FONT = Font(name=B.DISPLAY, size=9, bold=True, color=B.CHARCOAL)
INPUT_FILL = PatternFill("solid", fgColor=B.GREY)
GREY_FILL = PatternFill("solid", fgColor=B.GREY)
TINT_FILL = PatternFill("solid", fgColor=B.TINT)
ORANGE_FILL = PatternFill("solid", fgColor=B.ORANGE)
DARK_FILL = PatternFill("solid", fgColor=B.DARK)
PCT = "0%"
HOURS = "0.00"
DATE = "ddd d mmm yyyy"
SHORT_DATE = "d mmm"
TIME = "hh:mm"
YES_NO = [W("shared.yes"), W("shared.no")]
STATUS = [W("shared.not-started"), W("shared.in-progress"), W("shared.blocked"), W("shared.done")]
LIKELIHOOD = [
    W("shared.1-rare"),
    W("shared.2-unlikely"),
    W("shared.3-possible"),
    W("shared.4-likely"),
    W("shared.5-almost-certain"),
]
SEVERITY = [W("shared.1-minor-injury-or"), W("shared.2-first-aid-required"), W("shared.3-injury-requiring-medical"),
            W("shared.4-serious-injury"), W("shared.5-major-injury-or")]
BAND_FORMULA = 'IF(%s="","",IF(%s>=16,"Critical",IF(%s>=10,"High",IF(%s>=5,"Medium","Low"))))'


def edition(b):
    return b if B.BRANDS[b]["edition"] else W("edition.slot")


# ---------- building blocks ----------

def title_block(ws, b, eyebrow, title, sub, cols, widths=None):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = B.ORANGE
    for i, w in enumerate(widths or [18] * cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    banner(ws, b, cols)
    ws["A3"], ws["A4"], ws["A5"] = eyebrow.upper(), title.upper(), sub
    ws["A3"].font, ws["A4"].font, ws["A5"].font = EYEBROW_FONT, TITLE_FONT, SUB_FONT
    ws.row_dimensions[4].height = 30


def print_setup(ws, b, landscape=True, title_rows=None):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    if title_rows:
        ws.print_title_rows = title_rows
    ws.oddFooter.left.text = B.BRANDS[b]["url"]
    ws.oddFooter.right.text = W("print-setup.page-p-of-n")
    ws.oddFooter.left.font = ws.oddFooter.right.font = B.BODY


def head(ws, row, col, text, height=None):
    c = ws.cell(row, col, text)
    c.fill, c.font = HEAD_FILL, HEAD_FONT
    c.alignment = Alignment(vertical="center", wrap_text=True)
    if height:
        ws.row_dimensions[row].height = height
    return c


def heads(ws, row, texts, col=1, height=26):
    for j, t in enumerate(texts, col):
        head(ws, row, j, t)
    ws.row_dimensions[row].height = height


def body(ws, row, col, value, fmt=None, bold=False, wrap=True, align=None):
    c = ws.cell(row, col, value)
    c.font = TOTAL_FONT if bold else BODY_FONT
    c.alignment = Alignment(vertical="top", wrap_text=wrap, horizontal=align)
    if fmt:
        c.number_format = fmt
    return c


def label(ws, row, col, text):
    c = ws.cell(row, col, text)
    c.font = LABEL_FONT
    c.alignment = Alignment(vertical="top")
    return c


def inp(ws, row, col, value, fmt=None):
    """An input cell people fill in: Light Grey ground so it stands out."""
    c = ws.cell(row, col, value)
    c.font, c.fill = BODY_FONT, INPUT_FILL
    c.alignment = Alignment(vertical="top", wrap_text=True)
    if fmt:
        c.number_format = fmt
    return c


def listv(ws, rng, options, prompt=W("listv.pick-one")):
    dv = DataValidation(
        type="list",
        formula1='"%s"' % ",".join(options),
        allow_blank=True,
        promptTitle=W("listv.pick-one"),
        prompt=prompt,
        showInputMessage=True,
        showErrorMessage=True,
        errorTitle=W("listv.not-on-the-list"),
        error=W("listv.pick-a-value-from"),
    )
    dv.add(rng)
    ws.add_data_validation(dv)


def total_row(ws, row, cols, label_col=1, text=W("total-row.total")):
    ws.cell(row, label_col, text).font = TOTAL_FONT
    for col in cols:
        ws.cell(row, col).font = TOTAL_FONT
    for col in range(1, max(cols) + 1):
        ws.cell(row, col).border = Border(top=TOTAL_TOP)


def band_rules(ws, rng):
    """Risk band colours that pass contrast, with the band always written in the cell too."""
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Low"'], fill=GREY_FILL,
                                                  font=Font(color=B.CHARCOAL, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Medium"'], fill=TINT_FILL,
                                                  font=Font(color=B.DARK, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"High"'], fill=ORANGE_FILL,
                                                  font=Font(color=B.DARK, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Critical"'], fill=DARK_FILL,
                                                  font=Font(color=B.WHITE, bold=True)))


def month_headers(ws, row, col, start_cell, n=12, fmt="mmm yyyy"):
    for k in range(n):
        c = ws.cell(row, col + k, "=%s" % start_cell if k == 0 else "=EDATE(%s%d,1)" % (get_column_letter(col + k - 1), row))
        c.fill, c.font, c.number_format = HEAD_FILL, HEAD_FONT, fmt
        c.alignment = Alignment(horizontal="center", vertical="center")


def line_chart(ws, title, cats, vals, anchor, y_title=""):
    ch = LineChart()
    ch.title = title
    ch.y_axis.title = y_title
    ch.legend = None
    ch.add_data(vals, titles_from_data=True)
    ch.set_categories(cats)
    s = ch.series[0]
    s.graphicalProperties.line.solidFill = B.ORANGE
    s.graphicalProperties.line.width = 28000
    s.smooth = False
    ch.width, ch.height = 18, 8
    ws.add_chart(ch, anchor)


def col_chart(ws, title, cats, vals, anchor, y_title="", stacked=False):
    ch = BarChart()
    ch.type = "col"
    ch.title = title
    ch.y_axis.title = y_title
    ch.add_data(vals, titles_from_data=True)
    ch.set_categories(cats)
    for k, s in enumerate(ch.series):
        colour = [B.ORANGE, B.CHARCOAL, B.TINT, B.SLATE][k % 4]
        s.graphicalProperties.solidFill = colour
        s.graphicalProperties.line.solidFill = colour
    if stacked:
        ch.grouping, ch.overlap = "stacked", 100
    if len(ch.series) == 1:
        ch.legend = None
    ch.width, ch.height = 18, 8
    ws.add_chart(ch, anchor)


# ---------- forms: invoice, quote, purchase order, expense claim ----------

def form(wb, b, kind):
    spec = dict(eyebrow=W("form.eyebrow"), sub=W("form.sub"), number=W("form.number"), dated=W("form.dated"),
                third=W("form.third"), to=W("form.to"), close=W("form.close"))
    ws = wb.active
    title_block(ws, b, spec["eyebrow"], spec["eyebrow"].replace("-", " "), spec["sub"], 6, [30, 12, 16, 16, 4, 22])
    # Who it is from, and the numbers.
    label(ws, 7, 1, W("form.from") if kind != "Purchase-order" else W("form.ordered-by"))
    for k, line in enumerate(
        B.LEGAL.split(". ")[:1]
        + [W("form.address-line-1"), W("form.town-postcode"), C.fill(W("form.vat-number"), number=VAT_NUMBER)]
    ):
        body(ws, 8 + k, 1, line)
    for k, (lab, val, fmt) in enumerate([(spec["number"], "[0001]", None), (spec["dated"], date.today(), "d mmm yyyy"),
                                         (spec["third"], "=D8+14", "d mmm yyyy")]):
        label(ws, 7 + k, 3, lab)
        inp(ws, 7 + k, 4, val, fmt)
    label(ws, 13, 1, spec["to"])
    for k, line in enumerate(
        [W("form.company-name"), W("form.contact-name"), W("form.address-line-1"), W("form.town-postcode")]
    ):
        inp(ws, 14 + k, 1, line)
    label(ws, 13, 3, W("form.reference"))
    inp(ws, 14, 3, W("form.your-reference"))
    ws.merge_cells("C14:D14")
    # Lines.
    hr = 20
    heads(ws, hr, [W("form.description"), W("form.quantity"), W("form.unit-price"), W("form.total")])
    n = 8
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, W("form.item") if i == 0 else "")
        inp(ws, r, 2, 1 if i == 0 else None, "0.##")
        inp(ws, r, 3, 0, GBP)
        body(ws, r, 4, '=IF(AND(ISNUMBER(B%d),ISNUMBER(C%d)),B%d*C%d,"")' % (r, r, r, r), GBP)
        for c in range(1, 5):
            ws.cell(r, c).border = Border(bottom=THIN)
    last = hr + n
    label(ws, last + 2, 3, W("form.subtotal"))
    body(ws, last + 2, 4, "=SUM(D%d:D%d)" % (hr + 1, last), GBP, bold=True)
    label(ws, last + 3, 3, W("form.vat-rate"))
    inp(ws, last + 3, 4, 0.2, PCT)
    label(ws, last + 4, 3, W("form.vat"))
    body(ws, last + 4, 4, "=ROUND(D%d*D%d,2)" % (last + 2, last + 3), GBP, bold=True)
    label(ws, last + 5, 3, W("form.total"))
    body(ws, last + 5, 4, "=D%d+D%d" % (last + 2, last + 4), GBP, bold=True)
    for c in (3, 4):
        ws.cell(last + 5, c).border = Border(top=TOTAL_TOP)
    body(ws, last + 7, 1, spec["close"])
    ws.merge_cells(start_row=last + 7, start_column=1, end_row=last + 7, end_column=4)
    ws.row_dimensions[last + 7].height = 44
    c = body(ws, last + 9, 1, B.LEGAL)
    c.font = Font(name=B.BODY, size=7.5, color=B.SLATE)
    ws.merge_cells(start_row=last + 9, start_column=1, end_row=last + 9, end_column=4)
    ws.row_dimensions[last + 9].height = 30
    ws.print_area = "A1:D%d" % (last + 9)
    print_setup(ws, b, landscape=False)


def invoice(wb, b):
    form(wb, b, "Invoice")


def quote(wb, b):
    form(wb, b, "Quote")


def purchase_order(wb, b):
    form(wb, b, "Purchase-order")


def expense_claim(wb, b):
    ws = wb.active
    title_block(
        ws,
        b,
        W("expense-claim.expenses"),
        W("expense-claim.expense-claim"),
        W("expense-claim.one-line-per-receipt"),
        7,
        [14, 34, 16, 12, 14, 14, 24],
    )
    for k, (lab, val) in enumerate(
        [
            (W("expense-claim.name"), W("expense-claim.name-2")),
            (W("expense-claim.team"), W("expense-claim.team-2")),
            (W("expense-claim.claim-period"), W("expense-claim.month")),
            (W("expense-claim.claim-date"), W("expense-claim.date-2")),
        ]
    ):
        label(ws, 7 + k, 1, lab)
        inp(ws, 7 + k, 2, val)
    label(ws, 7, 4, W("expense-claim.vat-rate"))
    inp(ws, 7, 5, 0.2, PCT)
    hr = 12
    cats = [
        W("expense-claim.travel"),
        W("expense-claim.accommodation"),
        W("expense-claim.meals"),
        W("expense-claim.equipment"),
        W("expense-claim.event-costs"),
        W("expense-claim.other"),
    ]
    heads(
        ws,
        hr,
        [
            W("expense-claim.date"),
            W("expense-claim.description"),
            W("expense-claim.category"),
            W("expense-claim.receipt"),
            W("expense-claim.amount"),
            W("expense-claim.vat-in-the-amount"),
            W("expense-claim.notes"),
        ],
    )
    n = 12
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, None, SHORT_DATE)
        inp(ws, r, 2, W("expense-claim.what-and-why") if i == 0 else "")
        inp(ws, r, 3, cats[0] if i == 0 else "")
        inp(ws, r, 4, W("expense-claim.yes") if i == 0 else "")
        inp(ws, r, 5, 0, GBP)
        body(ws, r, 6, '=IF(ISNUMBER(E%d),ROUND(E%d-E%d/(1+$E$7),2),"")' % (r, r, r), GBP)
        inp(ws, r, 7, "")
    listv(ws, "C%d:C%d" % (hr + 1, hr + n), cats, W("expense-claim.what-kind-of-cost"))
    listv(ws, "D%d:D%d" % (hr + 1, hr + n), YES_NO, W("expense-claim.is-the-receipt-attached"))
    tr = hr + n + 2
    total_row(ws, tr, [5, 6])
    ws.cell(tr, 5, "=SUM(E%d:E%d)" % (hr + 1, hr + n)).number_format = GBP
    ws.cell(tr, 6, "=SUM(F%d:F%d)" % (hr + 1, hr + n)).number_format = GBP
    label(ws, tr + 3, 1, W("expense-claim.claimed-by"))
    inp(ws, tr + 3, 2, W("expense-claim.signature-and-date"))
    label(ws, tr + 4, 1, W("expense-claim.approved-by"))
    inp(ws, tr + 4, 2, W("expense-claim.signature-and-date"))
    print_setup(ws, b, landscape=True, title_rows="%d:%d" % (hr, hr))


# ---------- finance grids ----------

def grid(ws, b, eyebrow, title, sub, sections, start_cell="B7", first_col_width=30):
    """Rows of lines under section headings, 12 months across plus a total column, with a total row per section.
    sections: [(name, [lines]), ...]. Returns {section name: total row}."""
    cols = 15
    title_block(ws, b, eyebrow, title, sub, cols, [first_col_width] + [11] * 13 + [4])
    label(ws, 7, 1, W("grid.first-month"))
    inp(ws, 7, 2, date(date.today().year + 1, 1, 1), "mmm yyyy")
    hr = 9
    head(ws, hr, 1, "")
    month_headers(ws, hr, 2, start_cell)
    head(ws, hr, 14, W("grid.total"))
    ws.row_dimensions[hr].height = 24
    r = hr + 1
    totals = {}
    for name, lines in sections:
        c = ws.cell(r, 1, name)
        c.font = LABEL_FONT
        r += 1
        first = r
        for line in lines:
            inp(ws, r, 1, line)
            for k in range(12):
                inp(ws, r, 2 + k, 0, GBP)
            body(ws, r, 14, "=SUM(B%d:M%d)" % (r, r), GBP)
            r += 1
        for k in range(13):
            col = get_column_letter(2 + k)
            body(ws, r, 2 + k, "=SUM(%s%d:%s%d)" % (col, first, col, r - 1), GBP, bold=True)
        total_row(ws, r, list(range(2, 15)), text=C.fill(W("grid.total-section"), section=name.lower()))
        totals[name] = r
        r += 2
    ws.freeze_panes = "B%d" % (hr + 1)
    print_setup(ws, b, landscape=True, title_rows="%d:%d" % (hr, hr))
    return totals, r


def net_row(ws, r, a, z, text, cols=13, formula="=%s%d-%s%d"):
    ws.cell(r, 1, text).font = LABEL_FONT
    for k in range(cols):
        col = get_column_letter(2 + k)
        body(ws, r, 2 + k, formula % (col, a, col, z), GBP, bold=True)
    for col in range(1, 2 + cols):
        ws.cell(r, col).border = Border(top=TOTAL_TOP, bottom=TOTAL_TOP)


def annual_budget(wb, b):
    ws = wb.active
    totals, r = grid(
        ws,
        b,
        W("annual-budget.budget"),
        W("annual-budget.annual-budget"),
        W("annual-budget.twelve-months-of-income"),
        [
            (
                W("annual-budget.income"),
                [
                    W("annual-budget.tickets"),
                    W("annual-budget.partnerships"),
                    W("annual-budget.exhibitors"),
                    W("annual-budget.other-income"),
                ],
            ),
            (
                W("annual-budget.costs"),
                [
                    W("annual-budget.production"),
                    W("annual-budget.marketing"),
                    W("annual-budget.people"),
                    W("annual-budget.office-and-systems"),
                    W("annual-budget.travel"),
                    W("annual-budget.contingency"),
                ],
            ),
        ],
    )
    net_row(ws, r, totals[W("annual-budget.income")], totals[W("annual-budget.costs")], W("annual-budget.net"))
    s = wb.create_sheet("Summary")
    title_block(s, b, W("annual-budget.summary"), W("annual-budget.income-costs-and-net"), "", 8, [16, 14, 14, 14])
    heads(s, 7, [W("annual-budget.month"), W("annual-budget.income"), W("annual-budget.costs"), W("annual-budget.net")])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "=Budget!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "=Budget!%s%d" % (col, totals[W("annual-budget.income")]), GBP)
        body(s, 8 + k, 3, "=Budget!%s%d" % (col, totals[W("annual-budget.costs")]), GBP)
        body(s, 8 + k, 4, "=B%d-C%d" % (8 + k, 8 + k), GBP)
    col_chart(s, W("annual-budget.income-and-costs-by"), Reference(s, min_col=1, min_row=8, max_row=19),
              Reference(s, min_col=2, max_col=3, min_row=7, max_row=19), "F7", "£")
    print_setup(s, b)


def cash_flow(wb, b):
    ws = wb.active
    totals, r = grid(
        ws,
        b,
        W("cash-flow.cash-flow"),
        W("cash-flow.cash-flow-forecast"),
        W("cash-flow.cash-in-and-out"),
        [
            (
                W("cash-flow.cash-in"),
                [
                    W("cash-flow.ticket-sales"),
                    W("cash-flow.partner-payments"),
                    W("cash-flow.exhibitor-payments"),
                    W("cash-flow.other-receipts"),
                ],
            ),
            (
                W("cash-flow.cash-out"),
                [
                    W("cash-flow.suppliers"),
                    W("cash-flow.payroll"),
                    W("cash-flow.rent-and-systems"),
                    W("cash-flow.marketing"),
                    W("cash-flow.tax-and-vat"),
                    W("cash-flow.other-payments"),
                ],
            ),
        ],
    )
    net_row(ws, r, totals[W("cash-flow.cash-in")], totals[W("cash-flow.cash-out")], W("cash-flow.net-cash-flow"))
    net = r
    label(ws, r + 2, 1, W("cash-flow.opening-balance"))
    inp(ws, r + 2, 2, 0, GBP)
    for k in range(1, 12):
        col, prev = get_column_letter(2 + k), get_column_letter(1 + k)
        body(ws, r + 2, 2 + k, "=%s%d" % (prev, r + 3), GBP)
    ws.cell(r + 3, 1, W("cash-flow.closing-balance")).font = LABEL_FONT
    for k in range(12):
        col = get_column_letter(2 + k)
        body(ws, r + 3, 2 + k, "=%s%d+%s%d" % (col, r + 2, col, net), GBP, bold=True)
    for col in range(1, 14):
        ws.cell(r + 3, col).border = Border(top=TOTAL_TOP, bottom=TOTAL_TOP)
    ws.conditional_formatting.add("B%d:M%d" % (r + 3, r + 3), CellIsRule(operator="lessThan", formula=["0"],
                                                                      font=Font(color=B.ORANGE_DEEP, bold=True)))
    s = wb.create_sheet("Summary")
    title_block(s, b, W("cash-flow.summary"), W("cash-flow.closing-balance-by-month"), "", 8, [16, 16])
    heads(s, 7, [W("cash-flow.month"), W("cash-flow.closing-balance")])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "='Cash flow'!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "='Cash flow'!%s%d" % (col, r + 3), GBP)
    line_chart(s, W("cash-flow.closing-balance"), Reference(s, min_col=1, min_row=8, max_row=19),
               Reference(s, min_col=2, min_row=7, max_row=19), "D7", "£")
    print_setup(s, b)
    ws.title = "Cash flow"


def profit_and_loss(wb, b):
    ws = wb.active
    totals, r = grid(
        ws,
        b,
        W("profit-and-loss.profit-and-loss"),
        W("profit-and-loss.profit-and-loss-tracker"),
        W("profit-and-loss.actuals-by-month-gross"),
        [
            (
                W("profit-and-loss.revenue"),
                [
                    W("profit-and-loss.tickets"),
                    W("profit-and-loss.partnerships"),
                    W("profit-and-loss.exhibitors"),
                    W("profit-and-loss.other-revenue"),
                ],
            ),
            (
                W("profit-and-loss.cost-of-sales"),
                [
                    W("profit-and-loss.production"),
                    W("profit-and-loss.speakers-and-content"),
                    W("profit-and-loss.catering"),
                    W("profit-and-loss.print-and-signage"),
                ],
            ),
            (
                W("profit-and-loss.overheads"),
                [
                    W("profit-and-loss.people"),
                    W("profit-and-loss.marketing"),
                    W("profit-and-loss.office-and-systems"),
                    W("profit-and-loss.professional-fees"),
                    W("profit-and-loss.other-overheads"),
                ],
            ),
        ],
    )
    net_row(
        ws,
        r,
        totals[W("profit-and-loss.revenue")],
        totals[W("profit-and-loss.cost-of-sales")],
        W("profit-and-loss.gross-profit"),
    )
    gp = r
    ws.cell(r + 1, 1, W("profit-and-loss.gross-margin")).font = LABEL_FONT
    for k in range(13):
        col = get_column_letter(2 + k)
        body(
            ws,
            r + 1,
            2 + k,
            '=IF(%s%d=0,"",%s%d/%s%d)'
            % (col, totals[W("profit-and-loss.revenue")], col, gp, col, totals[W("profit-and-loss.revenue")]),
            PCT,
        )
    net_row(ws, r + 3, gp, totals[W("profit-and-loss.overheads")], W("profit-and-loss.net-profit"))
    s = wb.create_sheet("Summary")
    title_block(s, b, W("profit-and-loss.summary"), W("profit-and-loss.revenue-and-net-profit"), "", 8, [16, 14, 14])
    heads(s, 7, [W("profit-and-loss.month"), W("profit-and-loss.revenue"), W("profit-and-loss.net-profit")])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "='Profit and loss'!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "='Profit and loss'!%s%d" % (col, totals[W("profit-and-loss.revenue")]), GBP)
        body(s, 8 + k, 3, "='Profit and loss'!%s%d" % (col, r + 3), GBP)
    col_chart(s, W("profit-and-loss.revenue-and-net-profit-2"), Reference(s, min_col=1, min_row=8, max_row=19),
              Reference(s, min_col=2, max_col=3, min_row=7, max_row=19), "E7", "£")
    print_setup(s, b)
    ws.title = "Profit and loss"


# ---------- dashboards and plans ----------

def kpi_dashboard(wb, b):
    kpis = [
        W("kpi-dashboard.revenue"),
        W("kpi-dashboard.new-customers"),
        W("kpi-dashboard.active-customers"),
        W("kpi-dashboard.website-visits"),
        W("kpi-dashboard.email-subscribers"),
    ]
    start = date(date.today().year, 1, 1)
    rows = []
    for k in range(12):
        m = date(start.year + (start.month + k - 1) // 12, (start.month + k - 1) % 12 + 1, 1)
        rows.append([m, 0, 0, 0, 0, 0])
    inputs, t, hr, last = sheet(
        wb,
        b,
        "Inputs",
        W("kpi-dashboard.kpis"),
        W("kpi-dashboard.kpi-inputs"),
        W("kpi-dashboard.one-row-per-month"),
        [W("kpi-dashboard.month")] + kpis,
        rows,
        widths=[14, 14, 14, 14, 14, 16],
        number_cols=(2,),
        first=True,
    )
    for i in range(hr + 1, last + 1):
        inputs.cell(i, 1).number_format = "mmm yyyy"
    d = wb.create_sheet("Dashboard", 0)
    title_block(
        d,
        b,
        W("kpi-dashboard.dashboard"),
        W("kpi-dashboard.kpi-dashboard"),
        W("kpi-dashboard.the-latest-month-against"),
        10,
        [22, 14, 14, 14, 3, 14, 14, 14, 14, 14],
    )
    heads(
        d,
        7,
        [W("kpi-dashboard.kpi"), W("kpi-dashboard.latest"), W("kpi-dashboard.previous"), W("kpi-dashboard.change")],
    )
    n = W("kpi-dashboard.count-inputs-month")
    for k, kpi in enumerate(kpis):
        r = 8 + k
        body(d, r, 1, kpi, bold=True)
        fmt = GBP if kpi == W("kpi-dashboard.revenue") else "#,##0"
        body(d, r, 2, "=IFERROR(INDEX(Inputs[%s],%s),0)" % (kpi, n), fmt, bold=True)
        body(d, r, 3, "=IFERROR(INDEX(Inputs[%s],%s-1),0)" % (kpi, n), fmt)
        body(d, r, 4, '=IF(C%d=0,"",B%d/C%d-1)' % (r, r, r), PCT)
    d.conditional_formatting.add("D8:D12", CellIsRule(operator="lessThan", formula=["0"],
                                                      font=Font(color=B.ORANGE_DEEP, bold=True)))
    cats = Reference(inputs, min_col=1, min_row=hr + 1, max_row=last)
    line_chart(
        d, W("kpi-dashboard.revenue-by-month"), cats, Reference(inputs, min_col=2, min_row=hr, max_row=last), "F7", "£"
    )
    col_chart(
        d,
        W("kpi-dashboard.new-customers-by-month"),
        cats,
        Reference(inputs, min_col=3, min_row=hr, max_row=last),
        "F24",
    )
    print_setup(d, b)


def project_plan(wb, b):
    ws = wb.active
    weeks = 16
    cols = 7 + weeks
    title_block(
        ws,
        b,
        W("project-plan.plan"),
        W("project-plan.project-plan"),
        W("project-plan.one-row-per-task"),
        cols,
        [5, 30, 14, 12, 12, 7, 13] + [4.2] * weeks,
    )
    label(ws, 7, 1, W("project-plan.plan-start"))
    ws.merge_cells("A7:B7")
    inp(ws, 7, 3, date.today(), DATE)
    hr = 9
    heads(
        ws,
        hr,
        [
            W("project-plan.id"),
            W("project-plan.task"),
            W("project-plan.owner"),
            W("project-plan.start"),
            W("project-plan.end"),
            W("project-plan.days"),
            W("project-plan.status"),
        ],
        height=30,
    )
    for k in range(weeks):
        c = ws.cell(hr, 8 + k, "=$C$7+%d" % (7 * k))
        c.fill, c.font, c.number_format = HEAD_FILL, HEAD_FONT, "d mmm"
        c.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90)
    ws.row_dimensions[hr].height = 48
    tasks = [
        (W("project-plan.kick-off"), 0, 0),
        (W("project-plan.brief-agreed"), 1, 5),
        (W("project-plan.first-version"), 6, 20),
        (W("project-plan.feedback"), 21, 27),
        (W("project-plan.final-version"), 28, 41),
        (W("project-plan.launch"), 42, 42),
    ]
    n = 14
    for i in range(n):
        r = hr + 1 + i
        task = tasks[i] if i < len(tasks) else ("", None, None)
        body(ws, r, 1, i + 1)
        inp(ws, r, 2, task[0])
        inp(ws, r, 3, W("project-plan.name") if task[0] else "")
        inp(ws, r, 4, "=$C$7+%d" % task[1] if task[1] is not None else None, SHORT_DATE)
        inp(ws, r, 5, "=$C$7+%d" % task[2] if task[2] is not None else None, SHORT_DATE)
        body(ws, r, 6, '=IF(AND(ISNUMBER(D%d),ISNUMBER(E%d)),E%d-D%d+1,"")' % (r, r, r, r))
        inp(ws, r, 7, W("project-plan.not-started") if task[0] else "")
        for k in range(weeks):
            c = ws.cell(r, 8 + k)
            c.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    listv(ws, "G%d:G%d" % (hr + 1, hr + n), STATUS, W("project-plan.where-the-task-is"))
    grid_rng = "%s%d:%s%d" % ("H", hr + 1, get_column_letter(7 + weeks), hr + n)
    ws.conditional_formatting.add(grid_rng, FormulaRule(
        formula=['AND(ISNUMBER($D%d),ISNUMBER($E%d),H$%d<=$E%d,H$%d+6>=$D%d)' % (hr + 1, hr + 1, hr, hr + 1, hr, hr + 1)],
        fill=ORANGE_FILL))
    ws.conditional_formatting.add(grid_rng, FormulaRule(
        formula=['AND($G%d="Done",ISNUMBER($D%d),H$%d<=$E%d,H$%d+6>=$D%d)' % (hr + 1, hr + 1, hr, hr + 1, hr, hr + 1)],
        fill=DARK_FILL, stopIfTrue=True))
    ws.freeze_panes = "H%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))


def task_tracker(wb, b):
    rows = [
        [
            i + 1,
            W("task-tracker.task-2") if i == 0 else "",
            W("task-tracker.name") if i == 0 else "",
            W("task-tracker.medium") if i == 0 else "",
            None,
            W("task-tracker.not-started") if i == 0 else "",
            "",
        ]
        for i in range(10)
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Tasks",
        W("task-tracker.actions"),
        W("task-tracker.task-and-action-tracker"),
        W("task-tracker.one-row-per-action"),
        [
            "ID",
            W("task-tracker.task"),
            W("task-tracker.owner"),
            W("task-tracker.priority"),
            W("task-tracker.due"),
            W("task-tracker.status"),
            W("task-tracker.notes"),
        ],
        rows,
        validations=[
            (
                "D",
                [W("task-tracker.high"), W("task-tracker.medium"), W("task-tracker.low")],
                W("task-tracker.how-urgent"),
            ),
            ("F", STATUS, W("task-tracker.where-it-is-up")),
        ],
        widths=[6, 40, 16, 12, 14, 14, 36],
        date_cols=(5,),
        first=True,
    )
    ws.conditional_formatting.add("A%d:G%d" % (hr + 1, last + 200), FormulaRule(
        formula=['AND(ISNUMBER($E%d),$E%d<TODAY(),$F%d<>"Done")' % (hr + 1, hr + 1, hr + 1)],
        font=Font(color=B.ORANGE_DEEP, bold=True)))
    ws.conditional_formatting.add("A%d:G%d" % (hr + 1, last + 200), FormulaRule(
        formula=['$F%d="Done"' % (hr + 1)], fill=GREY_FILL))


def risk_register(wb, b):
    rows = []
    for i in range(8):
        r = 8 + i
        rows.append(
            [
                i + 1,
                W("risk-register.risk-2") if i == 0 else "",
                W("risk-register.delivery") if i == 0 else "",
                W("risk-register.name") if i == 0 else "",
                3 if i == 0 else None,
                3 if i == 0 else None,
                '=IF(AND(ISNUMBER(E%d),ISNUMBER(F%d)),E%d*F%d,"")' % (r, r, r, r),
                "=" + BAND_FORMULA % (("G%d" % r,) * 4),
                W("risk-register.what-is-in-place") if i == 0 else "",
                W("risk-register.what-we-will-do") if i == 0 else "",
                W("risk-register.open") if i == 0 else "",
                None,
            ]
        )
    ws, t, hr, last = sheet(
        wb,
        b,
        "Risks",
        W("risk-register.risks"),
        W("risk-register.risk-register"),
        W("risk-register.score-likelihood-and-impact"),
        [
            W("risk-register.id"),
            W("risk-register.risk"),
            W("risk-register.category"),
            W("risk-register.owner"),
            W("risk-register.likelihood"),
            W("risk-register.impact"),
            W("risk-register.score"),
            W("risk-register.band"),
            W("risk-register.controls-in-place"),
            W("risk-register.action"),
            W("risk-register.status"),
            W("risk-register.review-date"),
        ],
        rows,
        validations=[
            (
                "C",
                [
                    W("risk-register.delivery"),
                    W("risk-register.finance"),
                    W("risk-register.people"),
                    W("risk-register.legal"),
                    W("risk-register.reputation"),
                    W("risk-register.safety"),
                    W("risk-register.technology"),
                ],
                W("risk-register.what-kind-of-risk"),
            ),
            ("E", ["1", "2", "3", "4", "5"], W("risk-register.1-rare-to-5")),
            ("F", ["1", "2", "3", "4", "5"], W("risk-register.1-minor-to-5")),
            (
                "K",
                [W("risk-register.open"), W("risk-register.monitoring"), W("risk-register.closed")],
                W("risk-register.where-it-is-up"),
            ),
        ],
        widths=[6, 34, 14, 14, 11, 9, 8, 10, 32, 32, 12, 14],
        date_cols=(12,),
        first=True,
    )
    band_rules(ws, "H%d:H%d" % (hr + 1, last + 200))


def contact_list(wb, b):
    types = [
        W("contact-list.partner"),
        W("contact-list.exhibitor"),
        W("contact-list.speaker"),
        W("contact-list.supplier"),
        W("contact-list.press"),
        W("contact-list.investor"),
        W("contact-list.public-sector"),
        W("contact-list.other"),
    ]
    rows = [
        [
            W("contact-list.name"),
            W("contact-list.role"),
            W("contact-list.organisation"),
            types[0],
            W("contact-list.email"),
            W("contact-list.phone"),
            W("contact-list.owner"),
            None,
            "",
        ]
        for _ in range(8)
    ]
    sheet(
        wb,
        b,
        "Contacts",
        W("contact-list.contacts"),
        W("contact-list.contact-and-stakeholder-list"),
        W("contact-list.one-row-per-person"),
        [
            W("contact-list.name-2"),
            W("contact-list.role-2"),
            W("contact-list.organisation-2"),
            W("contact-list.type"),
            W("contact-list.email-2"),
            W("contact-list.phone-2"),
            W("contact-list.relationship-owner"),
            W("contact-list.last-contact"),
            W("contact-list.notes"),
        ],
        rows,
        validations=[("D", types, W("contact-list.who-they-are-to"))],
        widths=[20, 18, 22, 14, 26, 16, 18, 14, 34],
        date_cols=(8,),
        first=True,
    )


def supplier_register(wb, b):
    rows = [
        [
            W("supplier-register.supplier"),
            W("supplier-register.service"),
            W("supplier-register.name"),
            W("supplier-register.email"),
            W("supplier-register.phone"),
            None,
            None,
            0,
            None,
            W("supplier-register.active"),
        ]
        for _ in range(8)
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Suppliers",
        W("supplier-register.suppliers"),
        W("supplier-register.supplier-register"),
        W("supplier-register.one-row-per-supplier"),
        [
            W("supplier-register.supplier-2"),
            W("supplier-register.service-2"),
            W("supplier-register.contact"),
            W("supplier-register.email-2"),
            W("supplier-register.phone-2"),
            W("supplier-register.contract-start"),
            W("supplier-register.contract-end"),
            W("supplier-register.annual-value"),
            W("supplier-register.insurance-expiry"),
            W("supplier-register.status"),
        ],
        rows,
        validations=[
            (
                "J",
                [W("supplier-register.active"), W("supplier-register.under-review"), W("supplier-register.ended")],
                W("supplier-register.where-the-relationship-is"),
            )
        ],
        widths=[22, 20, 18, 26, 16, 14, 14, 14, 14, 14],
        totals=[8],
        number_cols=(8,),
        date_cols=(6, 7, 9),
        first=True,
    )
    for col in ("G", "I"):
        ws.conditional_formatting.add("%s%d:%s%d" % (col, hr + 1, col, last + 200), FormulaRule(
            formula=['AND(ISNUMBER(%s%d),%s%d<TODAY())' % (col, hr + 1, col, hr + 1)],
            font=Font(color=B.ORANGE_DEEP, bold=True)))


def asset_register(wb, b):
    rows = [
        [
            W("asset-register.tag"),
            W("asset-register.asset"),
            W("asset-register.laptop"),
            W("asset-register.location"),
            W("asset-register.name"),
            None,
            0,
            W("asset-register.supplier"),
            W("asset-register.serial"),
            W("asset-register.good"),
            W("asset-register.in-use"),
        ]
        for _ in range(8)
    ]
    sheet(
        wb,
        b,
        "Assets",
        W("asset-register.assets"),
        W("asset-register.asset-and-inventory-register"),
        W("asset-register.one-row-per-item"),
        [
            W("asset-register.asset-tag"),
            W("asset-register.asset-2"),
            W("asset-register.category"),
            W("asset-register.location-2"),
            W("asset-register.assigned-to"),
            W("asset-register.purchase-date"),
            W("asset-register.cost"),
            W("asset-register.supplier-2"),
            W("asset-register.serial-number"),
            W("asset-register.condition"),
            W("asset-register.status"),
        ],
        rows,
        validations=[
            (
                "C",
                [
                    W("asset-register.laptop"),
                    W("asset-register.phone"),
                    W("asset-register.screen"),
                    W("asset-register.av"),
                    W("asset-register.furniture"),
                    W("asset-register.signage"),
                    W("asset-register.stock"),
                    W("asset-register.other"),
                ],
                W("asset-register.what-kind-of-asset"),
            ),
            (
                "J",
                [
                    W("asset-register.new"),
                    W("asset-register.good"),
                    W("asset-register.worn"),
                    W("asset-register.faulty"),
                ],
                W("asset-register.its-condition"),
            ),
            (
                "K",
                [
                    W("asset-register.in-use"),
                    W("asset-register.in-store"),
                    W("asset-register.on-loan"),
                    W("asset-register.disposed"),
                ],
                W("asset-register.where-it-is"),
            ),
        ],
        widths=[10, 24, 12, 16, 16, 14, 12, 18, 18, 12, 12],
        totals=[7],
        number_cols=(7,),
        date_cols=(6,),
        first=True,
    )


def timesheet(wb, b):
    ws = wb.active
    title_block(
        ws,
        b,
        W("timesheet.timesheet"),
        W("timesheet.weekly-timesheet"),
        W("timesheet.times-in-24-hours"),
        8,
        [12, 14, 9, 9, 9, 9, 22, 30],
    )
    label(ws, 7, 1, W("timesheet.name"))
    inp(ws, 7, 2, W("timesheet.name-2"))
    label(ws, 8, 1, W("timesheet.week-starting"))
    inp(ws, 8, 2, date.today() - timedelta(days=date.today().weekday()), DATE)
    hr = 10
    heads(
        ws,
        hr,
        [
            W("timesheet.day"),
            W("timesheet.date"),
            W("timesheet.start"),
            W("timesheet.end"),
            W("timesheet.break-min"),
            W("timesheet.hours"),
            W("timesheet.project"),
            W("timesheet.notes"),
        ],
    )
    days = [
        W("timesheet.monday"),
        W("timesheet.tuesday"),
        W("timesheet.wednesday"),
        W("timesheet.thursday"),
        W("timesheet.friday"),
        W("timesheet.saturday"),
        W("timesheet.sunday"),
    ]
    for i, day in enumerate(days):
        r = hr + 1 + i
        body(ws, r, 1, day, bold=True)
        body(ws, r, 2, "=$B$8+%d" % i, SHORT_DATE)
        inp(ws, r, 3, None, TIME)
        inp(ws, r, 4, None, TIME)
        inp(ws, r, 5, 0)
        body(ws, r, 6, '=IF(AND(ISNUMBER(C%d),ISNUMBER(D%d)),ROUND((D%d-C%d)*24-E%d/60,2),"")' % (r, r, r, r, r), HOURS)
        inp(ws, r, 7, "")
        inp(ws, r, 8, "")
    tr = hr + 9
    total_row(ws, tr, [6], text=W("timesheet.total-hours"))
    ws.cell(tr, 6, "=SUM(F%d:F%d)" % (hr + 1, hr + 7)).number_format = HOURS
    label(ws, tr + 2, 1, W("timesheet.signed"))
    inp(ws, tr + 2, 2, W("timesheet.signature-and-date"))
    label(ws, tr + 3, 1, W("timesheet.approved"))
    inp(ws, tr + 3, 2, W("timesheet.signature-and-date"))
    print_setup(ws, b)


def leave_planner(wb, b):
    ws = wb.active
    days = 31
    cols = 2 + days + 4
    title_block(
        ws,
        b,
        W("leave-planner.leave"),
        W("leave-planner.holiday-and-leave-planner"),
        W("leave-planner.one-row-per-person"),
        cols,
        [20, 10] + [3.6] * days + [9, 9, 9, 10],
    )
    label(ws, 7, 1, W("leave-planner.month"))
    inp(ws, 7, 2, date(date.today().year, date.today().month, 1), "mmm yyyy")
    label(ws, 7, 4, W("leave-planner.codes"))
    ws.merge_cells(start_row=7, start_column=5, end_row=7, end_column=20)
    body(ws, 7, 5, W("leave-planner.h-holiday-s-sick"), wrap=False)
    hr = 9
    head(ws, hr, 1, W("leave-planner.name"))
    head(ws, hr, 2, W("leave-planner.allowance"))
    for k in range(days):
        c = ws.cell(hr, 3 + k, '=IF(DAY($B$7+%d)=%d,$B$7+%d,"")' % (k, k + 1, k))
        c.fill, c.font, c.number_format = HEAD_FILL, HEAD_FONT, "d"
        c.alignment = Alignment(horizontal="center", vertical="center")
    for j, h in enumerate(
        [
            W("leave-planner.holiday"),
            W("leave-planner.sick"),
            W("leave-planner.training"),
            W("leave-planner.holiday-left"),
        ]
    ):
        head(ws, hr, 3 + days + j, h)
    ws.row_dimensions[hr].height = 30
    codes = ["H", "S", "T", "W", "B"]
    n = 12
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, W("leave-planner.name-2") if i == 0 else "")
        inp(ws, r, 2, 25 if i == 0 else None)
        for k in range(days):
            c = ws.cell(r, 3 + k)
            c.font = BODY_FONT
            c.alignment = Alignment(horizontal="center")
            c.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
        first, last_col = "C", get_column_letter(2 + days)
        for j, code in enumerate(["H", "S", "T"]):
            body(ws, r, 3 + days + j, '=COUNTIF(%s%d:%s%d,"%s")' % (first, r, last_col, r, code), align="center")
        body(ws, r, 3 + days + 3, '=IF(ISNUMBER(B%d),B%d-%s%d,"")' % (r, r, get_column_letter(3 + days), r), align="center")
    rng = "C%d:%s%d" % (hr + 1, get_column_letter(2 + days), hr + n)
    listv(ws, rng, codes, W("leave-planner.h-s-t-w"))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"H"'], fill=ORANGE_FILL,
                                                  font=Font(color=B.DARK, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"S"'], fill=DARK_FILL,
                                                  font=Font(color=B.WHITE, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"T"'], fill=TINT_FILL,
                                                  font=Font(color=B.DARK, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"B"'], fill=GREY_FILL,
                                                  font=Font(color=B.CHARCOAL, bold=True)))
    # Weekends in grey.
    ws.conditional_formatting.add(rng, FormulaRule(formula=['AND(C$%d<>"",WEEKDAY(C$%d,2)>5)' % (hr, hr)], fill=GREY_FILL))
    ws.freeze_panes = "C%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))


def recruitment_tracker(wb, b):
    stages = [
        W("recruitment-tracker.applied"),
        W("recruitment-tracker.screen"),
        W("recruitment-tracker.interview-1"),
        W("recruitment-tracker.interview-2"),
        W("recruitment-tracker.offer"),
        W("recruitment-tracker.hired"),
        W("recruitment-tracker.declined"),
    ]
    rows = [
        [
            W("recruitment-tracker.role"),
            W("recruitment-tracker.candidate"),
            W("recruitment-tracker.where-they-came-from"),
            stages[0],
            None,
            W("recruitment-tracker.next-step"),
            None,
            W("recruitment-tracker.owner"),
            "",
        ]
        for _ in range(8)
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Candidates",
        W("recruitment-tracker.hiring"),
        W("recruitment-tracker.recruitment-tracker"),
        W("recruitment-tracker.one-row-per-candidate"),
        [
            W("recruitment-tracker.role-2"),
            W("recruitment-tracker.candidate-2"),
            W("recruitment-tracker.source"),
            W("recruitment-tracker.stage"),
            W("recruitment-tracker.applied"),
            W("recruitment-tracker.next-step-2"),
            W("recruitment-tracker.next-date"),
            W("recruitment-tracker.owner-2"),
            W("recruitment-tracker.notes"),
        ],
        rows,
        validations=[("D", stages, W("recruitment-tracker.where-they-are-in"))],
        widths=[20, 20, 18, 14, 14, 26, 14, 14, 30],
        date_cols=(5, 7),
        first=True,
    )
    s = wb.create_sheet("Summary")
    title_block(s, b, W("recruitment-tracker.summary"), W("recruitment-tracker.candidates-by-stage"), "", 8, [16, 12])
    heads(s, 7, [W("recruitment-tracker.stage"), W("recruitment-tracker.candidates")])
    for i, st in enumerate(stages, 8):
        body(s, i, 1, st)
        body(s, i, 2, "=COUNTIFS(Candidates[Stage],$A%d)" % i)
    col_chart(
        s,
        W("recruitment-tracker.candidates-by-stage"),
        Reference(s, min_col=1, min_row=8, max_row=7 + len(stages)),
        Reference(s, min_col=2, min_row=7, max_row=7 + len(stages)),
        "D7",
    )
    print_setup(s, b)


# ---------- events ----------

def speaker_tracker(wb, b):
    d = date(2027, 6, 30) if b == "Climb27" else None
    sess = [
        [
            d or W("speaker-tracker.day-2"),
            W("speaker-tracker.main-stage"),
            W("speaker-tracker.time"),
            W("speaker-tracker.session-title"),
            W("speaker-tracker.panel"),
            W("speaker-tracker.host"),
            W("speaker-tracker.speakers-2"),
            W("speaker-tracker.invited"),
        ]
        for _ in range(6)
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Sessions",
        W("speaker-tracker.agenda"),
        W("speaker-tracker.sessions"),
        W("speaker-tracker.one-row-per-session"),
        [
            W("speaker-tracker.day"),
            W("speaker-tracker.stage"),
            W("speaker-tracker.time-2"),
            W("speaker-tracker.title"),
            W("speaker-tracker.format"),
            W("speaker-tracker.host-2"),
            W("speaker-tracker.speakers"),
            W("speaker-tracker.status"),
        ],
        sess,
        validations=[
            (
                "E",
                [
                    W("speaker-tracker.talk"),
                    W("speaker-tracker.panel"),
                    W("speaker-tracker.fireside-chat"),
                    W("speaker-tracker.roundtable"),
                    W("speaker-tracker.workshop"),
                    W("speaker-tracker.pitch"),
                ],
                W("speaker-tracker.the-session-format"),
            ),
            (
                "H",
                [
                    W("speaker-tracker.invited"),
                    W("speaker-tracker.confirmed"),
                    W("speaker-tracker.briefed"),
                    W("speaker-tracker.live"),
                    W("speaker-tracker.done"),
                ],
                W("speaker-tracker.where-it-is-up"),
            ),
        ],
        widths=[14, 16, 10, 36, 14, 18, 32, 12],
        date_cols=(1,),
        first=True,
    )
    yes = [W("speaker-tracker.no")] * 7
    sp = [
        [
            W("speaker-tracker.name-2"),
            W("speaker-tracker.company-2"),
            W("speaker-tracker.role-2"),
            W("speaker-tracker.session-title"),
        ]
        + yes
        for _ in range(8)
    ]
    cols = [
        W("speaker-tracker.name"),
        W("speaker-tracker.company"),
        W("speaker-tracker.role"),
        W("speaker-tracker.session"),
        W("speaker-tracker.bio-received"),
        W("speaker-tracker.photo-received"),
        W("speaker-tracker.slides-received"),
        W("speaker-tracker.contract-signed"),
        W("speaker-tracker.travel-needed"),
        W("speaker-tracker.mobile-captured"),
        W("speaker-tracker.checked-in"),
    ]
    ws2, t2, hr2, last2 = sheet(
        wb,
        b,
        "Speakers",
        W("speaker-tracker.speakers"),
        W("speaker-tracker.speakers"),
        W("speaker-tracker.one-row-per-speaker"),
        cols,
        sp,
        validations=[(get_column_letter(c), YES_NO, W("speaker-tracker.yes-or-no")) for c in range(5, 12)],
        widths=[20, 20, 18, 30, 10, 10, 10, 10, 10, 10, 10],
    )
    ws2.conditional_formatting.add("E%d:K%d" % (hr2 + 1, last2 + 200), CellIsRule(operator="equal", formula=['"Yes"'],
                                                                             fill=GREY_FILL, font=Font(color=B.CHARCOAL, bold=True)))


def critical_path(wb, b):
    streams = [
        W("critical-path.site"),
        W("critical-path.agenda"),
        W("critical-path.partners"),
        W("critical-path.exhibitors"),
        W("critical-path.marketing"),
        W("critical-path.ticketing"),
        W("critical-path.production"),
        W("critical-path.staffing"),
        W("critical-path.health-and-safety"),
    ]
    ws = wb.active
    cols = 2 + len(streams)
    title_block(
        ws,
        b,
        W("critical-path.critical-path"),
        W("critical-path.production-critical-path"),
        W("critical-path.weeks-to-the-event"),
        cols,
        [10, 12] + [20] * len(streams),
    )
    label(ws, 7, 1, W("critical-path.event-date"))
    ws.merge_cells("A7:A7")
    ev = date(2027, 6, 30) if b == "Climb27" else date.today() + timedelta(days=182)
    inp(ws, 7, 2, ev, DATE)
    hr = 9
    heads(ws, hr, [W("critical-path.weeks-to-go"), W("critical-path.week-of")] + streams, height=30)
    samples = {
        (26, W("critical-path.site")): W("critical-path.site-confirmed-and-contract"),
        (26, W("critical-path.agenda")): W("critical-path.theme-and-formats-agreed"),
        (26, W("critical-path.ticketing")): W("critical-path.first-release-on-sale"),
        (26, W("critical-path.marketing")): W("critical-path.launch-campaign-live"),
        (20, W("critical-path.partners")): W("critical-path.partner-prospectus-out"),
        (20, W("critical-path.agenda")): W("critical-path.speaker-invitations-out"),
        (16, W("critical-path.exhibitors")): W("critical-path.exhibitor-sales-open"),
        (16, W("critical-path.production")): W("critical-path.stage-and-av-quotes"),
        (12, W("critical-path.agenda")): W("critical-path.agenda-live-on-the"),
        (12, W("critical-path.ticketing")): W("critical-path.second-release"),
        (12, W("critical-path.partners")): W("critical-path.headline-partner-signed"),
        (10, W("critical-path.staffing")): W("critical-path.crew-and-volunteers-recruited"),
        (8, W("critical-path.exhibitors")): W("critical-path.exhibitor-manual-sent"),
        (8, W("critical-path.health-and-safety")): W("critical-path.risk-assessment-issued"),
        (6, W("critical-path.production")): W("critical-path.production-schedule-signed-off"),
        (6, W("critical-path.marketing")): W("critical-path.final-push-starts"),
        (4, W("critical-path.exhibitors")): W("critical-path.forms-deadline"),
        (4, W("critical-path.agenda")): W("critical-path.speaker-briefs-sent"),
        (4, W("critical-path.health-and-safety")): W("critical-path.supplier-rams-in"),
        (2, W("critical-path.staffing")): W("critical-path.staff-briefing"),
        (2, W("critical-path.ticketing")): W("critical-path.final-release-closes"),
        (2, W("critical-path.production")): W("critical-path.run-sheet-locked"),
        (1, W("critical-path.site")): W("critical-path.build-day"),
        (1, W("critical-path.health-and-safety")): W("critical-path.site-induction"),
        (0, W("critical-path.site")): W("critical-path.event-days"),
        (-1, W("critical-path.site")): W("critical-path.load-out-and-returns"),
        (-1, W("critical-path.marketing")): W("critical-path.thank-you-emails-and"),
    }
    weeks = list(range(26, -2, -1))
    for i, w in enumerate(weeks):
        r = hr + 1 + i
        body(ws, r, 1, w if w >= 0 else W("critical-path.load-out"), bold=True, align="center")
        body(ws, r, 2, "=$B$7-7*%d" % w, SHORT_DATE)
        for j, s in enumerate(streams):
            inp(ws, r, 3 + j, samples.get((w, s), ""))
    last = hr + len(weeks)
    ws.conditional_formatting.add("A%d:%s%d" % (hr + 1, get_column_letter(cols), last),
                                  FormulaRule(formula=['$A%d=0' % (hr + 1)], fill=TINT_FILL, font=Font(color=B.DARK, bold=True)))
    ws.freeze_panes = "C%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))
    ws.title = "Critical path"
    rows = [
        [
            26,
            "=$B$7-7*A8",
            W("critical-path.site"),
            W("critical-path.site-confirmed"),
            W("critical-path.owner"),
            W("critical-path.done"),
        ],
        [
            12,
            "=$B$7-7*A9",
            W("critical-path.agenda"),
            W("critical-path.agenda-live"),
            W("critical-path.owner"),
            W("critical-path.in-progress"),
        ],
        [
            4,
            "=$B$7-7*A10",
            W("critical-path.exhibitors"),
            W("critical-path.forms-deadline"),
            W("critical-path.owner"),
            W("critical-path.not-started"),
        ],
    ]
    ms, t, hr2, last2 = sheet(
        wb,
        b,
        "Milestones",
        W("critical-path.milestones"),
        W("critical-path.milestones"),
        W("critical-path.one-row-per-milestone"),
        [
            W("critical-path.weeks-to-go"),
            W("critical-path.date"),
            W("critical-path.workstream"),
            W("critical-path.milestone"),
            W("critical-path.owner-2"),
            W("critical-path.status"),
        ],
        rows,
        validations=[
            ("C", streams, W("critical-path.which-workstream")),
            ("F", STATUS, W("critical-path.where-it-is-up")),
        ],
        widths=[12, 14, 18, 40, 16, 14],
        date_cols=(2,),
    )
    for i in range(hr2 + 1, last2 + 1):
        ms.cell(i, 2, "='Critical path'!$B$7-7*A%d" % i)
    ms["B5"] = ""


def supplier_crew_tracker(wb, b):
    rows = [
        [
            W("supplier-crew-tracker.supplier"),
            W("supplier-crew-tracker.service"),
            W("supplier-crew-tracker.name-phone"),
            W("supplier-crew-tracker.ref"),
            0,
            W("supplier-crew-tracker.no"),
            "=E8-IF(F8=\"Yes\",0,0)",
            W("supplier-crew-tracker.no"),
        ]
    ]
    rows = []
    for i in range(8):
        r = 8 + i
        rows.append(
            [
                W("supplier-crew-tracker.supplier"),
                W("supplier-crew-tracker.service"),
                W("supplier-crew-tracker.name-phone"),
                W("supplier-crew-tracker.ref"),
                0,
                0,
                "=IF(ISNUMBER(E%d),E%d-F%d,\"\")" % (r, r, r),
                W("supplier-crew-tracker.no"),
                W("supplier-crew-tracker.no"),
            ]
        )
    sheet(
        wb,
        b,
        "Suppliers",
        W("supplier-crew-tracker.suppliers"),
        W("supplier-crew-tracker.suppliers"),
        W("supplier-crew-tracker.one-row-per-supplier"),
        [
            W("supplier-crew-tracker.supplier-2"),
            W("supplier-crew-tracker.service-2"),
            W("supplier-crew-tracker.contact"),
            W("supplier-crew-tracker.booking-ref"),
            W("supplier-crew-tracker.cost"),
            W("supplier-crew-tracker.deposit-paid"),
            W("supplier-crew-tracker.balance-due"),
            W("supplier-crew-tracker.insurance-received"),
            W("supplier-crew-tracker.rams-received"),
        ],
        rows,
        validations=[
            ("H", YES_NO, W("supplier-crew-tracker.yes-or-no")),
            ("I", YES_NO, W("supplier-crew-tracker.yes-or-no")),
        ],
        widths=[22, 20, 22, 12, 12, 12, 12, 12, 12],
        totals=[5, 6, 7],
        number_cols=(5, 6, 7),
        first=True,
    )
    crew = [
        [
            W("supplier-crew-tracker.name"),
            W("supplier-crew-tracker.steward"),
            W("supplier-crew-tracker.main-stage"),
            None,
            None,
            W("supplier-crew-tracker.crew"),
            W("supplier-crew-tracker.no"),
        ]
        for _ in range(10)
    ]
    sheet(
        wb,
        b,
        "Crew call sheet",
        W("supplier-crew-tracker.crew"),
        W("supplier-crew-tracker.crew-call-sheet"),
        W("supplier-crew-tracker.one-row-per-person"),
        [
            W("supplier-crew-tracker.name-2"),
            W("supplier-crew-tracker.role"),
            W("supplier-crew-tracker.zone"),
            W("supplier-crew-tracker.call-time"),
            W("supplier-crew-tracker.finish-time"),
            W("supplier-crew-tracker.pass-type"),
            W("supplier-crew-tracker.radio-issued"),
        ],
        crew,
        validations=[
            (
                "B",
                [
                    W("supplier-crew-tracker.steward"),
                    W("supplier-crew-tracker.registration"),
                    W("supplier-crew-tracker.stage-crew"),
                    W("supplier-crew-tracker.runner"),
                    W("supplier-crew-tracker.team-lead"),
                    W("supplier-crew-tracker.security"),
                    W("supplier-crew-tracker.first-aid"),
                ],
                W("supplier-crew-tracker.their-role"),
            ),
            (
                "F",
                [
                    W("supplier-crew-tracker.crew"),
                    W("supplier-crew-tracker.staff"),
                    W("supplier-crew-tracker.contractor"),
                    W("supplier-crew-tracker.volunteer"),
                ],
                W("supplier-crew-tracker.the-pass-they-wear"),
            ),
            ("G", YES_NO, W("supplier-crew-tracker.yes-or-no")),
        ],
        widths=[22, 16, 18, 10, 10, 12, 12],
        time_cols=(4, 5),
    )


def floor_plan(wb, b):
    rows = [
        [
            W("floor-plan.a1"),
            W("floor-plan.3x2"),
            W("floor-plan.shell"),
            W("floor-plan.exhibitor-2"),
            W("floor-plan.blank"),
            "",
            W("floor-plan.standard"),
            W("floor-plan.general"),
            W("floor-plan.no"),
        ]
        + [W("floor-plan.no")] * 8
        for _ in range(10)
    ]
    forms = [
        "F%d %s" % (i, n)
        for i, n in enumerate(
            [
                W("floor-plan.exhibitor-form"),
                W("floor-plan.h-and-s"),
                W("floor-plan.induction"),
                W("floor-plan.pat"),
                W("floor-plan.own-h-and-s"),
                W("floor-plan.insurance"),
                W("floor-plan.extras"),
                W("floor-plan.panels"),
            ],
            1,
        )
    ]
    ws, t, hr, last = sheet(
        wb,
        b,
        "Stands",
        W("floor-plan.expo"),
        W("floor-plan.stand-allocation"),
        W("floor-plan.one-row-per-stand"),
        [
            W("floor-plan.stand"),
            W("floor-plan.size"),
            W("floor-plan.type"),
            W("floor-plan.exhibitor"),
            W("floor-plan.panels"),
            W("floor-plan.extras-ordered"),
            W("floor-plan.power"),
            W("floor-plan.wifi"),
            W("floor-plan.paid"),
        ]
        + forms,
        rows,
        validations=[
            (
                "C",
                [W("floor-plan.shell"), W("floor-plan.space-only"), W("floor-plan.pod")],
                W("floor-plan.the-stand-type"),
            ),
            (
                "E",
                [W("floor-plan.blank"), W("floor-plan.own-build"), W("floor-plan.printed"), W("floor-plan.own-print")],
                W("floor-plan.the-panel-option"),
            ),
            (
                "G",
                [W("floor-plan.standard"), W("floor-plan.extra"), W("floor-plan.none")],
                W("floor-plan.power-ordered"),
            ),
            ("H", [W("floor-plan.general"), W("floor-plan.dedicated")], W("floor-plan.wifi")),
        ]
        + [(get_column_letter(c), YES_NO, W("floor-plan.yes-or-no")) for c in range(9, 18)],
        widths=[8, 8, 10, 24, 10, 20, 10, 10, 8] + [7] * 8,
        first=True,
    )
    ws.conditional_formatting.add("I%d:Q%d" % (hr + 1, last + 200), CellIsRule(operator="equal", formula=['"Yes"'],
                                                                          fill=GREY_FILL, font=Font(color=B.CHARCOAL, bold=True)))
    slots = []
    for i in range(10):
        r = 8 + i
        slots.append(
            [
                W("floor-plan.exhibitor-2"),
                2,
                None,
                '=IF(ISNUMBER(C%d),C%d+TIME(0,30,0),"")' % (r, r),
                W("floor-plan.requested"),
            ]
        )
    sheet(
        wb,
        b,
        "Setup slots",
        W("floor-plan.build-up"),
        W("floor-plan.setup-slots"),
        W("floor-plan.one-row-per-booked"),
        [
            W("floor-plan.exhibitor"),
            W("floor-plan.people"),
            W("floor-plan.slot-start"),
            W("floor-plan.slot-end"),
            W("floor-plan.status"),
        ],
        slots,
        validations=[
            (
                "E",
                [W("floor-plan.requested"), W("floor-plan.confirmed"), W("floor-plan.arrived"), W("floor-plan.done")],
                W("floor-plan.where-it-is-up"),
            )
        ],
        widths=[26, 8, 12, 12, 12],
        time_cols=(3, 4),
    )
    vans = []
    for i in range(10):
        r = 8 + i
        vans.append(
            [
                W("floor-plan.exhibitor-2"),
                None,
                '=IF(ISNUMBER(B%d),B%d+TIME(0,15,0),"")' % (r, r),
                W("floor-plan.driver"),
                W("floor-plan.phone"),
                W("floor-plan.reg"),
                "",
            ]
        )
    sheet(
        wb,
        b,
        "Vehicle unloading",
        W("floor-plan.build-up"),
        W("floor-plan.vehicle-unloading"),
        W("floor-plan.slots-of-15-minutes"),
        [
            W("floor-plan.exhibitor"),
            W("floor-plan.slot-start"),
            W("floor-plan.slot-end"),
            W("floor-plan.driver-name"),
            W("floor-plan.driver-phone"),
            W("floor-plan.vehicle-registration"),
            W("floor-plan.notes"),
        ],
        vans,
        widths=[26, 12, 12, 18, 16, 14, 30],
        time_cols=(2, 3),
    )
    g = wb.create_sheet("Block plan")
    title_block(
        g,
        b,
        W("floor-plan.block-plan"),
        W("floor-plan.block-plan"),
        W("floor-plan.type-stand-numbers-into"),
        22,
        [6] + [5] * 20,
    )
    hr = 7
    head(g, hr, 1, "")
    for k in range(20):
        c = head(g, hr, 2 + k, get_column_letter(1 + k))
        c.alignment = Alignment(horizontal="center", vertical="center")
    for i in range(16):
        r = hr + 1 + i
        c = body(g, r, 1, i + 1, bold=True, align="center")
        for k in range(20):
            cell = g.cell(r, 2 + k)
            cell.font = BODY_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
        g.row_dimensions[r].height = 24
    for r, c, v in ((8, 2, "A1"), (8, 3, "A2"), (10, 2, "B1"), (10, 3, "B2"), (8, 8, W("floor-plan.stage"))):
        g.cell(r, c, v)
    for k in range(20):
        g.cell(13, 2 + k).fill = GREY_FILL
    print_setup(g, b)


def staff_rota(wb, b):
    rows = []
    zones = [
        W("staff-rota.registration"),
        W("staff-rota.main-stage"),
        W("staff-rota.expo"),
        W("staff-rota.roundtable-rooms"),
        W("staff-rota.green-room"),
    ]
    for i in range(12):
        r = 8 + i
        rows.append(
            [
                W("staff-rota.day-one") if i < 6 else W("staff-rota.day-two"),
                zones[i % 5],
                W("staff-rota.steward"),
                W("staff-rota.name-2"),
                None,
                None,
                30,
                '=IF(AND(ISNUMBER(E%d),ISNUMBER(F%d)),ROUND((F%d-E%d)*24-G%d/60,2),"")' % (r, r, r, r, r),
                W("staff-rota.lead"),
                W("staff-rota.no"),
            ]
        )
    ws, t, hr, last = sheet(
        wb,
        b,
        "Shifts",
        W("staff-rota.rota"),
        W("staff-rota.staff-and-volunteer-rota"),
        W("staff-rota.one-row-per-shift"),
        [
            W("staff-rota.day"),
            W("staff-rota.zone"),
            W("staff-rota.role"),
            W("staff-rota.name"),
            W("staff-rota.start"),
            W("staff-rota.end"),
            W("staff-rota.break-min"),
            W("staff-rota.hours"),
            W("staff-rota.team-lead"),
            W("staff-rota.radio"),
        ],
        rows,
        validations=[
            (
                "A",
                [W("staff-rota.build-day"), W("staff-rota.day-one"), W("staff-rota.day-two"), W("staff-rota.load-out")],
                W("staff-rota.which-day"),
            ),
            ("B", zones + [W("staff-rota.everywhere")], W("staff-rota.which-zone")),
            (
                "C",
                [
                    W("staff-rota.steward"),
                    W("staff-rota.registration"),
                    W("staff-rota.stage-crew"),
                    W("staff-rota.runner"),
                    W("staff-rota.team-lead"),
                    W("staff-rota.floater"),
                ],
                W("staff-rota.their-role"),
            ),
            ("J", YES_NO, W("staff-rota.radio-issued")),
        ],
        widths=[12, 18, 14, 20, 9, 9, 11, 9, 16, 9],
        time_cols=(5, 6),
        first=True,
    )
    for i in range(hr + 1, last + 1):
        ws.cell(i, 8).number_format = HOURS
    s = wb.create_sheet("By person")
    title_block(s, b, W("staff-rota.summary"), W("staff-rota.hours-by-person"), W("staff-rota.type-each-name-once"), 8,
                [22, 10, 10])
    heads(s, 7, [W("staff-rota.name"), W("staff-rota.shifts"), W("staff-rota.hours")])
    for i in range(8, 28):
        inp(s, i, 1, W("staff-rota.name-2") if i == 8 else "")
        body(s, i, 2, '=IF(A%d="","",COUNTIFS(Shifts[Name],A%d))' % (i, i))
        body(s, i, 3, '=IF(A%d="","",SUMIFS(Shifts[Hours],Shifts[Name],A%d))' % (i, i), HOURS)
    print_setup(s, b)


def feedback_results(wb, b):
    qs = [["Q1", W("feedback-results.how-likely-are-you"), W("feedback-results.score-1-to-10")],
          ["Q2", W("feedback-results.how-useful-were-the"), W("feedback-results.score-1-to-5")],
          ["Q3", W("feedback-results.how-useful-were-the-2"), W("feedback-results.score-1-to-5")],
          ["Q4", W("feedback-results.how-easy-was-the"), W("feedback-results.score-1-to-5")],
          ["Q5", W("feedback-results.how-likely-are-you-2"), W("feedback-results.score-1-to-5")],
          ["Q6", W("feedback-results.what-should-we-keep"), W("feedback-results.free-text")]]
    sheet(
        wb,
        b,
        "Questions",
        W("feedback-results.survey"),
        W("feedback-results.questions"),
        W("feedback-results.one-row-per-question"),
        ["ID", W("feedback-results.question"), W("feedback-results.type")],
        qs,
        widths=[8, 60, 16],
        first=True,
    )
    resp = [
        [W("feedback-results.respondent"), None, W("feedback-results.attendee"), None, None, None, None, None, ""]
        for _ in range(10)
    ]
    r_ws, t, hr, last = sheet(
        wb,
        b,
        "Responses",
        W("feedback-results.survey"),
        W("feedback-results.responses"),
        W("feedback-results.one-row-per-response"),
        [
            W("feedback-results.respondent-2"),
            W("feedback-results.date"),
            W("feedback-results.type"),
            "Q1",
            "Q2",
            "Q3",
            "Q4",
            "Q5",
            W("feedback-results.q6-comment"),
        ],
        resp,
        validations=[
            (
                "C",
                [
                    W("feedback-results.attendee"),
                    W("feedback-results.speaker"),
                    W("feedback-results.partner"),
                    W("feedback-results.exhibitor"),
                    W("feedback-results.crew"),
                ],
                W("feedback-results.who-answered"),
            )
        ],
        widths=[18, 14, 12, 8, 8, 8, 8, 8, 50],
        date_cols=(2,),
    )
    s = wb.create_sheet("Summary", 0)
    title_block(
        s,
        b,
        W("feedback-results.summary"),
        W("feedback-results.feedback-results"),
        W("feedback-results.averages-and-counts-from"),
        8,
        [10, 50, 12, 12],
    )
    heads(
        s,
        7,
        [
            W("feedback-results.id"),
            W("feedback-results.question"),
            W("feedback-results.average"),
            W("feedback-results.responses"),
        ],
    )
    for i, q in enumerate(qs[:5], 8):
        body(s, i, 1, q[0])
        body(s, i, 2, q[1])
        body(s, i, 3, '=IFERROR(AVERAGE(Responses[%s]),"")' % q[0], "0.0")
        body(s, i, 4, "=COUNT(Responses[%s])" % q[0])
    col_chart(s, W("feedback-results.average-score-by-question"), Reference(s, min_col=1, min_row=8, max_row=12),
              Reference(s, min_col=3, min_row=7, max_row=12), "F7")
    print_setup(s, b)
    sheet(
        wb,
        b,
        "Comments",
        W("feedback-results.survey"),
        W("feedback-results.comments"),
        W("feedback-results.one-row-per-comment"),
        [
            W("feedback-results.respondent-2"),
            W("feedback-results.comment"),
            W("feedback-results.theme"),
            W("feedback-results.quote-in-the-report"),
        ],
        [
            [
                W("feedback-results.respondent"),
                W("feedback-results.comment-2"),
                W("feedback-results.sessions"),
                W("feedback-results.no"),
            ]
            for _ in range(8)
        ],
        validations=[
            (
                "C",
                [
                    W("feedback-results.sessions"),
                    W("feedback-results.networking"),
                    W("feedback-results.site"),
                    W("feedback-results.food-and-drink"),
                    W("feedback-results.expo"),
                    W("feedback-results.agenda"),
                    W("feedback-results.other"),
                ],
                W("feedback-results.the-theme"),
            ),
            ("D", YES_NO, W("feedback-results.consent-to-quote")),
        ],
        widths=[18, 70, 16, 14],
    )


def exhibitor_risk_assessment(wb, b):
    ed = edition(b)
    r = wb.active
    title_block(
        r,
        b,
        W("exhibitor-risk-assessment.read-me"),
        W("exhibitor-risk-assessment.exhibitor-and-partner-risk"),
        W("exhibitor-risk-assessment.five-steps-then-the"),
        4,
        [6, 90],
    )
    steps = [
        W("exhibitor-risk-assessment.complete-your-details-at"),
        W("exhibitor-risk-assessment.each-row-is-one"),
        W("exhibitor-risk-assessment.add-rows-for-anything"),
        W("exhibitor-risk-assessment.score-likelihood-and-severity"),
        C.fill(
            W("exhibitor-risk-assessment.check-it-before-you"),
            email=B.BRANDS[b]["email"].replace("marketing", "exhibitors"),
        ),
    ]
    for i, s in enumerate(steps):
        body(r, 7 + i, 1, i + 1, bold=True, align="center")
        body(r, 7 + i, 2, s)
        r.row_dimensions[7 + i].height = 32
    label(r, 13, 1, W("exhibitor-risk-assessment.likelihood"))
    for i, l in enumerate(LIKELIHOOD):
        body(r, 14 + i, 2, l)
    label(r, 20, 1, W("exhibitor-risk-assessment.severity"))
    for i, s in enumerate(SEVERITY):
        body(r, 21 + i, 2, s)
    label(r, 27, 1, W("exhibitor-risk-assessment.bands"))
    for i, (band, what) in enumerate(
        [
            (W("exhibitor-risk-assessment.low-1-to-4"), W("exhibitor-risk-assessment.acceptable-keep-the-controls")),
            (W("exhibitor-risk-assessment.medium-5-to-9"), W("exhibitor-risk-assessment.acceptable-with-the-controls")),
            (W("exhibitor-risk-assessment.high-10-to-15"), W("exhibitor-risk-assessment.add-controls-to-bring")),
            (W("exhibitor-risk-assessment.critical-16-to-25"), W("exhibitor-risk-assessment.do-not-run-this")),
        ]
    ):
        body(r, 28 + i, 2, "%s: %s" % (band, what))
    print_setup(r, b, landscape=False)
    ws = wb.create_sheet("Risk register")
    cols = 18
    title_block(
        ws,
        b,
        W("exhibitor-risk-assessment.risk-register"),
        C.fill(W("exhibitor-risk-assessment.your-stand-at"), edition=ed),
        W("exhibitor-risk-assessment.one-row-per-hazard"),
        cols,
        [16, 22, 22, 18, 20, 36, 30, 10, 10, 9, 10, 10, 10, 9, 10, 16, 12, 26],
    )
    details = [
        (W("exhibitor-risk-assessment.company"), W("exhibitor-risk-assessment.company-2")),
        (
            W("exhibitor-risk-assessment.event"),
            "%s, %s" % (ed, B.BRANDS[b]["edition"] or W("exhibitor-risk-assessment.dates")),
        ),
        (W("exhibitor-risk-assessment.stand"), W("exhibitor-risk-assessment.stand-number")),
        (W("exhibitor-risk-assessment.contact-name"), W("exhibitor-risk-assessment.name")),
        (W("exhibitor-risk-assessment.email"), W("exhibitor-risk-assessment.email-2")),
        (W("exhibitor-risk-assessment.phone"), W("exhibitor-risk-assessment.phone-2")),
        (W("exhibitor-risk-assessment.date"), W("exhibitor-risk-assessment.date-2")),
        (W("exhibitor-risk-assessment.completed-by"), W("exhibitor-risk-assessment.name")),
    ]
    for i, (k, v) in enumerate(details):
        label(ws, 7 + i // 2, 1 + 2 * (i % 2), k)
        inp(ws, 7 + i // 2, 2 + 2 * (i % 2), v)
    label(ws, 12, 1, W("exhibitor-risk-assessment.matrix"))
    body(ws, 12, 2, W("exhibitor-risk-assessment.likelihood-1-rare-2"), wrap=True)
    ws.merge_cells(start_row=12, start_column=2, end_row=12, end_column=12)
    ws.row_dimensions[12].height = 44
    hr = 14
    heads(
        ws,
        hr,
        [
            W("exhibitor-risk-assessment.area-or-activity"),
            W("exhibitor-risk-assessment.item-or-task"),
            W("exhibitor-risk-assessment.hazard"),
            W("exhibitor-risk-assessment.who-could-be-harmed"),
            W("exhibitor-risk-assessment.potential-harm"),
            W("exhibitor-risk-assessment.existing-controls"),
            W("exhibitor-risk-assessment.additional-controls-for-this"),
            W("exhibitor-risk-assessment.likelihood-before"),
            W("exhibitor-risk-assessment.severity-before"),
            W("exhibitor-risk-assessment.risk-score-before"),
            W("exhibitor-risk-assessment.risk-band-before"),
            W("exhibitor-risk-assessment.likelihood-after"),
            W("exhibitor-risk-assessment.severity-after"),
            W("exhibitor-risk-assessment.residual-score"),
            W("exhibitor-risk-assessment.residual-band"),
            W("exhibitor-risk-assessment.person-responsible"),
            W("exhibitor-risk-assessment.status"),
            W("exhibitor-risk-assessment.notes-or-evidence"),
        ],
        height=40,
    )
    hazards = [
        (
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.moving-in-out-and"),
            W("exhibitor-risk-assessment.congestion-or-blocked-routes"),
            W("exhibitor-risk-assessment.visitors-and-your-team"),
            W("exhibitor-risk-assessment.trips-falls-or-collisions"),
            W("exhibitor-risk-assessment.layout-leaves-a-clear"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.hands-on-demos-and"),
            W("exhibitor-risk-assessment.crowding-at-the-stand"),
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.trips-and-collisions"),
            W("exhibitor-risk-assessment.queues-stay-inside-the"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.layout"),
            W("exhibitor-risk-assessment.your-space-and-its"),
            W("exhibitor-risk-assessment.items-or-queues-spilling"),
            W("exhibitor-risk-assessment.visitors-other-exhibitors-and"),
            W("exhibitor-risk-assessment.trips-or-a-slower"),
            W("exhibitor-risk-assessment.everything-stays-inside-the"),
            2,
            3,
        ),
        (
            W("exhibitor-risk-assessment.your-team"),
            W("exhibitor-risk-assessment.long-days-on-your"),
            W("exhibitor-risk-assessment.tiredness-and-dehydration"),
            W("exhibitor-risk-assessment.your-team"),
            W("exhibitor-risk-assessment.lower-awareness-fainting-minor"),
            W("exhibitor-risk-assessment.a-break-rota-water"),
            2,
            1,
        ),
        (
            W("exhibitor-risk-assessment.your-team"),
            W("exhibitor-risk-assessment.people-working-in-your"),
            W("exhibitor-risk-assessment.not-knowing-the-layout"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.unsafe-behaviour-a-slow"),
            W("exhibitor-risk-assessment.everyone-is-briefed-before"),
            2,
            3,
        ),
        (
            W("exhibitor-risk-assessment.set-up-and-break"),
            W("exhibitor-risk-assessment.lifting-and-moving-equipment"),
            W("exhibitor-risk-assessment.heavy-or-awkward-loads"),
            W("exhibitor-risk-assessment.your-team-and-contractors"),
            W("exhibitor-risk-assessment.strains-sprains-and-back"),
            W("exhibitor-risk-assessment.trolleys-for-heavy-items"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.set-up-and-break"),
            W("exhibitor-risk-assessment.custom-structures"),
            W("exhibitor-risk-assessment.collapse-or-falling-items"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.serious-injury"),
            W("exhibitor-risk-assessment.designed-and-built-by"),
            1,
            4,
        ),
        (
            W("exhibitor-risk-assessment.interactive-activity"),
            W("exhibitor-risk-assessment.games-challenges-and-competitions"),
            W("exhibitor-risk-assessment.crowding-over-excitement-or"),
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.trips-collisions-minor-injury"),
            W("exhibitor-risk-assessment.clear-rules-on-display"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.housekeeping"),
            W("exhibitor-risk-assessment.cables-flooring-edges-boxes"),
            W("exhibitor-risk-assessment.trip-hazards-inside-your"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.trips-and-falls"),
            W("exhibitor-risk-assessment.cables-run-behind-the"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.housekeeping"),
            W("exhibitor-risk-assessment.drinks-waste-and-spills"),
            W("exhibitor-risk-assessment.wet-or-slippery-floor"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.slips-and-falls"),
            W("exhibitor-risk-assessment.spills-are-cleaned-straight"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.housekeeping"),
            W("exhibitor-risk-assessment.stock-packaging-and-spare"),
            W("exhibitor-risk-assessment.poorly-stacked-items-or"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.items-falling-trips"),
            W("exhibitor-risk-assessment.stock-is-stacked-low"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.electrical"),
            W("exhibitor-risk-assessment.power-and-data-cables"),
            W("exhibitor-risk-assessment.trailing-or-damaged-cables"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.trips-electric-shock"),
            W("exhibitor-risk-assessment.cables-are-checked-before"),
            2,
            3,
        ),
        (
            W("exhibitor-risk-assessment.electrical"),
            W("exhibitor-risk-assessment.screens-laptops-lighting-and"),
            W("exhibitor-risk-assessment.faulty-electrical-equipment"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.electric-shock-or-fire"),
            W("exhibitor-risk-assessment.equipment-is-in-good"),
            1,
            4,
        ),
        (
            W("exhibitor-risk-assessment.electrical"),
            W("exhibitor-risk-assessment.extension-leads-and-power"),
            W("exhibitor-risk-assessment.overloaded-sockets-or-daisy"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.fire"),
            W("exhibitor-risk-assessment.power-use-stays-within"),
            1,
            4,
        ),
        (
            W("exhibitor-risk-assessment.demonstrations"),
            W("exhibitor-risk-assessment.live-product-demos"),
            W("exhibitor-risk-assessment.unsafe-use-or-visitors"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.minor-injury"),
            W("exhibitor-risk-assessment.demos-are-run-by"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.demonstrations"),
            W("exhibitor-risk-assessment.machines-props-or-anything"),
            W("exhibitor-risk-assessment.contact-with-moving-parts"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.crush-cut-or-trapping"),
            W("exhibitor-risk-assessment.guards-stay-on-a"),
            2,
            3,
        ),
        (
            W("exhibitor-risk-assessment.demonstrations"),
            W("exhibitor-risk-assessment.stock-and-giveaways-on"),
            W("exhibitor-risk-assessment.items-falling-distraction-while"),
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.minor-injury"),
            W("exhibitor-risk-assessment.stock-kept-in-a"),
            2,
            1,
        ),
        (
            W("exhibitor-risk-assessment.food-and-drink"),
            W("exhibitor-risk-assessment.serving-food-or-samples"),
            W("exhibitor-risk-assessment.contamination-poor-hygiene-or"),
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.food-poisoning-or-an"),
            W("exhibitor-risk-assessment.food-handlers-are-trained"),
            2,
            3,
        ),
        (
            W("exhibitor-risk-assessment.food-and-drink"),
            W("exhibitor-risk-assessment.hot-drinks-hot-food"),
            W("exhibitor-risk-assessment.heat-steam-and-hot"),
            W("exhibitor-risk-assessment.your-team-and-visitors"),
            W("exhibitor-risk-assessment.burns-and-scalds"),
            W("exhibitor-risk-assessment.hot-equipment-sits-at"),
            2,
            2,
        ),
        (
            W("exhibitor-risk-assessment.food-and-drink"),
            W("exhibitor-risk-assessment.storing-food"),
            W("exhibitor-risk-assessment.food-kept-at-the"),
            W("exhibitor-risk-assessment.visitors"),
            W("exhibitor-risk-assessment.food-poisoning"),
            W("exhibitor-risk-assessment.chilled-food-kept-chilled"),
            2,
            3,
        ),
    ]
    n = len(hazards) + 6
    for i in range(n):
        r_ = hr + 1 + i
        h = hazards[i] if i < len(hazards) else ("", "", "", "", "", "", None, None)
        for j, v in enumerate(h[:6]):
            inp(ws, r_, 1 + j, v)
        inp(ws, r_, 7, "")
        inp(ws, r_, 8, h[6])
        inp(ws, r_, 9, h[7])
        body(ws, r_, 10, '=IF(AND(ISNUMBER(H%d),ISNUMBER(I%d)),H%d*I%d,"")' % (r_, r_, r_, r_), align="center")
        body(ws, r_, 11, "=" + BAND_FORMULA % (("J%d" % r_,) * 4), bold=True, align="center")
        inp(ws, r_, 12, h[6])
        inp(ws, r_, 13, h[7])
        body(ws, r_, 14, '=IF(AND(ISNUMBER(L%d),ISNUMBER(M%d)),L%d*M%d,"")' % (r_, r_, r_, r_), align="center")
        body(ws, r_, 15, "=" + BAND_FORMULA % (("N%d" % r_,) * 4), bold=True, align="center")
        inp(ws, r_, 16, W("exhibitor-risk-assessment.name") if i < len(hazards) else "")
        inp(ws, r_, 17, W("exhibitor-risk-assessment.open") if i < len(hazards) else "")
        inp(ws, r_, 18, "")
        ws.row_dimensions[r_].height = 58 if i < len(hazards) else 30
    last = hr + n
    for col in ("H", "I", "L", "M"):
        listv(
            ws,
            "%s%d:%s%d" % (col, hr + 1, col, last + 100),
            ["1", "2", "3", "4", "5"],
            W("exhibitor-risk-assessment.1-to-5"),
        )
    listv(
        ws,
        "Q%d:Q%d" % (hr + 1, last + 100),
        [
            W("exhibitor-risk-assessment.open"),
            W("exhibitor-risk-assessment.in-progress"),
            W("exhibitor-risk-assessment.done"),
        ],
        W("exhibitor-risk-assessment.where-the-controls-are"),
    )
    band_rules(ws, "K%d:K%d" % (hr + 1, last + 100))
    band_rules(ws, "O%d:O%d" % (hr + 1, last + 100))
    ws.freeze_panes = "D%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))
    label(ws, last + 2, 1, W("exhibitor-risk-assessment.signed"))
    inp(ws, last + 2, 2, W("exhibitor-risk-assessment.name-and-date"))


BOOKS = {
    "Invoice": invoice, "Quote": quote, "Purchase-order": purchase_order, "Annual-budget": annual_budget,
    "Cash-flow-forecast": cash_flow, "Profit-and-loss": profit_and_loss, "Expense-claim": expense_claim,
    "KPI-dashboard": kpi_dashboard, "Project-plan": project_plan, "Task-tracker": task_tracker,
    "Risk-register": risk_register, "Contact-list": contact_list, "Supplier-register": supplier_register,
    "Asset-register": asset_register, "Timesheet": timesheet, "Leave-planner": leave_planner,
    "Recruitment-tracker": recruitment_tracker, "Speaker-tracker": speaker_tracker, "Critical-path": critical_path,
    "Supplier-crew-tracker": supplier_crew_tracker, "Floor-plan": floor_plan, "Staff-rota": staff_rota,
    "Feedback-results": feedback_results, "Exhibitor-risk-assessment": exhibitor_risk_assessment,
}


def all_copy(brands=("ClimbUK", "ClimbGroup", "Climb27")):
    """Every string a reader sees in the workbooks, for the copy checker: the words of every workbook's copy file."""
    import catalog as K
    import copy_md
    from xl_copy import SHARED
    out = [copy_md.reader_words(C.load(SHARED))]
    for b in brands:
        for row in K.rows("excel", b):
            out.append(copy_md.reader_words(C.load(K.copy_file(b, row))))
    return out
