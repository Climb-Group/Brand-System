"""The catalogue of Office templates: one row per template, naming its app, the brands that get it and the group it
belongs to. The builders, the previews and the package read this table, so adding a template is one row plus its
content, never a new hand-written function per file.

Columns:
    app        word, excel or powerpoint
    name       the file stem after the brand (ClimbUK_<name>.dotx), hyphenated
    title      what people call it
    brands     the brands that get it ("3" in the brief is ALL, "UK+Group" is UKG)
    group      Company (any business) or Events (the events business), for the READMEs and the previews
    external   True for the co-branded versions people outside the company fill in; they live in <Brand>/external/
    original   True for the first template set (built by the hand-written functions, never remade)
"""
ALL = ("ClimbUK", "ClimbGroup", "Climb27")
UKG = ("ClimbUK", "ClimbGroup")

EXT = {"word": "dotx", "excel": "xltx", "powerpoint": "potx"}
DOC_EXT = {"word": "docx", "excel": "xlsx", "powerpoint": "pptx"}
LO_EXT = {"dotx": "ott", "xltx": "ots", "potx": "otp"}


def t(app, name, title, brands=ALL, group="Company", external=False, original=False):
    return dict(app=app, name=name, title=title, brands=brands, group=group, external=external, original=original)


TEMPLATES = [
    # The first set.
    t("word", "Letterhead", "Letterhead", original=True),
    t("word", "Report", "Report", original=True),
    t("word", "Proposal", "Proposal", original=True),
    t("word", "Press-release", "Press release", original=True),
    t("word", "Meeting-notes", "Meeting notes", original=True),
    t("excel", "Event-budget", "Event budget", group="Events", original=True),
    t("excel", "Partner-pipeline", "Partner pipeline", group="Events", original=True),
    t("excel", "Run-sheet", "Run sheet", group="Events", original=True),
    t("excel", "Content-calendar", "Content calendar", group="Events", original=True),
    t("powerpoint", "Presentation_16x9", "Presentation 16:9", original=True),
    # Word, any company.
    t("word", "Memo", "Memo"),
    t("word", "Contract", "Contract"),
    t("word", "Partnership-agreement", "Partnership agreement", group="Events"),
    t("word", "Award-sponsorship-agreement", "Award sponsorship agreement", group="Events"),
    t("word", "Exhibitor-agreement", "Exhibitor agreement", group="Events"),
    t("word", "Non-disclosure-agreement", "Non-disclosure agreement"),
    t("word", "Statement-of-work", "Statement of work", UKG),
    t("word", "Business-plan", "Business plan"),
    t("word", "Policy", "Policy document"),
    t("word", "Standard-operating-procedure", "Standard operating procedure"),
    t("word", "Job-description", "Job description", UKG),
    t("word", "Offer-letter", "Offer letter", UKG),
    t("word", "Employee-handbook", "Employee handbook", UKG),
    t("word", "Brief", "Project or creative brief", UKG),
    t("word", "Case-study", "Case study"),
    t("word", "Fact-sheet", "One-page fact sheet"),
    t("word", "Newsletter", "Newsletter"),
    t("word", "Certificate", "Certificate (award, completion, appreciation)"),
    t("word", "Board-report", "Board report", UKG),
    t("word", "Terms-and-conditions", "Terms and conditions"),
    # Word, events.
    t("word", "Post-event-report", "Post-event report", group="Events"),
    t("word", "Exhibitor-manual", "Exhibitor manual", group="Events"),
    t("word", "Speaker-brief", "Speaker brief", group="Events"),
    t("word", "Host-brief", "Host brief", group="Events"),
    t("word", "Event-risk-assessment", "Event risk assessment and method statement", group="Events"),
    t("word", "Event-day-pack", "Event day pack", group="Events"),
    t("word", "Attendance-certificate", "Attendance certificate", group="Events"),
    t("word", "Exhibitor-risk-assessment", "Exhibitor and partner risk assessment", group="Events", external=True),
    # Excel, any company.
    t("excel", "Invoice", "Invoice"),
    t("excel", "Quote", "Quote or estimate"),
    t("excel", "Purchase-order", "Purchase order"),
    t("excel", "Annual-budget", "Annual budget", UKG),
    t("excel", "Cash-flow-forecast", "Cash flow forecast", UKG),
    t("excel", "Profit-and-loss", "Profit and loss tracker"),
    t("excel", "Expense-claim", "Expense claim"),
    t("excel", "KPI-dashboard", "KPI dashboard"),
    t("excel", "Project-plan", "Project plan (Gantt)"),
    t("excel", "Task-tracker", "Task and action tracker"),
    t("excel", "Risk-register", "Risk register"),
    t("excel", "Contact-list", "Contact and stakeholder list"),
    t("excel", "Supplier-register", "Supplier register", UKG),
    t("excel", "Asset-register", "Asset and inventory register", UKG),
    t("excel", "Timesheet", "Timesheet"),
    t("excel", "Leave-planner", "Holiday and leave planner", UKG),
    t("excel", "Recruitment-tracker", "Recruitment tracker", UKG),
    # Excel, events.
    t("excel", "Speaker-tracker", "Speaker and session tracker", group="Events"),
    t("excel", "Critical-path", "Production critical path", group="Events"),
    t("excel", "Supplier-crew-tracker", "Supplier and crew tracker", group="Events"),
    t("excel", "Floor-plan", "Floor plan and stand allocation", group="Events"),
    t("excel", "Staff-rota", "Staff and volunteer rota", group="Events"),
    t("excel", "Feedback-results", "Feedback survey results", group="Events"),
    t("excel", "Exhibitor-risk-assessment", "Exhibitor and partner risk assessment", group="Events", external=True),
    # PowerPoint, any company.
    t("powerpoint", "Investor-pitch-deck", "Investor pitch deck"),
    t("powerpoint", "Sales-deck", "Sales deck"),
    t("powerpoint", "Quarterly-business-review", "Quarterly business review", UKG),
    t("powerpoint", "Board-presentation", "Board presentation", UKG),
    t("powerpoint", "Project-kick-off", "Project kick-off", UKG),
    t("powerpoint", "Training-deck", "Training and onboarding deck", UKG),
    t("powerpoint", "All-hands", "All-hands update"),
    t("powerpoint", "Org-chart", "Org chart"),
    # PowerPoint, events.
    t("powerpoint", "Partner-prospectus", "Partner prospectus", group="Events"),
    t("powerpoint", "Stage-holding-slides", "Stage holding slides", group="Events"),
    t("powerpoint", "Speaker-slides", "Speaker slide template", group="Events"),
    t("powerpoint", "Investor-pitch-deck", "Investor pitch deck (for founders pitching at the event)", external=True),
    t("powerpoint", "Stage-holding-slides", "Stage holding slides (for a partner stage)", group="Events", external=True),
    t("powerpoint", "Speaker-slides", "Speaker slide template (with the speaker's own logo)", group="Events", external=True),
]


def rows(app=None, brand=None, external=None, original=None, group=None):
    out = []
    for r in TEMPLATES:
        if app and r["app"] != app:
            continue
        if brand and brand not in r["brands"]:
            continue
        if external is not None and r["external"] != external:
            continue
        if original is not None and r["original"] != original:
            continue
        if group and r["group"] != group:
            continue
        out.append(r)
    return out


def stem(brand, row):
    """The file stem: ClimbUK_Memo, or ClimbUK_External-Speaker-slides for a co-branded version."""
    return "%s_%s%s" % (brand, "External-" if row["external"] else "", row["name"])


def folder(brand, row):
    """The folder under templates/office for this file."""
    return "%s/%s" % (brand, "external" if row["external"] else row["app"])
