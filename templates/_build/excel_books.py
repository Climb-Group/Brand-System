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
from xl import (BODY_FONT, EYEBROW_FONT, GBP, HEAD_FILL, HEAD_FONT, SUB_FONT, THIN, TITLE_FONT, TOTAL_FONT, TOTAL_TOP,
                banner, sheet, summary_chart)

VAT_NUMBER = "GB335770882"
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
YES_NO = ["Yes", "No"]
STATUS = ["Not started", "In progress", "Blocked", "Done"]
LIKELIHOOD = ["1 Rare", "2 Unlikely", "3 Possible", "4 Likely", "5 Almost certain"]
SEVERITY = ["1 Minor injury or inconvenience", "2 First aid required", "3 Injury requiring medical treatment",
            "4 Serious injury", "5 Major injury or fatality"]
BAND_FORMULA = 'IF(%s="","",IF(%s>=16,"Critical",IF(%s>=10,"High",IF(%s>=5,"Medium","Low"))))'


def edition(b):
    return b if B.BRANDS[b]["edition"] else "[Edition]"


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
    ws.oddFooter.right.text = "Page &P of &N"
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


def listv(ws, rng, options, prompt="Pick one"):
    dv = DataValidation(type="list", formula1='"%s"' % ",".join(options), allow_blank=True, promptTitle="Pick one",
                        prompt=prompt, showInputMessage=True, showErrorMessage=True, errorTitle="Not on the list",
                        error="Pick a value from the list.")
    dv.add(rng)
    ws.add_data_validation(dv)


def total_row(ws, row, cols, label_col=1, text="Total"):
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
    spec = {
        "Invoice": dict(eyebrow="Invoice", sub="Payable within 14 days of the invoice date.",
                        number="Invoice number", dated="Invoice date", third="Due date", to="Bill to",
                        close="Pay by bank transfer to [Account name], sort code [00-00-00], account [00000000], "
                              "quoting the invoice number. Questions to [email]."),
        "Quote": dict(eyebrow="Quote", sub="Prices hold until the date shown. To accept, reply to [email].",
                      number="Quote number", dated="Quote date", third="Valid until", to="Quote for",
                      close="This quote becomes an order when you accept it in writing. Work starts on [what starts it]."),
        "Purchase-order": dict(eyebrow="Purchase order", sub="Quote this number on your invoice.",
                               number="Purchase order number", dated="Order date", third="Required by", to="Supplier",
                               close="Send invoices to [email] quoting the purchase order number. Payment within 14 "
                                     "days of a correct invoice."),
    }[kind]
    ws = wb.active
    title_block(ws, b, spec["eyebrow"], spec["eyebrow"].replace("-", " "), spec["sub"], 6, [30, 12, 16, 16, 4, 22])
    # Who it is from, and the numbers.
    label(ws, 7, 1, "From" if kind != "Purchase-order" else "Ordered by")
    for k, line in enumerate(B.LEGAL.split(". ")[:1] + ["[Address line 1]", "[Town, Postcode]", "VAT number %s" % VAT_NUMBER]):
        body(ws, 8 + k, 1, line)
    for k, (lab, val, fmt) in enumerate([(spec["number"], "[0001]", None), (spec["dated"], date.today(), "d mmm yyyy"),
                                         (spec["third"], "=D8+14", "d mmm yyyy")]):
        label(ws, 7 + k, 3, lab)
        inp(ws, 7 + k, 4, val, fmt)
    label(ws, 13, 1, spec["to"])
    for k, line in enumerate(["[Company name]", "[Contact name]", "[Address line 1]", "[Town, Postcode]"]):
        inp(ws, 14 + k, 1, line)
    label(ws, 13, 3, "Reference")
    inp(ws, 14, 3, "[Your reference]")
    ws.merge_cells("C14:D14")
    # Lines.
    hr = 20
    heads(ws, hr, ["Description", "Quantity", "Unit price", "Total"])
    n = 8
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, "[Item]" if i == 0 else "")
        inp(ws, r, 2, 1 if i == 0 else None, "0.##")
        inp(ws, r, 3, 0, GBP)
        body(ws, r, 4, '=IF(AND(ISNUMBER(B%d),ISNUMBER(C%d)),B%d*C%d,"")' % (r, r, r, r), GBP)
        for c in range(1, 5):
            ws.cell(r, c).border = Border(bottom=THIN)
    last = hr + n
    label(ws, last + 2, 3, "Subtotal")
    body(ws, last + 2, 4, "=SUM(D%d:D%d)" % (hr + 1, last), GBP, bold=True)
    label(ws, last + 3, 3, "VAT rate")
    inp(ws, last + 3, 4, 0.2, PCT)
    label(ws, last + 4, 3, "VAT")
    body(ws, last + 4, 4, "=ROUND(D%d*D%d,2)" % (last + 2, last + 3), GBP, bold=True)
    label(ws, last + 5, 3, "Total")
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
    title_block(ws, b, "Expenses", "Expense claim", "One line per receipt. Attach every receipt to the claim.", 7,
                [14, 34, 16, 12, 14, 14, 24])
    for k, (lab, val) in enumerate([("Name", "[Name]"), ("Team", "[Team]"), ("Claim period", "[Month]"),
                                    ("Claim date", "[Date]")]):
        label(ws, 7 + k, 1, lab)
        inp(ws, 7 + k, 2, val)
    label(ws, 7, 4, "VAT rate")
    inp(ws, 7, 5, 0.2, PCT)
    hr = 12
    cats = ["Travel", "Accommodation", "Meals", "Equipment", "Event costs", "Other"]
    heads(ws, hr, ["Date", "Description", "Category", "Receipt", "Amount", "VAT in the amount", "Notes"])
    n = 12
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, None, SHORT_DATE)
        inp(ws, r, 2, "[What and why]" if i == 0 else "")
        inp(ws, r, 3, cats[0] if i == 0 else "")
        inp(ws, r, 4, "Yes" if i == 0 else "")
        inp(ws, r, 5, 0, GBP)
        body(ws, r, 6, '=IF(ISNUMBER(E%d),ROUND(E%d-E%d/(1+$E$7),2),"")' % (r, r, r), GBP)
        inp(ws, r, 7, "")
    listv(ws, "C%d:C%d" % (hr + 1, hr + n), cats, "What kind of cost")
    listv(ws, "D%d:D%d" % (hr + 1, hr + n), YES_NO, "Is the receipt attached")
    tr = hr + n + 2
    total_row(ws, tr, [5, 6])
    ws.cell(tr, 5, "=SUM(E%d:E%d)" % (hr + 1, hr + n)).number_format = GBP
    ws.cell(tr, 6, "=SUM(F%d:F%d)" % (hr + 1, hr + n)).number_format = GBP
    label(ws, tr + 3, 1, "Claimed by")
    inp(ws, tr + 3, 2, "[Signature and date]")
    label(ws, tr + 4, 1, "Approved by")
    inp(ws, tr + 4, 2, "[Signature and date]")
    print_setup(ws, b, landscape=True, title_rows="%d:%d" % (hr, hr))


# ---------- finance grids ----------

def grid(ws, b, eyebrow, title, sub, sections, start_cell="B7", first_col_width=30):
    """Rows of lines under section headings, 12 months across plus a total column, with a total row per section.
    sections: [(name, [lines]), ...]. Returns {section name: total row}."""
    cols = 15
    title_block(ws, b, eyebrow, title, sub, cols, [first_col_width] + [11] * 13 + [4])
    label(ws, 7, 1, "First month")
    inp(ws, 7, 2, date(date.today().year + 1, 1, 1), "mmm yyyy")
    hr = 9
    head(ws, hr, 1, "")
    month_headers(ws, hr, 2, start_cell)
    head(ws, hr, 14, "Total")
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
        total_row(ws, r, list(range(2, 15)), text="Total %s" % name.lower())
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
    totals, r = grid(ws, b, "Budget", "Annual budget", "Twelve months of income and costs. Change the first month and "
                     "the headers follow.",
                     [("Income", ["Tickets", "Partnerships", "Exhibitors", "Other income"]),
                      ("Costs", ["Production", "Marketing", "People", "Office and systems", "Travel", "Contingency"])])
    net_row(ws, r, totals["Income"], totals["Costs"], "Net")
    s = wb.create_sheet("Summary")
    title_block(s, b, "Summary", "Income, costs and net by month", "", 8, [16, 14, 14, 14])
    heads(s, 7, ["Month", "Income", "Costs", "Net"])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "=Budget!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "=Budget!%s%d" % (col, totals["Income"]), GBP)
        body(s, 8 + k, 3, "=Budget!%s%d" % (col, totals["Costs"]), GBP)
        body(s, 8 + k, 4, "=B%d-C%d" % (8 + k, 8 + k), GBP)
    col_chart(s, "Income and costs by month", Reference(s, min_col=1, min_row=8, max_row=19),
              Reference(s, min_col=2, max_col=3, min_row=7, max_row=19), "F7", "£")
    print_setup(s, b)


def cash_flow(wb, b):
    ws = wb.active
    totals, r = grid(ws, b, "Cash flow", "Cash flow forecast", "Cash in and out by month. The closing balance carries "
                     "into the next month.",
                     [("Cash in", ["Ticket sales", "Partner payments", "Exhibitor payments", "Other receipts"]),
                      ("Cash out", ["Suppliers", "Payroll", "Rent and systems", "Marketing", "Tax and VAT", "Other payments"])])
    net_row(ws, r, totals["Cash in"], totals["Cash out"], "Net cash flow")
    net = r
    label(ws, r + 2, 1, "Opening balance")
    inp(ws, r + 2, 2, 0, GBP)
    for k in range(1, 12):
        col, prev = get_column_letter(2 + k), get_column_letter(1 + k)
        body(ws, r + 2, 2 + k, "=%s%d" % (prev, r + 3), GBP)
    ws.cell(r + 3, 1, "Closing balance").font = LABEL_FONT
    for k in range(12):
        col = get_column_letter(2 + k)
        body(ws, r + 3, 2 + k, "=%s%d+%s%d" % (col, r + 2, col, net), GBP, bold=True)
    for col in range(1, 14):
        ws.cell(r + 3, col).border = Border(top=TOTAL_TOP, bottom=TOTAL_TOP)
    ws.conditional_formatting.add("B%d:M%d" % (r + 3, r + 3), CellIsRule(operator="lessThan", formula=["0"],
                                                                      font=Font(color=B.ORANGE_DEEP, bold=True)))
    s = wb.create_sheet("Summary")
    title_block(s, b, "Summary", "Closing balance by month", "", 8, [16, 16])
    heads(s, 7, ["Month", "Closing balance"])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "='Cash flow'!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "='Cash flow'!%s%d" % (col, r + 3), GBP)
    line_chart(s, "Closing balance", Reference(s, min_col=1, min_row=8, max_row=19),
               Reference(s, min_col=2, min_row=7, max_row=19), "D7", "£")
    print_setup(s, b)
    ws.title = "Cash flow"


def profit_and_loss(wb, b):
    ws = wb.active
    totals, r = grid(ws, b, "Profit and loss", "Profit and loss tracker", "Actuals by month. Gross profit is revenue less "
                     "cost of sales; net profit takes off overheads.",
                     [("Revenue", ["Tickets", "Partnerships", "Exhibitors", "Other revenue"]),
                      ("Cost of sales", ["Production", "Speakers and content", "Catering", "Print and signage"]),
                      ("Overheads", ["People", "Marketing", "Office and systems", "Professional fees", "Other overheads"])])
    net_row(ws, r, totals["Revenue"], totals["Cost of sales"], "Gross profit")
    gp = r
    ws.cell(r + 1, 1, "Gross margin").font = LABEL_FONT
    for k in range(13):
        col = get_column_letter(2 + k)
        body(ws, r + 1, 2 + k, '=IF(%s%d=0,"",%s%d/%s%d)' % (col, totals["Revenue"], col, gp, col, totals["Revenue"]), PCT)
    net_row(ws, r + 3, gp, totals["Overheads"], "Net profit")
    s = wb.create_sheet("Summary")
    title_block(s, b, "Summary", "Revenue and net profit by month", "", 8, [16, 14, 14])
    heads(s, 7, ["Month", "Revenue", "Net profit"])
    for k in range(12):
        col = get_column_letter(2 + k)
        body(s, 8 + k, 1, "='Profit and loss'!%s9" % col, "mmm yyyy")
        body(s, 8 + k, 2, "='Profit and loss'!%s%d" % (col, totals["Revenue"]), GBP)
        body(s, 8 + k, 3, "='Profit and loss'!%s%d" % (col, r + 3), GBP)
    col_chart(s, "Revenue and net profit", Reference(s, min_col=1, min_row=8, max_row=19),
              Reference(s, min_col=2, max_col=3, min_row=7, max_row=19), "E7", "£")
    print_setup(s, b)
    ws.title = "Profit and loss"


# ---------- dashboards and plans ----------

def kpi_dashboard(wb, b):
    kpis = ["Revenue", "New customers", "Active customers", "Website visits", "Email subscribers"]
    start = date(date.today().year, 1, 1)
    rows = []
    for k in range(12):
        m = date(start.year + (start.month + k - 1) // 12, (start.month + k - 1) % 12 + 1, 1)
        rows.append([m, 0, 0, 0, 0, 0])
    inputs, t, hr, last = sheet(wb, b, "Inputs", "KPIs", "KPI inputs", "One row per month. The dashboard reads from here; "
                                "add rows at the bottom as months pass.", ["Month"] + kpis, rows,
                                widths=[14, 14, 14, 14, 14, 16], number_cols=(2,), first=True)
    for i in range(hr + 1, last + 1):
        inputs.cell(i, 1).number_format = "mmm yyyy"
    d = wb.create_sheet("Dashboard", 0)
    title_block(d, b, "Dashboard", "KPI dashboard", "The latest month against the one before, and the trend.", 10,
                [22, 14, 14, 14, 3, 14, 14, 14, 14, 14])
    heads(d, 7, ["KPI", "Latest", "Previous", "Change"])
    n = "COUNT(Inputs[Month])"
    for k, kpi in enumerate(kpis):
        r = 8 + k
        body(d, r, 1, kpi, bold=True)
        fmt = GBP if kpi == "Revenue" else "#,##0"
        body(d, r, 2, "=IFERROR(INDEX(Inputs[%s],%s),0)" % (kpi, n), fmt, bold=True)
        body(d, r, 3, "=IFERROR(INDEX(Inputs[%s],%s-1),0)" % (kpi, n), fmt)
        body(d, r, 4, '=IF(C%d=0,"",B%d/C%d-1)' % (r, r, r), PCT)
    d.conditional_formatting.add("D8:D12", CellIsRule(operator="lessThan", formula=["0"],
                                                      font=Font(color=B.ORANGE_DEEP, bold=True)))
    cats = Reference(inputs, min_col=1, min_row=hr + 1, max_row=last)
    line_chart(d, "Revenue by month", cats, Reference(inputs, min_col=2, min_row=hr, max_row=last), "F7", "£")
    col_chart(d, "New customers by month", cats, Reference(inputs, min_col=3, min_row=hr, max_row=last), "F24")
    print_setup(d, b)


def project_plan(wb, b):
    ws = wb.active
    weeks = 16
    cols = 7 + weeks
    title_block(ws, b, "Plan", "Project plan", "One row per task. Set the plan start; the week columns shade themselves "
                "between each task's start and end.", cols, [5, 30, 14, 12, 12, 7, 13] + [4.2] * weeks)
    label(ws, 7, 1, "Plan start")
    ws.merge_cells("A7:B7")
    inp(ws, 7, 3, date.today(), DATE)
    hr = 9
    heads(ws, hr, ["ID", "Task", "Owner", "Start", "End", "Days", "Status"], height=30)
    for k in range(weeks):
        c = ws.cell(hr, 8 + k, "=$C$7+%d" % (7 * k))
        c.fill, c.font, c.number_format = HEAD_FILL, HEAD_FONT, "d mmm"
        c.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90)
    ws.row_dimensions[hr].height = 48
    tasks = [("Kick-off", 0, 0), ("Brief agreed", 1, 5), ("First version", 6, 20), ("Feedback", 21, 27),
             ("Final version", 28, 41), ("Launch", 42, 42)]
    n = 14
    for i in range(n):
        r = hr + 1 + i
        task = tasks[i] if i < len(tasks) else ("", None, None)
        body(ws, r, 1, i + 1)
        inp(ws, r, 2, task[0])
        inp(ws, r, 3, "[Name]" if task[0] else "")
        inp(ws, r, 4, "=$C$7+%d" % task[1] if task[1] is not None else None, SHORT_DATE)
        inp(ws, r, 5, "=$C$7+%d" % task[2] if task[2] is not None else None, SHORT_DATE)
        body(ws, r, 6, '=IF(AND(ISNUMBER(D%d),ISNUMBER(E%d)),E%d-D%d+1,"")' % (r, r, r, r))
        inp(ws, r, 7, "Not started" if task[0] else "")
        for k in range(weeks):
            c = ws.cell(r, 8 + k)
            c.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    listv(ws, "G%d:G%d" % (hr + 1, hr + n), STATUS, "Where the task is up to")
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
    rows = [[i + 1, "[Task]" if i == 0 else "", "[Name]" if i == 0 else "", "Medium" if i == 0 else "", None,
             "Not started" if i == 0 else "", ""] for i in range(10)]
    ws, t, hr, last = sheet(wb, b, "Tasks", "Actions", "Task and action tracker", "One row per action. Overdue rows "
                            "turn orange until they are done.", ["ID", "Task", "Owner", "Priority", "Due", "Status", "Notes"],
                            rows, validations=[("D", ["High", "Medium", "Low"], "How urgent"), ("F", STATUS, "Where it is up to")],
                            widths=[6, 40, 16, 12, 14, 14, 36], date_cols=(5,), first=True)
    ws.conditional_formatting.add("A%d:G%d" % (hr + 1, last + 200), FormulaRule(
        formula=['AND(ISNUMBER($E%d),$E%d<TODAY(),$F%d<>"Done")' % (hr + 1, hr + 1, hr + 1)],
        font=Font(color=B.ORANGE_DEEP, bold=True)))
    ws.conditional_formatting.add("A%d:G%d" % (hr + 1, last + 200), FormulaRule(
        formula=['$F%d="Done"' % (hr + 1)], fill=GREY_FILL))


def risk_register(wb, b):
    rows = []
    for i in range(8):
        r = 8 + i
        rows.append([i + 1, "[Risk]" if i == 0 else "", "Delivery" if i == 0 else "", "[Name]" if i == 0 else "",
                     3 if i == 0 else None, 3 if i == 0 else None,
                     '=IF(AND(ISNUMBER(E%d),ISNUMBER(F%d)),E%d*F%d,"")' % (r, r, r, r), "=" + BAND_FORMULA % (("G%d" % r,) * 4),
                     "[What is in place]" if i == 0 else "", "[What we will do]" if i == 0 else "", "Open" if i == 0 else "",
                     None])
    ws, t, hr, last = sheet(wb, b, "Risks", "Risks", "Risk register", "Score likelihood and impact 1 to 5. Score is the "
                            "product: Low 1 to 4, Medium 5 to 9, High 10 to 15, Critical 16 to 25.",
                            ["ID", "Risk", "Category", "Owner", "Likelihood", "Impact", "Score", "Band", "Controls in place",
                             "Action", "Status", "Review date"], rows,
                            validations=[("C", ["Delivery", "Finance", "People", "Legal", "Reputation", "Safety", "Technology"],
                                          "What kind of risk"), ("E", ["1", "2", "3", "4", "5"], "1 rare to 5 almost certain"),
                                         ("F", ["1", "2", "3", "4", "5"], "1 minor to 5 severe"),
                                         ("K", ["Open", "Monitoring", "Closed"], "Where it is up to")],
                            widths=[6, 34, 14, 14, 11, 9, 8, 10, 32, 32, 12, 14], date_cols=(12,), first=True)
    band_rules(ws, "H%d:H%d" % (hr + 1, last + 200))


def contact_list(wb, b):
    types = ["Partner", "Exhibitor", "Speaker", "Supplier", "Press", "Investor", "Public sector", "Other"]
    rows = [["[Name]", "[Role]", "[Organisation]", types[0], "[email]", "[phone]", "[Owner]", None, ""] for _ in range(8)]
    sheet(wb, b, "Contacts", "Contacts", "Contact and stakeholder list", "One row per person. Keep the owner and the last "
          "contact date current, and never share the sheet outside the team.",
          ["Name", "Role", "Organisation", "Type", "Email", "Phone", "Relationship owner", "Last contact", "Notes"], rows,
          validations=[("D", types, "Who they are to us")], widths=[20, 18, 22, 14, 26, 16, 18, 14, 34], date_cols=(8,),
          first=True)


def supplier_register(wb, b):
    rows = [["[Supplier]", "[Service]", "[Name]", "[email]", "[phone]", None, None, 0, None, "Active"] for _ in range(8)]
    ws, t, hr, last = sheet(wb, b, "Suppliers", "Suppliers", "Supplier register", "One row per supplier. Insurance and "
                            "contract dates in the past turn orange.",
                            ["Supplier", "Service", "Contact", "Email", "Phone", "Contract start", "Contract end", "Annual "
                             "value", "Insurance expiry", "Status"], rows,
                            validations=[("J", ["Active", "Under review", "Ended"], "Where the relationship is up to")],
                            widths=[22, 20, 18, 26, 16, 14, 14, 14, 14, 14], totals=[8], number_cols=(8,),
                            date_cols=(6, 7, 9), first=True)
    for col in ("G", "I"):
        ws.conditional_formatting.add("%s%d:%s%d" % (col, hr + 1, col, last + 200), FormulaRule(
            formula=['AND(ISNUMBER(%s%d),%s%d<TODAY())' % (col, hr + 1, col, hr + 1)],
            font=Font(color=B.ORANGE_DEEP, bold=True)))


def asset_register(wb, b):
    rows = [["[Tag]", "[Asset]", "Laptop", "[Location]", "[Name]", None, 0, "[Supplier]", "[Serial]", "Good", "In use"]
            for _ in range(8)]
    sheet(wb, b, "Assets", "Assets", "Asset and inventory register", "One row per item. Tag every asset and record who "
          "holds it.", ["Asset tag", "Asset", "Category", "Location", "Assigned to", "Purchase date", "Cost", "Supplier",
                        "Serial number", "Condition", "Status"], rows,
          validations=[("C", ["Laptop", "Phone", "Screen", "AV", "Furniture", "Signage", "Stock", "Other"], "What kind of asset"),
                       ("J", ["New", "Good", "Worn", "Faulty"], "Its condition"),
                       ("K", ["In use", "In store", "On loan", "Disposed"], "Where it is")],
          widths=[10, 24, 12, 16, 16, 14, 12, 18, 18, 12, 12], totals=[7], number_cols=(7,), date_cols=(6,), first=True)


def timesheet(wb, b):
    ws = wb.active
    title_block(ws, b, "Timesheet", "Weekly timesheet", "Times in 24 hours. Hours work themselves out from start, end "
                "and break.", 8, [12, 14, 9, 9, 9, 9, 22, 30])
    label(ws, 7, 1, "Name")
    inp(ws, 7, 2, "[Name]")
    label(ws, 8, 1, "Week starting")
    inp(ws, 8, 2, date.today() - timedelta(days=date.today().weekday()), DATE)
    hr = 10
    heads(ws, hr, ["Day", "Date", "Start", "End", "Break (min)", "Hours", "Project", "Notes"])
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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
    total_row(ws, tr, [6], text="Total hours")
    ws.cell(tr, 6, "=SUM(F%d:F%d)" % (hr + 1, hr + 7)).number_format = HOURS
    label(ws, tr + 2, 1, "Signed")
    inp(ws, tr + 2, 2, "[Signature and date]")
    label(ws, tr + 3, 1, "Approved")
    inp(ws, tr + 3, 2, "[Signature and date]")
    print_setup(ws, b)


def leave_planner(wb, b):
    ws = wb.active
    days = 31
    cols = 2 + days + 4
    title_block(ws, b, "Leave", "Holiday and leave planner", "One row per person, one sheet per month. Type a code "
                "in each day: H holiday, S sick, T training, W working from home, B bank holiday.", cols,
                [20, 10] + [3.6] * days + [9, 9, 9, 10])
    label(ws, 7, 1, "Month")
    inp(ws, 7, 2, date(date.today().year, date.today().month, 1), "mmm yyyy")
    label(ws, 7, 4, "Codes")
    ws.merge_cells(start_row=7, start_column=5, end_row=7, end_column=20)
    body(ws, 7, 5, "H holiday, S sick, T training, W working from home, B bank holiday", wrap=False)
    hr = 9
    head(ws, hr, 1, "Name")
    head(ws, hr, 2, "Allowance")
    for k in range(days):
        c = ws.cell(hr, 3 + k, '=IF(DAY($B$7+%d)=%d,$B$7+%d,"")' % (k, k + 1, k))
        c.fill, c.font, c.number_format = HEAD_FILL, HEAD_FONT, "d"
        c.alignment = Alignment(horizontal="center", vertical="center")
    for j, h in enumerate(["Holiday", "Sick", "Training", "Holiday left"]):
        head(ws, hr, 3 + days + j, h)
    ws.row_dimensions[hr].height = 30
    codes = ["H", "S", "T", "W", "B"]
    n = 12
    for i in range(n):
        r = hr + 1 + i
        inp(ws, r, 1, "[Name]" if i == 0 else "")
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
    listv(ws, rng, codes, "H, S, T, W or B")
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
    stages = ["Applied", "Screen", "Interview 1", "Interview 2", "Offer", "Hired", "Declined"]
    rows = [["[Role]", "[Candidate]", "[Where they came from]", stages[0], None, "[Next step]", None, "[Owner]", ""] for _ in range(8)]
    ws, t, hr, last = sheet(wb, b, "Candidates", "Hiring", "Recruitment tracker", "One row per candidate. Keep the next "
                            "step and its date current; nobody waits more than a week for an answer.",
                            ["Role", "Candidate", "Source", "Stage", "Applied", "Next step", "Next date", "Owner", "Notes"], rows,
                            validations=[("D", stages, "Where they are in the process")],
                            widths=[20, 20, 18, 14, 14, 26, 14, 14, 30], date_cols=(5, 7), first=True)
    s = wb.create_sheet("Summary")
    title_block(s, b, "Summary", "Candidates by stage", "", 8, [16, 12])
    heads(s, 7, ["Stage", "Candidates"])
    for i, st in enumerate(stages, 8):
        body(s, i, 1, st)
        body(s, i, 2, "=COUNTIFS(Candidates[Stage],$A%d)" % i)
    col_chart(s, "Candidates by stage", Reference(s, min_col=1, min_row=8, max_row=7 + len(stages)),
              Reference(s, min_col=2, min_row=7, max_row=7 + len(stages)), "D7")
    print_setup(s, b)


# ---------- events ----------

def speaker_tracker(wb, b):
    d = date(2027, 6, 30) if b == "Climb27" else None
    sess = [[d or "[Day]", "Main stage", "[Time]", "[Session title]", "Panel", "[Host]", "[Speakers]", "Invited"] for _ in range(6)]
    ws, t, hr, last = sheet(wb, b, "Sessions", "Agenda", "Sessions", "One row per session. Status moves from invited to "
                            "confirmed to briefed.", ["Day", "Stage", "Time", "Title", "Format", "Host", "Speakers", "Status"],
                            sess, validations=[("E", ["Talk", "Panel", "Fireside chat", "Roundtable", "Workshop", "Pitch"],
                                                "The session format"),
                                               ("H", ["Invited", "Confirmed", "Briefed", "Live", "Done"], "Where it is up to")],
                            widths=[14, 16, 10, 36, 14, 18, 32, 12], date_cols=(1,), first=True)
    yes = ["No"] * 7
    sp = [["[Name]", "[Company]", "[Role]", "[Session title]"] + yes for _ in range(8)]
    cols = ["Name", "Company", "Role", "Session", "Bio received", "Photo received", "Slides received", "Contract signed",
            "Travel needed", "Mobile captured", "Checked in"]
    ws2, t2, hr2, last2 = sheet(wb, b, "Speakers", "Speakers", "Speakers", "One row per speaker. Every column after Session "
                                "is Yes or No; the sheet is done when the last column is all Yes.", cols, sp,
                                validations=[(get_column_letter(c), YES_NO, "Yes or no") for c in range(5, 12)],
                                widths=[20, 20, 18, 30, 10, 10, 10, 10, 10, 10, 10])
    ws2.conditional_formatting.add("E%d:K%d" % (hr2 + 1, last2 + 200), CellIsRule(operator="equal", formula=['"Yes"'],
                                                                             fill=GREY_FILL, font=Font(color=B.CHARCOAL, bold=True)))


def critical_path(wb, b):
    streams = ["Site", "Agenda", "Partners", "Exhibitors", "Marketing", "Ticketing", "Production", "Staffing",
               "Health and safety"]
    ws = wb.active
    cols = 2 + len(streams)
    title_block(ws, b, "Critical path", "Production critical path", "Weeks to the event down the side, workstreams "
                "across. Set the event date; the week dates follow.", cols, [10, 12] + [20] * len(streams))
    label(ws, 7, 1, "Event date")
    ws.merge_cells("A7:A7")
    ev = date(2027, 6, 30) if b == "Climb27" else date.today() + timedelta(days=182)
    inp(ws, 7, 2, ev, DATE)
    hr = 9
    heads(ws, hr, ["Weeks to go", "Week of"] + streams, height=30)
    samples = {
        (26, "Site"): "Site confirmed and contract signed", (26, "Agenda"): "Theme and formats agreed",
        (26, "Ticketing"): "First release on sale", (26, "Marketing"): "Launch campaign live",
        (20, "Partners"): "Partner prospectus out", (20, "Agenda"): "Speaker invitations out",
        (16, "Exhibitors"): "Exhibitor sales open", (16, "Production"): "Stage and AV quotes in",
        (12, "Agenda"): "Agenda live on the website", (12, "Ticketing"): "Second release",
        (12, "Partners"): "Headline partner signed", (10, "Staffing"): "Crew and volunteers recruited",
        (8, "Exhibitors"): "Exhibitor manual sent", (8, "Health and safety"): "Risk assessment issued",
        (6, "Production"): "Production schedule signed off", (6, "Marketing"): "Final push starts",
        (4, "Exhibitors"): "Forms deadline", (4, "Agenda"): "Speaker briefs sent", (4, "Health and safety"): "Supplier RAMS in",
        (2, "Staffing"): "Staff briefing", (2, "Ticketing"): "Final release closes", (2, "Production"): "Run sheet locked",
        (1, "Site"): "Build day", (1, "Health and safety"): "Site induction", (0, "Site"): "Event days",
        (-1, "Site"): "Load-out and returns", (-1, "Marketing"): "Thank-you emails and recap",
    }
    weeks = list(range(26, -2, -1))
    for i, w in enumerate(weeks):
        r = hr + 1 + i
        body(ws, r, 1, w if w >= 0 else "Load-out", bold=True, align="center")
        body(ws, r, 2, "=$B$7-7*%d" % w, SHORT_DATE)
        for j, s in enumerate(streams):
            inp(ws, r, 3 + j, samples.get((w, s), ""))
    last = hr + len(weeks)
    ws.conditional_formatting.add("A%d:%s%d" % (hr + 1, get_column_letter(cols), last),
                                  FormulaRule(formula=['$A%d=0' % (hr + 1)], fill=TINT_FILL, font=Font(color=B.DARK, bold=True)))
    ws.freeze_panes = "C%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))
    ws.title = "Critical path"
    rows = [[26, "=$B$7-7*A8", "Site", "Site confirmed", "[Owner]", "Done"], [12, "=$B$7-7*A9", "Agenda", "Agenda live",
            "[Owner]", "In progress"], [4, "=$B$7-7*A10", "Exhibitors", "Forms deadline", "[Owner]", "Not started"]]
    ms, t, hr2, last2 = sheet(wb, b, "Milestones", "Milestones", "Milestones", "One row per milestone, with its owner and "
                              "status. B7 is the event date on the critical path sheet.",
                              ["Weeks to go", "Date", "Workstream", "Milestone", "Owner", "Status"], rows,
                              validations=[("C", streams, "Which workstream"), ("F", STATUS, "Where it is up to")],
                              widths=[12, 14, 18, 40, 16, 14], date_cols=(2,))
    for i in range(hr2 + 1, last2 + 1):
        ms.cell(i, 2, "='Critical path'!$B$7-7*A%d" % i)
    ms["B5"] = ""


def supplier_crew_tracker(wb, b):
    rows = [["[Supplier]", "[Service]", "[Name, phone]", "[Ref]", 0, "No", "=E8-IF(F8=\"Yes\",0,0)", "No"]]
    rows = []
    for i in range(8):
        r = 8 + i
        rows.append(["[Supplier]", "[Service]", "[Name, phone]", "[Ref]", 0, 0, "=IF(ISNUMBER(E%d),E%d-F%d,\"\")" % (r, r, r),
                     "No", "No"])
    sheet(wb, b, "Suppliers", "Suppliers", "Suppliers", "One row per supplier. Balance due is cost less deposit paid. "
          "Nobody works on site until insurance and RAMS are in.",
          ["Supplier", "Service", "Contact", "Booking ref", "Cost", "Deposit paid", "Balance due", "Insurance received",
           "RAMS received"], rows, validations=[("H", YES_NO, "Yes or no"), ("I", YES_NO, "Yes or no")],
          widths=[22, 20, 22, 12, 12, 12, 12, 12, 12], totals=[5, 6, 7], number_cols=(5, 6, 7), first=True)
    crew = [["[Name]", "Steward", "Main stage", None, None, "Crew", "No"] for _ in range(10)]
    sheet(wb, b, "Crew call sheet", "Crew", "Crew call sheet", "One row per person per day. Radio issued is ticked when "
          "they sign for it.", ["Name", "Role", "Zone", "Call time", "Finish time", "Pass type", "Radio issued"], crew,
          validations=[("B", ["Steward", "Registration", "Stage crew", "Runner", "Team lead", "Security", "First aid"], "Their role"),
                       ("F", ["Crew", "Staff", "Contractor", "Volunteer"], "The pass they wear"), ("G", YES_NO, "Yes or no")],
          widths=[22, 16, 18, 10, 10, 12, 12], time_cols=(4, 5))


def floor_plan(wb, b):
    rows = [["[A1]", "[3x2]", "Shell", "[Exhibitor]", "Blank", "", "Standard", "General", "No"] + ["No"] * 8 for _ in range(10)]
    forms = ["F%d %s" % (i, n) for i, n in enumerate(["Exhibitor form", "H and S", "Induction", "PAT", "Own H and S",
                                                      "Insurance", "Extras", "Panels"], 1)]
    ws, t, hr, last = sheet(wb, b, "Stands", "Expo", "Stand allocation", "One row per stand. The eight form columns "
                            "follow the exhibitor manual checklist.",
                            ["Stand", "Size", "Type", "Exhibitor", "Panels", "Extras ordered", "Power", "WiFi", "Paid"] + forms,
                            rows, validations=[("C", ["Shell", "Space only", "Pod"], "The stand type"),
                                               ("E", ["Blank", "Own build", "Printed", "Own print"], "The panel option"),
                                               ("G", ["Standard", "Extra", "None"], "Power ordered"),
                                               ("H", ["General", "Dedicated"], "WiFi")] +
                            [(get_column_letter(c), YES_NO, "Yes or no") for c in range(9, 18)],
                            widths=[8, 8, 10, 24, 10, 20, 10, 10, 8] + [7] * 8, first=True)
    ws.conditional_formatting.add("I%d:Q%d" % (hr + 1, last + 200), CellIsRule(operator="equal", formula=['"Yes"'],
                                                                          fill=GREY_FILL, font=Font(color=B.CHARCOAL, bold=True)))
    slots = []
    for i in range(10):
        r = 8 + i
        slots.append(["[Exhibitor]", 2, None, '=IF(ISNUMBER(C%d),C%d+TIME(0,30,0),"")' % (r, r), "Requested"])
    sheet(wb, b, "Setup slots", "Build-up", "Setup slots", "One row per booked slot. End is start plus 30 minutes "
          "unless you change it.", ["Exhibitor", "People", "Slot start", "Slot end", "Status"], slots,
          validations=[("E", ["Requested", "Confirmed", "Arrived", "Done"], "Where it is up to")],
          widths=[26, 8, 12, 12, 12], time_cols=(3, 4))
    vans = []
    for i in range(10):
        r = 8 + i
        vans.append(["[Exhibitor]", None, '=IF(ISNUMBER(B%d),B%d+TIME(0,15,0),"")' % (r, r), "[Driver]", "[Phone]", "[Reg]", ""])
    sheet(wb, b, "Vehicle unloading", "Build-up", "Vehicle unloading", "Slots of 15 minutes. Unload, then move the "
          "vehicle so the next one can pull in.",
          ["Exhibitor", "Slot start", "Slot end", "Driver name", "Driver phone", "Vehicle registration", "Notes"], vans,
          widths=[26, 12, 12, 18, 16, 14, 30], time_cols=(2, 3))
    g = wb.create_sheet("Block plan")
    title_block(g, b, "Block plan", "Block plan", "Type stand numbers into the grid. Each cell is one bay; shade walls "
                "and aisles with the Light Grey fill.", 22, [6] + [5] * 20)
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
    for r, c, v in ((8, 2, "A1"), (8, 3, "A2"), (10, 2, "B1"), (10, 3, "B2"), (8, 8, "Stage")):
        g.cell(r, c, v)
    for k in range(20):
        g.cell(13, 2 + k).fill = GREY_FILL
    print_setup(g, b)


def staff_rota(wb, b):
    rows = []
    zones = ["Registration", "Main stage", "Expo", "Roundtable rooms", "Green room"]
    for i in range(12):
        r = 8 + i
        rows.append(["Day one" if i < 6 else "Day two", zones[i % 5], "Steward", "[Name]", None, None, 30,
                     '=IF(AND(ISNUMBER(E%d),ISNUMBER(F%d)),ROUND((F%d-E%d)*24-G%d/60,2),"")' % (r, r, r, r, r), "[Lead]", "No"])
    ws, t, hr, last = sheet(wb, b, "Shifts", "Rota", "Staff and volunteer rota", "One row per shift. Hours work "
                            "themselves out from start, end and break.",
                            ["Day", "Zone", "Role", "Name", "Start", "End", "Break (min)", "Hours", "Team lead", "Radio"],
                            rows, validations=[("A", ["Build day", "Day one", "Day two", "Load-out"], "Which day"),
                                               ("B", zones + ["Everywhere"], "Which zone"),
                                               ("C", ["Steward", "Registration", "Stage crew", "Runner", "Team lead", "Floater"],
                                                "Their role"), ("J", YES_NO, "Radio issued")],
                            widths=[12, 18, 14, 20, 9, 9, 11, 9, 16, 9], time_cols=(5, 6), first=True)
    for i in range(hr + 1, last + 1):
        ws.cell(i, 8).number_format = HOURS
    s = wb.create_sheet("By person")
    title_block(s, b, "Summary", "Hours by person", "Type each name once; shifts and hours come from the rota.", 8,
                [22, 10, 10])
    heads(s, 7, ["Name", "Shifts", "Hours"])
    for i in range(8, 28):
        inp(s, i, 1, "[Name]" if i == 8 else "")
        body(s, i, 2, '=IF(A%d="","",COUNTIFS(Shifts[Name],A%d))' % (i, i))
        body(s, i, 3, '=IF(A%d="","",SUMIFS(Shifts[Hours],Shifts[Name],A%d))' % (i, i), HOURS)
    print_setup(s, b)


def feedback_results(wb, b):
    qs = [["Q1", "How likely are you to recommend the event to a colleague?", "Score 1 to 10"],
          ["Q2", "How useful were the sessions you went to?", "Score 1 to 5"],
          ["Q3", "How useful were the people you met?", "Score 1 to 5"],
          ["Q4", "How easy was the day to get around?", "Score 1 to 5"],
          ["Q5", "How likely are you to come next year?", "Score 1 to 5"],
          ["Q6", "What should we keep, change or try?", "Free text"]]
    sheet(wb, b, "Questions", "Survey", "Questions", "One row per question. The responses sheet has one column per "
          "scored question.", ["ID", "Question", "Type"], qs, widths=[8, 60, 16], first=True)
    resp = [["[Respondent]", None, "Attendee", None, None, None, None, None, ""] for _ in range(10)]
    r_ws, t, hr, last = sheet(wb, b, "Responses", "Survey", "Responses", "One row per response, scores only. Comments "
                              "are copied to the comments sheet and tagged by theme.",
                              ["Respondent", "Date", "Type", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6 comment"], resp,
                              validations=[("C", ["Attendee", "Speaker", "Partner", "Exhibitor", "Crew"], "Who answered")],
                              widths=[18, 14, 12, 8, 8, 8, 8, 8, 50], date_cols=(2,))
    s = wb.create_sheet("Summary", 0)
    title_block(s, b, "Summary", "Feedback results", "Averages and counts from the responses sheet.", 8, [10, 50, 12, 12])
    heads(s, 7, ["ID", "Question", "Average", "Responses"])
    for i, q in enumerate(qs[:5], 8):
        body(s, i, 1, q[0])
        body(s, i, 2, q[1])
        body(s, i, 3, '=IFERROR(AVERAGE(Responses[%s]),"")' % q[0], "0.0")
        body(s, i, 4, "=COUNT(Responses[%s])" % q[0])
    col_chart(s, "Average score by question", Reference(s, min_col=1, min_row=8, max_row=12),
              Reference(s, min_col=3, min_row=7, max_row=12), "F7")
    print_setup(s, b)
    sheet(wb, b, "Comments", "Survey", "Comments", "One row per comment, with a theme so the report can count them.",
          ["Respondent", "Comment", "Theme", "Quote in the report"],
          [["[Respondent]", "[Comment]", "Sessions", "No"] for _ in range(8)],
          validations=[("C", ["Sessions", "Networking", "Site", "Food and drink", "Expo", "Agenda", "Other"], "The theme"),
                       ("D", YES_NO, "Consent to quote")], widths=[18, 70, 16, 14])


def exhibitor_risk_assessment(wb, b):
    ed = edition(b)
    r = wb.active
    title_block(r, b, "Read me", "Exhibitor and partner risk assessment", "Five steps, then the risk register sheet.", 4,
                [6, 90])
    steps = ["Complete your details at the top of the risk register sheet.",
             "Each row is one hazard, not one item. Work left to right: what could go wrong, who it could harm, what you "
             "already do, what you will add for this event.",
             "Add rows for anything unusual: games, interactive experiences, food or drink, machines or moving parts.",
             "Score likelihood and severity before and after your controls. The score, the band and what to do about it "
             "work themselves out.",
             "Check it before you submit, and update it if your plans change. Send it to %s by the deadline in your "
             "contract." % B.BRANDS[b]["email"].replace("marketing", "exhibitors")]
    for i, s in enumerate(steps):
        body(r, 7 + i, 1, i + 1, bold=True, align="center")
        body(r, 7 + i, 2, s)
        r.row_dimensions[7 + i].height = 32
    label(r, 13, 1, "Likelihood")
    for i, l in enumerate(LIKELIHOOD):
        body(r, 14 + i, 2, l)
    label(r, 20, 1, "Severity")
    for i, s in enumerate(SEVERITY):
        body(r, 21 + i, 2, s)
    label(r, 27, 1, "Bands")
    for i, (band, what) in enumerate([("Low 1 to 4", "Acceptable. Keep the controls in place."),
                                       ("Medium 5 to 9", "Acceptable with the controls in place. Check them each day."),
                                       ("High 10 to 15", "Add controls to bring this down before the event, and tell us."),
                                       ("Critical 16 to 25", "Do not run this activity as planned. Add controls and talk to us "
                                                             "first.")]):
        body(r, 28 + i, 2, "%s: %s" % (band, what))
    print_setup(r, b, landscape=False)
    ws = wb.create_sheet("Risk register")
    cols = 18
    title_block(ws, b, "Risk register", "Your stand at %s" % ed, "One row per hazard. Columns J, K, N and O work "
                "themselves out.", cols, [16, 22, 22, 18, 20, 36, 30, 10, 10, 9, 10, 10, 10, 9, 10, 16, 12, 26])
    details = [("Company", "[Company]"), ("Event", "%s, %s" % (ed, B.BRANDS[b]["edition"] or "[Dates]")),
               ("Stand", "[Stand number]"), ("Contact name", "[Name]"), ("Email", "[email]"), ("Phone", "[phone]"),
               ("Date", "[Date]"), ("Completed by", "[Name]")]
    for i, (k, v) in enumerate(details):
        label(ws, 7 + i // 2, 1 + 2 * (i % 2), k)
        inp(ws, 7 + i // 2, 2 + 2 * (i % 2), v)
    label(ws, 12, 1, "Matrix")
    body(ws, 12, 2, "Likelihood 1 Rare, 2 Unlikely, 3 Possible, 4 Likely, 5 Almost certain. Severity 1 Minor injury or "
                    "inconvenience, 2 First aid required, 3 Injury requiring medical treatment, 4 Serious injury, 5 Major "
                    "injury or fatality. Score is likelihood times severity: Low 1 to 4, Medium 5 to 9, High 10 to 15, "
                    "Critical 16 to 25.", wrap=True)
    ws.merge_cells(start_row=12, start_column=2, end_row=12, end_column=12)
    ws.row_dimensions[12].height = 44
    hr = 14
    heads(ws, hr, ["Area or activity", "Item or task", "Hazard", "Who could be harmed", "Potential harm", "Existing controls",
                   "Additional controls for this event", "Likelihood before", "Severity before", "Risk score before",
                   "Risk band before", "Likelihood after", "Severity after", "Residual score", "Residual band",
                   "Person responsible", "Status", "Notes or evidence"], height=40)
    hazards = [
        ("Visitors", "Moving in, out and around your space", "Congestion or blocked routes", "Visitors and your team",
         "Trips, falls or collisions", "Layout leaves a clear way in and out. The team watches numbers and pauses an "
         "activity if it gets too busy.", 2, 2),
        ("Visitors", "Hands-on demos and queues", "Crowding at the stand", "Visitors", "Trips and collisions",
         "Queues stay inside the space. One team member manages the queue.", 2, 2),
        ("Layout", "Your space and its footprint", "Items or queues spilling into aisles or blocking exits",
         "Visitors, other exhibitors and your team", "Trips, or a slower evacuation in an emergency", "Everything stays "
         "inside the space you were given. Aisles, exits, fire points and extinguishers are never blocked.", 2, 3),
        ("Your team", "Long days on your feet", "Tiredness and dehydration", "Your team", "Lower awareness, fainting, "
         "minor injury", "A break rota, water on the stand and enough people to cover breaks.", 2, 1),
        ("Your team", "People working in your space", "Not knowing the layout, the risks or the emergency plan",
         "Your team and visitors", "Unsafe behaviour, a slow response in an emergency", "Everyone is briefed before doors "
         "open: this assessment, the nearest fire exits, the evacuation signal and how to call for first aid.", 2, 3),
        ("Set up and break down", "Lifting and moving equipment or stock", "Heavy or awkward loads", "Your team and "
         "contractors", "Strains, sprains and back injury", "Trolleys for heavy items. Two people for anything awkward. "
         "Loads split into smaller boxes.", 2, 2),
        ("Set up and break down", "Custom structures", "Collapse or falling items", "Your team and visitors",
         "Serious injury", "Designed and built by a competent contractor, with calculations or certificates.", 1, 4),
        ("Interactive activity", "Games, challenges and competitions", "Crowding, over-excitement or misuse", "Visitors",
         "Trips, collisions, minor injury", "Clear rules on display. A team member runs the activity. The queue stays "
         "inside the space.", 2, 2),
        ("Housekeeping", "Cables, flooring edges, boxes and bags", "Trip hazards inside your space", "Your team and "
         "visitors", "Trips and falls", "Cables run behind the stand or under cable covers. Flooring edges are taped "
         "down. Bags and boxes are stored out of the way.", 2, 2),
        ("Housekeeping", "Drinks, waste and spills", "Wet or slippery floor", "Your team and visitors", "Slips and falls",
         "Spills are cleaned straight away. Waste is cleared through the day.", 2, 2),
        ("Housekeeping", "Stock, packaging and spare equipment", "Poorly stacked items or storage in walkways",
         "Your team and visitors", "Items falling, trips", "Stock is stacked low and steady inside the space. Packaging "
         "goes to the agreed storage area, not behind the stand.", 2, 2),
        ("Electrical", "Power and data cables", "Trailing or damaged cables", "Your team and visitors", "Trips, electric "
         "shock", "Cables are checked before use, routed safely and covered where people walk.", 2, 3),
        ("Electrical", "Screens, laptops, lighting and chargers", "Faulty electrical equipment", "Your team and visitors",
         "Electric shock or fire", "Equipment is in good condition and tested (PAT), or booked for testing on site. "
         "Anything damaged is taken out of use.", 1, 4),
        ("Electrical", "Extension leads and power supply", "Overloaded sockets or daisy-chained leads", "Your team and "
         "visitors", "Fire", "Power use stays within the supply you ordered. No extension leads plugged into each other. "
         "Power is off at the end of each day.", 1, 4),
        ("Demonstrations", "Live product demos", "Unsafe use, or visitors too close", "Your team and visitors",
         "Minor injury", "Demos are run by trained team members, with a clear area around the demo.", 2, 2),
        ("Demonstrations", "Machines, props or anything with moving parts", "Contact with moving parts", "Your team and "
         "visitors", "Crush, cut or trapping injuries", "Guards stay on. A barrier or distance keeps visitors back. "
         "Supervised at all times and switched off when no one is with it.", 2, 3),
        ("Demonstrations", "Stock and giveaways on display", "Items falling, distraction while demonstrating", "Visitors",
         "Minor injury", "Stock kept in a tidy, low stack. One person demonstrates while another watches the stand.", 2, 1),
        ("Food and drink", "Serving food or samples", "Contamination, poor hygiene or allergens", "Visitors",
         "Food poisoning or an allergic reaction", "Food handlers are trained. Hand washing or sanitiser at the serving "
         "point. Allergen information is on display for every item.", 2, 3),
        ("Food and drink", "Hot drinks, hot food and kitchen equipment", "Heat, steam and hot surfaces", "Your team and "
         "visitors", "Burns and scalds", "Hot equipment sits at the back, out of reach. Lids on hot drinks. Equipment "
         "used as the maker intends.", 2, 2),
        ("Food and drink", "Storing food", "Food kept at the wrong temperature", "Visitors", "Food poisoning",
         "Chilled food kept chilled and hot food kept hot, with temperatures checked and noted.", 2, 3),
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
        inp(ws, r_, 16, "[Name]" if i < len(hazards) else "")
        inp(ws, r_, 17, "Open" if i < len(hazards) else "")
        inp(ws, r_, 18, "")
        ws.row_dimensions[r_].height = 58 if i < len(hazards) else 30
    last = hr + n
    for col in ("H", "I", "L", "M"):
        listv(ws, "%s%d:%s%d" % (col, hr + 1, col, last + 100), ["1", "2", "3", "4", "5"], "1 to 5")
    listv(ws, "Q%d:Q%d" % (hr + 1, last + 100), ["Open", "In progress", "Done"], "Where the controls are up to")
    band_rules(ws, "K%d:K%d" % (hr + 1, last + 100))
    band_rules(ws, "O%d:O%d" % (hr + 1, last + 100))
    ws.freeze_panes = "D%d" % (hr + 1)
    print_setup(ws, b, title_rows="%d:%d" % (hr, hr))
    label(ws, last + 2, 1, "Signed")
    inp(ws, last + 2, 2, "[Name and date]")


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
    """Every string a reader sees in the workbooks, for the copy checker: build each book in memory and walk the cells."""
    from openpyxl import Workbook
    out = []
    for b in brands:
        for name, fn in BOOKS.items():
            wb = Workbook()
            fn(wb, b)
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for c in row:
                        if isinstance(c.value, str) and not c.value.startswith("="):
                            out.append(c.value)
                for dv in ws.data_validations.dataValidation:
                    out.append(dv.prompt or "")
                for ch in ws._charts:
                    pass
    return out
