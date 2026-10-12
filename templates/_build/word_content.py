"""The content of every Word template added after the first set, as data the renderer in word_build.py lays out.

Each entry in DOCS is keyed by the catalogue name and holds:
    kind        "plain" (standard header on every page), "cover" (Dark Brown photo cover, then inner pages),
                "landscape" (A4 landscape, used by the certificates) or "landscape-plain"
    label       the document label in the running header (and the cover sticker for "cover")
    title       the cover or first-page title; {word} is orange, _word_ is italic
    sub, meta   the cover lines ("cover" only)
    blocks(b)   a function of the brand name returning the block list

Blocks (tuples, first item is the block type):
    ("eyebrow", text)            ("title", text)             ("sub", text)              ("lead", text)
    ("h1", text) ("h2", text) ("h3", text)                   ("p", text)                ("bullets", [..])
    ("numbers", [..])            ("callout", text)           ("quote", text, source)    ("big", number, text)
    ("kv", [(key, value), ..])   ("table", [header], [rows], [widths cm] or None)
    ("clauses", [(heading, note), ..], start)                ("sign", [party, ..])      ("sigline", who)
    ("checklist", [..])          ("small", text)             ("page",)                  ("toc",)
    ("merge", [(label, field), ..])  a line of mail merge fields (certificates)

Sample copy follows the climb-voice skill and passes check_copy.py (python3 word_build.py --copy prints it all).
No venue, no names, no numbers as promises: every fact a person must fill in is a [slot].
"""
import brand as B

LEGAL_PARTY = "The Investor Ladder Limited, trading as ClimbGroup (\"ClimbGroup\")"
PARTNER_EMAIL = "partnerships@climb-uk.com"
EXHIBITOR_EMAIL = "exhibitors@climb-uk.com"
SPEAKER_EMAIL = "speakers@climb-uk.com"


def edition(b):
    """The event name for event pieces: the edition when the brand is one, else a slot."""
    return b if B.BRANDS[b]["edition"] else "[Edition]"


def event_dates(b):
    return B.BRANDS[b]["edition"] or "[Dates]"


def host_line(b, verb="Speaking at"):
    return "%s %s" % (verb, "a ClimbGroup event" if b == "ClimbGroup" else b)


APPROVED = "[Approved clause text]"

# The clause set shared by the event agreements (partnership, award sponsorship, exhibitor).
EVENT_CLAUSES = [
    ("Definitions and interpretation", "What each capitalised term means, and how to read the agreement."),
    ("Fees and payment", "The fee in Schedule 1, invoiced on signature and payable within 14 days of the invoice date."),
    ("Each party's obligations", "What each side does, by when, and the information each gives the other."),
    ("Host obligations", "Promote the partner, feature their mark, keep them informed and co-operate. No particular "
                         "result is assured."),
    ("Changes", "A change is sent on the change request form, reviewed within 48 hours, and none is made within 72 "
                "hours of the event. At most 5 changes."),
    ("Limitation of liability", "What each party is and is not liable for, and the cap."),
    ("Termination", "When either party may end the agreement, and the notice needed."),
    ("Cancellation by the partner", "The sliding scale in the table below applies to written notice."),
    ("Consequences of termination", "What is paid, returned and taken down when the agreement ends."),
    ("Anti-bribery and compliance", "Each party complies with the Bribery Act 2010 and keeps its own policies."),
    ("Intellectual property and use of marks", "Each party keeps its own marks and licenses them only for this event."),
    ("Data protection", "How attendee and contact data is handled under UK GDPR, and who is the controller."),
    ("Force majeure", "What happens when something outside either party's control stops the event."),
    ("General", "Whole agreement, variation, waiver, assignment, notices, third parties, law and jurisdiction."),
]

CANCELLATION = ("table", ["Written notice received", "Share of the fee payable"],
                [["More than [180] days before the event", "[25]%"], ["[120] to [180] days before the event", "[50]%"],
                 ["[60] to [119] days before the event", "[75]%"], ["Fewer than [60] days before the event", "100%"]],
                [10.0, 6.6])

PACKAGE_SCHEDULE = [("Package", "[Package name]"), ("Event", "[Edition and dates]"), ("Fee", "[Amount] plus VAT"),
                    ("Invoice date", "[Date]"), ("Payment due", "14 days from the invoice date"),
                    ("Partner contact", "[Name, role, email]"), ("Host contact", "[Name, role, email]")]


def event_agreement(kind, party, deliverables):
    def blocks(b):
        ed = edition(b)
        return [
            ("eyebrow", "%s agreement" % kind),
            ("title", "%s {agreement}" % kind),
            ("sub", "Between ClimbGroup and [Company name] for %s." % ed),
            ("kv", [("Parties", "%s and [Company name], registered in [Country] under number [Number], of [Address] "
                                "(\"the %s\")" % (LEGAL_PARTY, party)),
                    ("Event", "%s, %s" % (ed, event_dates(b))), ("Agreement date", "[Date]"),
                    ("Schedules", "1 Package details, 2 Deliverables")]),
            ("p", "This agreement sets out what the %s books, what ClimbGroup provides and what each side does. "
                  "Clause headings are fixed; the approved wording for each clause goes under its heading." % party),
            ("clauses", EVENT_CLAUSES, 1),
            ("h3", "Cancellation scale (clause 8)"),
            CANCELLATION,
            ("page",),
            ("h1", "Schedule 1: Package details"),
            ("kv", PACKAGE_SCHEDULE),
            ("h1", "Schedule 2: Deliverables"),
            ("table", ["Deliverable", "Detail", "By when", "Owner"], deliverables, [5.0, 6.4, 2.6, 2.6]),
            ("sign", ["ClimbGroup", "The %s" % party]),
        ]
    return blocks


PARTNER_DELIVERABLES = [["Branding", "[Mark on the website, stage screens and signage]", "[Date]", "ClimbGroup"],
                        ["Stage or panel slot", "[Format, stage, length]", "On the day", "Both"],
                        ["Expo space", "[Stand number and size]", "Build day", "ClimbGroup"],
                        ["Delegate passes", "[Number] passes", "[Date]", "ClimbGroup"],
                        ["Drinks reception tickets", "[Number] tickets", "[Date]", "ClimbGroup"],
                        ["Agenda listing", "[Where the partner appears]", "[Date]", "ClimbGroup"],
                        ["Partner assets", "Logo files, session title, speaker details", "[Date]", "The Partner"]]
AWARD_DELIVERABLES = [["Award category", "[Category name] presented by [Company]", "Awards night", "Both"],
                      ["Stage moment", "The partner presents the award on the main stage", "Awards night", "Both"],
                      ["Branding", "[Mark on the award, the screens and the awards page]", "[Date]", "ClimbGroup"],
                      ["Judging", "[A seat on the judging panel]", "[Date]", "Both"],
                      ["Tickets", "[Number] awards tickets", "[Date]", "ClimbGroup"],
                      ["Partner assets", "Logo files, presenter name and bio", "[Date]", "The Sponsor"]]
EXHIBITOR_DELIVERABLES = [["Stand", "[Stand number, size and type] with the standard fit-out", "Build day", "ClimbGroup"],
                          ["Listing", "[Company] in the exhibitor list and the app", "[Date]", "ClimbGroup"],
                          ["Passes", "[Number] exhibitor passes", "[Date]", "ClimbGroup"],
                          ["Forms", "Exhibitor form, health and safety and site induction acknowledgements, risk "
                                    "assessment, insurance", "[Date]", "The Exhibitor"],
                          ["Extras", "[Ordered extras from the exhibitor manual]", "[Date]", "Both"]]


def contract(b):
    return [
        ("eyebrow", "Agreement"),
        ("title", "[Services] {agreement}"),
        ("sub", "Between ClimbGroup and [Company name]."),
        ("kv", [("Parties", "%s and [Company name], registered in [Country] under number [Number], of [Address] "
                            "(\"the Supplier\")" % LEGAL_PARTY),
                ("Agreement date", "[Date]"), ("Term", "From [Start date] to [End date]"),
                ("Schedules", "1 Services, 2 Fees")]),
        ("p", "This agreement sets out the services, the fees and what each side does. Clause headings are fixed; the "
              "approved wording for each clause goes under its heading."),
        ("clauses", [
            ("Definitions and interpretation", "What each capitalised term means, and how to read the agreement."),
            ("Term", "When the agreement starts and ends, and how it renews."),
            ("Services", "What is supplied, to what standard, and by when (Schedule 1)."),
            ("Fees and payment", "The fees in Schedule 2, invoiced [monthly] and payable within 14 days of the invoice "
                                 "date."),
            ("Each party's obligations", "What each side does and the information each gives the other."),
            ("Changes", "How a change to the services or the fees is requested, reviewed and agreed in writing."),
            ("Limitation of liability", "What each party is and is not liable for, and the cap."),
            ("Termination", "When either party may end the agreement, and the notice needed."),
            ("Consequences of termination", "What is paid, returned and handed over when the agreement ends."),
            ("Anti-bribery and compliance", "Each party complies with the Bribery Act 2010 and keeps its own policies."),
            ("Intellectual property", "Who owns what is created, and the licence each party gets."),
            ("Confidentiality", "What stays confidential, for how long, and the exceptions."),
            ("Data protection", "How personal data is handled under UK GDPR, and who is the controller."),
            ("Force majeure", "What happens when something outside either party's control stops performance."),
            ("General", "Whole agreement, variation, waiver, assignment, notices, third parties, law and jurisdiction."),
        ], 1),
        ("page",),
        ("h1", "Schedule 1: Services"),
        ("table", ["Service", "Standard", "By when"], [["[Service]", "[What good looks like]", "[Date]"],
                                                       ["[Service]", "[What good looks like]", "[Date]"]], [6.0, 7.6, 3.0]),
        ("h1", "Schedule 2: Fees"),
        ("table", ["Item", "Fee", "When invoiced"], [["[Item]", "[Amount] plus VAT", "[On signature]"],
                                                     ["[Item]", "[Amount] plus VAT", "[Monthly]"]], [7.0, 5.0, 4.6]),
        ("sign", ["ClimbGroup", "The Supplier"]),
    ]


def nda(b):
    return [
        ("eyebrow", "Non-disclosure agreement"),
        ("title", "Non-disclosure {agreement}"),
        ("sub", "Between ClimbGroup and [Company or person]."),
        ("kv", [("Parties", "%s and [Company or person], of [Address] (\"the Recipient\")" % LEGAL_PARTY),
                ("Purpose", "[Why information is being shared, in one line]"),
                ("Agreement date", "[Date]"), ("Term", "[Number] years from the agreement date")]),
        ("p", "This is a mutual agreement: each party may share confidential information with the other for the "
              "purpose above, and each keeps what it receives confidential."),
        ("clauses", [
            ("Definitions", "What counts as confidential information, and what the purpose is."),
            ("Confidential information", "Everything marked confidential, and anything a reasonable person would treat "
                                         "as confidential, in any form."),
            ("Obligations of the receiving party", "Use it only for the purpose, share it only with people who need it "
                                                   "and are bound the same way, and keep it secure."),
            ("Exceptions", "Information that is public, already known, independently developed or required by law."),
            ("Return or destruction", "On request or at the end of the term, return or destroy it and confirm in "
                                      "writing."),
            ("Term", "How long the obligations last, including after the agreement ends."),
            ("Remedies", "Each party may seek an injunction as well as damages."),
            ("General", "Whole agreement, variation, assignment, notices, law and jurisdiction."),
        ], 1),
        ("sign", ["ClimbGroup", "The Recipient"]),
    ]


def statement_of_work(b):
    return [
        ("eyebrow", "Statement of work"),
        ("title", "[Project] statement of {work}"),
        ("sub", "What we will deliver, by when and for how much."),
        ("kv", [("Client", "[Company name]"), ("Supplier", "ClimbGroup"), ("Owner", "[Name, role]"),
                ("Start", "[Date]"), ("End", "[Date]"), ("Reference", "[Agreement or purchase order number]")]),
        ("h1", "Overview"),
        ("lead", "One paragraph on what this piece of work is and why the client wants it."),
        ("h1", "Scope"),
        ("h2", "In scope"),
        ("bullets", ["[The thing we will do]", "[The thing we will do]", "[The thing we will do]"]),
        ("h2", "Out of scope"),
        ("bullets", ["[The thing we will not do, so nobody assumes it]", "[Another one]"]),
        ("h1", "Deliverables"),
        ("table", ["Deliverable", "What it includes", "Due", "Accepted by"],
         [["[Deliverable]", "[What is in it]", "[Date]", "[Name]"], ["[Deliverable]", "[What is in it]", "[Date]", "[Name]"]],
         [4.4, 7.0, 2.6, 2.6]),
        ("h1", "Timeline"),
        ("table", ["Milestone", "Date", "Depends on"],
         [["Kick-off", "[Date]", "Signed statement of work"], ["[Milestone]", "[Date]", "[What must be done first]"],
          ["Handover", "[Date]", "All deliverables accepted"]], [6.0, 3.6, 7.0]),
        ("h1", "Fees and payment"),
        ("table", ["Item", "Fee", "Invoiced"], [["[Item]", "[Amount] plus VAT", "[On signature]"],
                                                ["[Item]", "[Amount] plus VAT", "[On acceptance]"]], [7.0, 5.0, 4.6]),
        ("p", "Invoices are payable within 14 days. Expenses are agreed in writing before they are incurred."),
        ("h1", "Assumptions"),
        ("bullets", ["[What we assume the client provides, and by when]", "[Who makes decisions, and how fast]"]),
        ("h1", "Acceptance and changes"),
        ("p", "Each deliverable is accepted in writing within [5] working days of delivery, or is treated as accepted. A "
              "change to scope, dates or fees is requested in writing, costed within [3] working days and agreed by both "
              "owners before work on it starts."),
        ("sign", ["ClimbGroup", "The Client"]),
    ]


def business_plan(b):
    return [
        ("toc",),
        ("eyebrow", "Summary"),
        ("h1", "The plan in one {page}"),
        ("lead", "What the business does, who it serves, how it makes money and what it needs next, in a page a busy "
                 "reader can act on."),
        ("p", "[Two or three short paragraphs. State the problem, the product, the customers and the next milestone.]"),
        ("callout", "The ask: [amount] to [what it funds], returning [what the reader gets] by [date]."),
        ("page",),
        ("h1", "The business"),
        ("h2", "What we do"), ("p", "[What the business sells, in plain words a customer would use.]"),
        ("h2", "Why now"), ("p", "[What has changed in the market or the technology that makes this the moment.]"),
        ("h2", "Where we are"), ("p", "[Stage, customers, revenue and team today, with the source for each number.]"),
        ("h1", "The market"),
        ("p", "[Who the customers are, how many there are, what they pay today and where that number comes from.]"),
        ("table", ["Segment", "Who they are", "What they pay today", "Why they switch"],
         [["[Segment]", "[Description]", "[Amount]", "[Reason]"], ["[Segment]", "[Description]", "[Amount]", "[Reason]"]],
         [3.6, 5.0, 3.6, 4.4]),
        ("h1", "Products and services"),
        ("bullets", ["[Product]: [what it does and for whom]", "[Product]: [what it does and for whom]"]),
        ("h1", "Marketing and sales"),
        ("p", "[How customers hear about the business, how they buy and what each sale costs to win.]"),
        ("h1", "Operations"),
        ("p", "[How the product is made and delivered, the key suppliers and systems, and what has to scale.]"),
        ("h1", "Team"),
        ("table", ["Name", "Role", "What they bring"], [["[Name]", "[Role]", "[Experience in one line]"],
                                                        ["[Name]", "[Role]", "[Experience in one line]"]], [4.0, 4.0, 8.6]),
        ("h1", "Financials"),
        ("table", ["", "Year 1", "Year 2", "Year 3"],
         [["Revenue", "[Amount]", "[Amount]", "[Amount]"], ["Gross margin", "[%]", "[%]", "[%]"],
          ["Operating costs", "[Amount]", "[Amount]", "[Amount]"], ["Net result", "[Amount]", "[Amount]", "[Amount]"],
          ["Cash at year end", "[Amount]", "[Amount]", "[Amount]"]], [6.0, 3.5, 3.5, 3.6]),
        ("small", "Table 1. Three-year summary. The detailed model is in the annual budget and cash flow forecast workbooks."),
        ("h1", "Funding and the ask"),
        ("p", "[How much, what it funds, what it returns and the milestones it reaches. Find investors looking for real "
              "deal flow by saying exactly what the money does.]"),
        ("h1", "Risks"),
        ("table", ["Risk", "Likelihood", "Impact", "What we do about it"],
         [["[Risk]", "[Low, medium or high]", "[Low, medium or high]", "[Control]"]], [5.0, 3.0, 3.0, 5.6]),
        ("h1", "Appendix"),
        ("bullets", ["[Detailed financial model]", "[Customer evidence]", "[Product roadmap]"]),
    ]


def policy(b):
    return [
        ("eyebrow", "Policy"),
        ("title", "[Policy name] {policy}"),
        ("kv", [("Owner", "[Name, role]"), ("Approved by", "[Name, role]"), ("Version", "[1.0]"),
                ("Effective from", "[Date]"), ("Next review", "[Date]")]),
        ("h1", "Purpose"), ("p", "[Why this policy exists and the outcome it protects, in two sentences.]"),
        ("h1", "Scope"), ("p", "[Who it applies to: employees, contractors, volunteers, suppliers. Where and when.]"),
        ("h1", "Policy"),
        ("p", "[The rules, as short numbered statements. Each one says what people do, not what they should feel.]"),
        ("numbers", ["[Rule one]", "[Rule two]", "[Rule three]"]),
        ("h1", "Responsibilities"),
        ("table", ["Who", "What they do"], [["Everyone", "[What every person covered by the policy does]"],
                                            ["Managers", "[What managers do]"], ["[Role]", "[What the owner does]"]],
         [4.6, 12.0]),
        ("h1", "Procedure"),
        ("numbers", ["[Step one: who does what]", "[Step two]", "[Step three]"]),
        ("h1", "If the policy is not followed"),
        ("p", "[What happens, who decides, and how a person raises a concern.]"),
        ("h1", "Related documents"),
        ("bullets", ["[Procedure name]", "[Form name]", "[Law or standard it follows]"]),
        ("h1", "Version history"),
        ("table", ["Version", "Date", "Change", "By"], [["1.0", "[Date]", "First issue", "[Name]"]], [2.2, 3.0, 8.4, 3.0]),
    ]


def sop(b):
    return [
        ("eyebrow", "Standard operating procedure"),
        ("title", "Speaker {check-in} at the registration desk"),
        ("kv", [("Owner", "[Name, role]"), ("Applies to", "Registration desk team"), ("Version", "[1.0]"),
                ("Last reviewed", "[Date]")]),
        ("h1", "Purpose"),
        ("lead", "Get every speaker checked in within a minute of reaching the desk, so they are in the green room on "
                 "time and the stage team knows they have arrived."),
        ("h1", "Before you start"),
        ("bullets", ["The desk device is signed in and on the event's registration screen.",
                     "Switch the desk to speaker mode: open the mode menu and choose Speaker.",
                     "Keep the printed speaker list to hand for manual check-in."]),
        ("h1", "Check in a speaker"),
        ("numbers", ["Ask for their e-ticket and scan it.", "Pick the session they are speaking in from the list that "
                     "appears.", "Press Check in. The screen confirms with the speaker's name and session.",
                     "Press Continue and hand over their pass. Point them to the green room."]),
        ("h2", "Manual check-in"),
        ("p", "If the ticket will not scan, press Manual check-in, type the speaker's name, pick them from the list and "
              "check them in. If they are not on the list, escalate (below) before issuing a pass."),
        ("h2", "Undo a mistaken check-in"),
        ("p", "Open the speaker's record, press Undo check-in and confirm. Check in the right person straight after, so "
              "the stage team's list stays right."),
        ("h1", "Warnings and when to escalate"),
        ("table", ["Message on screen", "What it means", "What to do"],
         [["Invalid badge", "The ticket is not valid for this event or has already been used", "Check the name on the "
           "printed list. If they are on it, check them in manually. If not, escalate."],
          ["No sessions", "The ticket is valid but no session is linked to it", "Check them in as an attendee, then "
           "escalate so the session is linked."]], [3.4, 6.0, 7.2]),
        ("h2", "What to pass on when you escalate"),
        ("bullets", ["The speaker's name and the event", "The exact message on the screen", "The session and its time",
                     "Whether the ticket works in attendee mode"]),
        ("callout", "Escalate to the registration lead on the radio or at the help point. Never leave a speaker waiting "
                    "at the desk: seat them nearby and bring the answer to them."),
        ("h1", "Version history"),
        ("table", ["Version", "Date", "Change", "By"], [["1.0", "[Date]", "First issue", "[Name]"]], [2.2, 3.0, 8.4, 3.0]),
    ]


def job_description(b):
    return [
        ("eyebrow", "Job description"),
        ("title", "[Role {title}]"),
        ("kv", [("Team", "[Team]"), ("Reports to", "[Role]"), ("Location", "[Office, hybrid or remote]"),
                ("Hours", "[Full time, part time]"), ("Salary", "[Range]"), ("Closing date", "[Date]")]),
        ("h1", "About the role"),
        ("lead", "[Two sentences on what this person makes happen and why it matters to the business.]"),
        ("h1", "What you will do"),
        ("bullets", ["[Outcome you own]", "[Outcome you own]", "[Outcome you own]", "[Who you work with most]"]),
        ("h1", "What you bring"),
        ("bullets", ["[Experience that is essential]", "[Skill that is essential]", "[The way of working we need]"]),
        ("h1", "Nice to have"),
        ("bullets", ["[Experience that helps but is not essential]"]),
        ("h1", "How we work"),
        ("p", "[A short paragraph on the team, the pace and what people say they like about working here.]"),
        ("h1", "How to apply"),
        ("callout", "Send your CV and a short note on why this role, to [email] by [date]. We reply to everyone."),
    ]


def offer_letter(b):
    return [
        ("p", "[Candidate name]\n[Address line 1]\n[Town]\n[Postcode]"),
        ("p", "[Date]"),
        ("p", "Dear [First name],"),
        ("h2", "Offer of employment: [Role title]"),
        ("p", "We are delighted to offer you the role of [Role title] at %s. Here are the main terms; the full terms "
              "are in the contract that comes with this letter." % b),
        ("kv", [("Role", "[Role title]"), ("Start date", "[Date]"), ("Salary", "[Amount] a year"),
                ("Hours", "[Hours] a week"), ("Location", "[Office or remote]"), ("Reports to", "[Name, role]"),
                ("Holiday", "[Days] a year plus bank holidays"), ("Probation", "[Months] months")]),
        ("p", "This offer depends on [references and the right to work in the UK]. To accept, sign below and return "
              "this letter by [date]."),
        ("p", "We are looking forward to working with you."),
        ("p", "Best wishes,"),
        ("sigline", "[Name], [Role], %s" % b),
        ("h3", "Acceptance"),
        ("p", "I accept the offer on the terms above."),
        ("sigline", "[Candidate name]"),
    ]


def employee_handbook(b):
    return [
        ("toc",),
        ("eyebrow", "Welcome"),
        ("h1", "Welcome to the {team}"),
        ("lead", "This handbook tells you how we work, what you can expect from us and what we ask of you. Keep it to "
                 "hand in your first weeks and come back to it whenever a question comes up."),
        ("h1", "How we work"),
        ("bullets", ["[Value one, and what it looks like day to day]", "[Value two]", "[Value three]"]),
        ("h1", "Your first weeks"),
        ("numbers", ["Day one: your kit, your accounts and a tour of how the team runs.",
                     "Week one: meet the people you will work with most and agree your first goals.",
                     "Month one: a check-in with your manager on how it is going."]),
        ("h1", "Working hours and flexibility"), ("p", "[Core hours, where people work, how to book time away.]"),
        ("h1", "Pay and benefits"), ("p", "[When pay is made, pension, and the benefits people can use.]"),
        ("h1", "Holiday and leave"), ("p", "[Holiday allowance, how to book it, and the other kinds of leave.]"),
        ("h1", "Sickness"), ("p", "[Who to tell, by when, and how sick pay works.]"),
        ("h1", "Conduct"), ("p", "[What we expect of each other, and what happens when it is not met.]"),
        ("h1", "Equality and respect"), ("p", "[Everyone is treated fairly. How to raise anything that falls short.]"),
        ("h1", "Health and safety"), ("p", "[Who is responsible, how to report an accident or a near miss.]"),
        ("h1", "Data and devices"), ("p", "[How to look after company data and devices, and what to do if one is lost.]"),
        ("h1", "Raising a concern"), ("p", "[Who to talk to, and how a concern is handled.]"),
        ("h1", "Leaving"), ("p", "[Notice periods, handover and returning kit.]"),
        ("h1", "Policies"),
        ("table", ["Policy", "Owner", "Where to find it"], [["[Policy name]", "[Role]", "[Link or folder]"],
                                                             ["[Policy name]", "[Role]", "[Link or folder]"]], [6.0, 4.0, 6.6]),
    ]


def brief(b):
    return [
        ("eyebrow", "Brief"),
        ("title", "[Project] {brief}"),
        ("kv", [("Project", "[Name]"), ("Requested by", "[Name, role]"), ("Owner", "[Name, role]"),
                ("Due", "[Date]"), ("Budget", "[Amount]")]),
        ("h1", "Background"), ("p", "[What is happening and why this piece of work is needed now.]"),
        ("h1", "Objective"), ("callout", "[The one result this work must achieve, in a sentence someone could test.]"),
        ("h1", "Audience"), ("p", "[Who it is for, what they already know and what they need to do next.]"),
        ("h1", "Key message"), ("quote", "[The one line the audience should remember.]", "The message, in the brand voice"),
        ("h1", "Deliverables"),
        ("table", ["Deliverable", "Format and size", "Due", "Owner"],
         [["[Deliverable]", "[Format]", "[Date]", "[Name]"], ["[Deliverable]", "[Format]", "[Date]", "[Name]"]],
         [5.0, 6.0, 2.8, 2.8]),
        ("h1", "Tone and look"),
        ("p", "Written in the brand voice and built from the brand templates: one orange word and one italic word per "
              "headline, real photos, one button per view. The brand guidelines say the rest."),
        ("h1", "Must and must not"),
        ("bullets", ["Must: [the thing it has to include]", "Must not: [the thing it cannot say or show]"]),
        ("h1", "Timeline"),
        ("table", ["Stage", "Date"], [["Brief agreed", "[Date]"], ["First version", "[Date]"], ["Feedback", "[Date]"],
                                      ["Final", "[Date]"], ["Live", "[Date]"]], [8.6, 8.0]),
        ("h1", "Approval"), ("p", "[Who signs it off, and how long they have.]"),
        ("h1", "Success looks like"), ("p", "[The measure you will look at afterwards, and the number you want.]"),
    ]


def case_study(b):
    ed = edition(b)
    return [
        ("eyebrow", "Case study: [Company]"),
        ("title", "From [the problem] to {the result}"),
        ("lead", "[One or two sentences: who the company is, what they came for and what they left with.]"),
        ("h1", "The challenge"),
        ("p", "[What the company was trying to do, and what was in the way. Use their words where you can.]"),
        ("h1", "What happened at %s" % ed),
        ("p", "[The sessions, the people and the conversations that mattered. Be specific: name the format and the "
              "moment.]"),
        ("h1", "The result"),
        ("big", "[00]", "[What the number measures, and where it comes from. One fact, never a guess.]"),
        ("quote", "[Put the quote here, word for word, exactly as it was said, with permission to use it.]",
         "[First name Last name], [Role], [Company]"),
        ("h1", "What is next"),
        ("p", "[What the company is doing now, and what they plan to do at the next edition.]"),
        ("h2", "About [Company]"),
        ("p", "[One paragraph on the company, in their words.]"),
        ("callout", "Want the same for your business? Get your ticket at %s." % B.BRANDS[b]["url"]),
    ]


def fact_sheet(b):
    ed = edition(b)
    return [
        ("eyebrow", "Fact sheet"),
        ("title", "%s at a {glance}" % ed),
        ("lead", "The Festival for Business Growth: two days of main stage moments, roundtables and the people who move "
                 "businesses forward."),
        ("kv", [("What", "A festival for growing companies, the people who fund them and the firms that help them"),
                ("When", event_dates(b)), ("Who it is for", "Founders and growing companies, investors, advisers, "
                                                           "professional services firms, universities and the public sector"),
                ("Formats", "Main stage moments, roundtables, workshops, investor speed networking, the expo, ClimbAwards "
                            "and the after party"),
                ("Tickets", "[Release name], [price], [state]"), ("Partners", "Book a call with the partnerships team")]),
        ("h2", "Three things to know"),
        ("bullets", ["Find your people: the right people in the room, with time to talk properly.",
                     "Main stage moments: short, big moments, not long lectures.",
                     "Doing, not dreaming: every session ends with something to do next."]),
        ("h2", "Contact"),
        ("p", "Press: %s. Partnerships: %s. Everything else: %s." % (B.BRANDS[b]["email"], PARTNER_EMAIL, B.BRANDS[b]["url"])),
    ]


def newsletter(b):
    return [
        ("eyebrow", "[Month] newsletter"),
        ("title", "What is {new} this _month_"),
        ("lead", "[Two lines on the one thing readers should know, and what to do about it.]"),
        ("h1", "[Story one headline]"),
        ("p", "[Three or four sentences. What happened, why it matters to the reader, what to do next.]"),
        ("p", "See the full story at [link text that says where it goes]."),
        ("h1", "[Story two headline]"),
        ("p", "[Three or four sentences.]"),
        ("quote", "[A line from someone who was there, word for word, with permission.]", "[Name], [Role], [Company]"),
        ("h1", "[Story three headline]"),
        ("p", "[Three or four sentences.]"),
        ("h2", "Dates for your diary"),
        ("table", ["Date", "What", "Where to book"], [["[Date]", "[Event or deadline]", "[Link text]"],
                                                      ["[Date]", "[Event or deadline]", "[Link text]"]], [3.4, 8.0, 5.2]),
        ("callout", "Get your ticket at %s, and send this to someone who should be in the room." % B.BRANDS[b]["url"]),
    ]


def board_report(b):
    return [
        ("toc",),
        ("eyebrow", "For the board"),
        ("h1", "Summary for the {board}"),
        ("lead", "[Five lines: where the business is against plan, the two things that changed, and the decisions this "
                 "meeting needs to make.]"),
        ("h2", "Decisions needed"),
        ("numbers", ["[Decision, with the recommendation and the date it is needed by]", "[Decision]"]),
        ("page",),
        ("h1", "Performance against plan"),
        ("table", ["Measure", "Plan", "Actual", "Variance", "Comment"],
         [["Revenue", "[Amount]", "[Amount]", "[Amount]", "[Why]"], ["Tickets", "[Number]", "[Number]", "[Number]", "[Why]"],
          ["Partners", "[Number]", "[Number]", "[Number]", "[Why]"], ["Cash", "[Amount]", "[Amount]", "[Amount]", "[Why]"]],
         [3.6, 2.6, 2.6, 2.6, 5.2]),
        ("h1", "Finance"), ("p", "[Profit and loss, cash and the forecast to year end, with the workbook attached.]"),
        ("h1", "People"), ("p", "[Hires, leavers, capacity and anything the board should know about the team.]"),
        ("h1", "Events and products"), ("p", "[Where each edition and product is up to against its plan.]"),
        ("h1", "Risks"),
        ("table", ["Risk", "Score", "Trend", "What we are doing"],
         [["[Risk]", "[Score]", "[Up, flat or down]", "[Control]"]], [5.6, 2.2, 3.0, 5.8]),
        ("h1", "Outlook"), ("p", "[The next quarter in three paragraphs: what will happen, what could go wrong, what "
                                 "the board will see next time.]"),
        ("h1", "Appendix"), ("bullets", ["[Management accounts]", "[Pipeline report]", "[Minutes of the last meeting]"]),
    ]


def terms_and_conditions(b):
    return [
        ("eyebrow", "Terms"),
        ("title", "Terms and {conditions}"),
        ("sub", "[Tickets, services or partnerships]: the terms that apply when you book with ClimbGroup."),
        ("p", "These terms are between you and %s. They apply from the moment you book. Clause headings are fixed; the "
              "approved wording for each clause goes under its heading." % LEGAL_PARTY),
        ("clauses", [
            ("About these terms", "Who we are, what these terms cover and when they apply."),
            ("Definitions", "What the capitalised words mean."),
            ("Booking and payment", "How a booking is made and confirmed, prices, VAT and when payment is due."),
            ("Changes and cancellation", "What you can change, by when, and what is refunded. Ticket releases close "
                                         "when they are gone."),
            ("What you can expect from us", "What we provide and the standard we work to."),
            ("What we ask of you", "Conduct at the event, passes, photography and filming consent."),
            ("Intellectual property", "Who owns the content, recordings and marks."),
            ("Liability", "What we are and are not liable for, and the liability the law does not let us exclude."),
            ("Data protection", "How we use your details, and the privacy notice this links to."),
            ("Events outside our control", "What happens if the event is moved, changed or cannot go ahead."),
            ("General", "Whole agreement, changes to these terms, law and jurisdiction."),
            ("Contact", "Questions about these terms go to [email]."),
        ], 1),
        ("small", "Version [1.0], effective from [Date]."),
    ]


def post_event_report(b):
    ed = edition(b)
    return [
        ("toc",),
        ("eyebrow", "The event in one page"),
        ("h1", "%s in one {page}" % ed),
        ("lead", "[What happened, who came and what they said, in a page a partner or a board member can read in two "
                 "minutes.]"),
        ("big", "[00]", "[What the number measures, with its source. One fact per number.]"),
        ("page",),
        ("h1", "Highlights"),
        ("bullets", ["[The main stage moment people talked about]", "[The roundtable that ran over because nobody wanted "
                     "to leave]", "[The ClimbAwards winner and why]", "[The after party]"]),
        ("h1", "Sessions and speakers"),
        ("table", ["Session", "Format", "Speakers", "Stage"],
         [["[Title]", "[Panel, talk, roundtable]", "[Names]", "[Stage]"], ["[Title]", "[Format]", "[Names]", "[Stage]"]],
         [6.0, 3.4, 4.6, 2.6]),
        ("h1", "Partners and exhibitors"),
        ("p", "Thank you to every partner and exhibitor who made %s happen. [List them by package, with their marks on "
              "the next page.]" % ed),
        ("h1", "What people told us"),
        ("p", "[The themes from the feedback survey, each with one line of evidence from the results workbook.]"),
        ("quote", "[A line from the feedback, word for word, with permission to use it.]", "[Role], [Company]"),
        ("quote", "[A second line.]", "[Role], [Company]"),
        ("page",),
        ("h1", "Photos"),
        ("p", "[Add the photos here: real moments, with consent, each with a caption that says who and what.]"),
        ("small", "[Caption: who, where, what is happening]"),
        ("page",),
        ("h1", "Next time"),
        ("bullets", ["[What we will keep]", "[What we will change]", "[What we will try]"]),
        ("h1", "Appendix"),
        ("bullets", ["[Full feedback results]", "[Agenda as run]", "[Budget against actual]"]),
    ]


def exhibitor_manual(b):
    ed = edition(b)
    return [
        ("toc",),
        ("eyebrow", "Welcome"),
        ("h1", "Welcome to {%s}" % ed),
        ("lead", "Everything you need to build, staff and break down your stand, in the order you will need it. Your "
                 "tasks and deadlines are in the exhibitor portal; this manual explains each one."),
        ("h2", "The exhibitor portal"),
        ("numbers", ["Sign in with the link in your welcome email.", "Complete each task on the list, in order.",
                     "Upload the forms as you go. A task turns green when it is done.",
                     "Questions go to %s." % EXHIBITOR_EMAIL]),
        ("page",),
        ("h1", "Your stand"),
        ("h2", "What every stand includes"),
        ("table", ["Item", "Included", "Notes"],
         [["Lighting", "[Yes]", "[Spotlights per stand]"], ["Power socket", "[Yes]", "[Sockets and rating]"],
          ["Walls", "[Yes]", "[Panel type and colour]"], ["Table and stools", "[Yes]", "[Number]"],
          ["Name board", "[Yes]", "Your company name as entered in the portal"], ["Screen", "[Yes or on request]", "[Size]"]],
         [4.0, 3.6, 9.0]),
        ("h2", "Stand sizes"),
        ("table", ["Type", "Size", "What fits"], [["[Type]", "[Width x depth]", "[Table, two stools, one banner]"],
                                                   ["[Type]", "[Width x depth]", "[What fits]"]], [4.0, 4.0, 8.6]),
        ("h2", "Panel options"),
        ("bullets", ["Leave the panels blank and use your own banners.",
                     "Remove the walls and build your own stand (send your drawings and your contractor's documents).",
                     "Order printed panels through the portal.",
                     "Print your own panels to the sizes in the portal."]),
        ("callout", "Panel artwork and build drawings are due by [date]. After that, stands ship as standard."),
        ("h2", "Stand extras"),
        ("p", "Extra furniture, screens, power and printing are ordered in the portal by [date]. Prices are in the order "
              "form."),
        ("h1", "Build-up"),
        ("p", "Book your setup slot in the portal. There is no access before the expo opens on day one unless you have a "
              "booked slot. Bring your pass and sign in at the exhibitor desk."),
        ("h2", "Vehicle unloading"),
        ("p", "Book an unloading slot of about 15 minutes. Unload, then move the vehicle to [where to park] so the next "
              "exhibitor can pull in."),
        ("h2", "Deliveries"),
        ("bullets", ["Small items only, sent to [exact delivery address] and labelled with your company name and stand "
                     "number.", "Deliveries are accepted from [date] and stored until build-up.",
                     "Collect everything by [deadline]. Items are left at your own risk."]),
        ("h1", "Breakdown"),
        ("p", "Breakdown starts at [time] and finishes at [time] on [day]. Do not book travel before breakdown ends, and "
              "leave the stand as you found it."),
        ("h1", "On site"),
        ("h2", "WiFi"),
        ("p", "General WiFi covers the expo floor. A dedicated line for demos is ordered in the portal."),
        ("h2", "Electrical items"),
        ("p", "Every electrical item must carry a current PAT test label, or be tested on site for [fee] an item."),
        ("h2", "FAQs"),
        ("h3", "How high can my stand be?"),
        ("p", "[Height limit]. Anything higher needs drawings approved by [date]."),
        ("h3", "How do I fix things to the panels?"),
        ("p", "Hook Velcro only. No tape, pins, nails, glue or putty: damage is charged at cost."),
        ("h3", "What is the flooring?"),
        ("p", "[Flooring type]. Order your own in the portal if you want something different."),
        ("h3", "Where do I get help on site?"),
        ("p", "The exhibitor desk at [location], or any member of the team in a crew shirt."),
        ("page",),
        ("h1", "Forms checklist"),
        ("p", "Complete these in the portal, in this order."),
        ("numbers", ["Exhibitor form", "Health and safety acknowledgement", "Site induction acknowledgement",
                     "PAT testing certificate", "Your own health and safety documents", "Employers liability insurance",
                     "Additional stand orders", "Stand panels"]),
        ("checklist", ["Booked on site (setup slot)", "Booked off site (breakdown)"]),
        ("page",),
        ("h1", "Health and safety acknowledgement"),
        ("p", "By signing, you confirm that your company and everyone working on your stand will follow the law below, "
              "the site rules and the instructions of the event team."),
        ("bullets", ["Health and Safety at Work etc. Act 1974", "Management of Health and Safety at Work Regulations 1999",
                     "Workplace (Health, Safety and Welfare) Regulations 1992",
                     "Provision and Use of Work Equipment Regulations (PUWER) 1998", "Work at Height Regulations 2005",
                     "Reporting of Injuries, Diseases and Dangerous Occurrences Regulations (RIDDOR) 2013",
                     "Control of Substances Hazardous to Health (COSHH) Regulations 2002",
                     "Personal Protective Equipment (PPE) Regulations", "Manual Handling Operations Regulations 1992",
                     "Construction (Design and Management) (CDM) Regulations 2015", "Electricity at Work Regulations 1989",
                     "Lifting Operations and Lifting Equipment Regulations (LOLER) 1998"]),
        ("h2", "Site rules"),
        ("bullets", ["Security and vigilance: wear your pass, challenge anyone without one, report anything unattended.",
                     "Evacuation: when the announcement is made, stop work, leave by the nearest exit and go to the "
                     "assembly point at [location]. Do not use lifts. Do not go back for belongings.",
                     "First aid: the first aid point is at [location]. Report every injury to the exhibitor desk.",
                     "Fire: raise the alarm at the nearest call point and leave. Fight a fire only if trained and safe.",
                     "Closed footwear and PPE in active build zones. Keep gangways clear. No under 16s during build and "
                     "breakdown. No lone working. Report accidents and near misses the same day."]),
        ("sigline", "[Name], [Company], [Stand number]"),
        ("page",),
        ("h1", "Site induction acknowledgement"),
        ("kv", [("Your name", "[Name]"), ("Company", "[Company]"), ("Stand", "[Stand number]"),
                ("Mobile on the day", "[Phone]")]),
        ("bullets", ["Keep your pass visible at all times.", "The on-site help point is the exhibitor desk at [location].",
                     "Evacuation: leave by the nearest exit and go to the assembly point at [location].",
                     "Welfare and facilities: toilets, water and the lunch area are at [location].",
                     "Wear PPE during build and breakdown.", "Sign in and out at the exhibitor desk every day."]),
        ("sigline", "[Name], [Company]"),
    ]


def speaker_brief(b, host=False):
    ed = edition(b)
    who = "host" if host else "speaker"
    out = [
        ("eyebrow", "%s brief" % ("Host" if host else "Speaker")),
        ("title", "Thank you for %s at {%s}" % ("hosting" if host else "speaking", ed)),
        ("lead", "Here is everything you need before, during and after your session. Read it once now and once again "
                 "the day before."),
        ("h1", "Your session"),
        ("table", ["Detail", "Confirmed"],
         [["Title", "[Session title]"], ["Date", "[Date]"], ["Time", "[Start] to [End]"], ["Stage", "[Stage]"],
          ["Duration", "[Minutes]"], ["Host", "[Name, company]"], ["Fellow speakers", "[Names, companies]"]], [4.6, 12.0]),
    ]
    if host:
        out += [("callout", "As a host you move between sessions through the day. Tell the team the date of your prep "
                            "call as soon as it is booked, so the running order is built around it.")]
    out += [
        ("h1", "Preparing your session"),
        ("bullets", ["Your host sets up a group chat for each session, named \"%s - Day, Stage, Time\", with the "
                     "team's event mobile added, and books a video call before the event." % ed,
                     "A session with several guests runs like a TV chat show: a 5 minute host introduction, then the "
                     "conversation.", "A one-to-one is a fireside chat.",
                     "Please do not script it. Know your three points and talk."]),
        ("h2", "Promote your session"),
        ("p", "The share kit has images and lines for your social channels. Post once when the agenda goes live and once "
              "the week before."),
        ("h1", "On the day"),
        ("bullets", ["Registration opens at [time]. Bring your e-ticket or use the ClimbGroup Event App.",
                     "Arrive at the speaker green room at least one hour before your session, and allow 30 minutes "
                     "before that to collect your pass.", "No pass, no stage access."]),
        ("h2", "Ending your session"),
        ("p", "60 seconds before the end a tone plays and music fades in. Wrap up in those 60 seconds. The lights dim, "
              "you leave the stage and hand back the microphones straight away. A session that overruns has its "
              "microphones cut, so the next one starts on time."),
        ("h2", "The green room"),
        ("p", "For speakers, hosts and partners only. Capacity is limited for fire safety, so guests wait in the lounge."),
        ("h2", "Roundtables, workshops and podcasts"),
        ("p", "Roundtables and workshops are booked in the app. Podcast recordings are arranged separately with the team."),
        ("h1", "Schedule changes"),
        ("callout", "Send your mobile number to %s so we can reach you if the running order changes on the day."
                    % SPEAKER_EMAIL),
        ("h1", "Travel and parking"),
        ("p", "[How to get there, where to park and the code or pass you need.]"),
        ("h1", "Thank you"),
        ("p", "Your session is one of the moments people will remember. Thank you for being part of %s." % ed),
    ]
    return out


def event_risk_assessment(b):
    ed = edition(b)
    return [
        ("toc",),
        ("eyebrow", "Risk assessment and method statement"),
        ("h1", "Overview"),
        ("kv", [("Event", "%s, %s" % (ed, event_dates(b))), ("Organiser", LEGAL_PARTY), ("Location", "[Location]"),
                ("Assessed by", "[Name, role]"), ("Date", "[Date]"), ("Review", "[Date, or when plans change]")]),
        ("p", "[What the event is, how many days it runs, the areas it uses and who attends. The method statement "
              "says how each part runs safely; the risk register scores what could go wrong.]"),
        ("h1", "Schedule"),
        ("table", ["Day", "Time", "Activity", "Areas"],
         [["Build day", "[Times]", "Set-up and stand build", "[Areas]"], ["Day one", "[Times]", "Doors, sessions, expo, "
          "awards and after party", "[Areas]"], ["Day two", "[Times]", "Sessions, expo, close and breakdown", "[Areas]"]],
         [3.0, 3.0, 7.0, 3.6]),
        ("h1", "Method statement"),
        ("h2", "Set-up and breakdown"), ("p", "[Who builds what, in what order, with what equipment and supervision.]"),
        ("h2", "Event management"), ("p", "[The control room, the radio net, the event manager and the chain of command.]"),
        ("h2", "Outdoor zone"), ("p", "[Weather plan, barriers, lighting, ground conditions.]"),
        ("h2", "Sessions and activities"), ("p", "[Stage management, capacity, seating, AV and cables.]"),
        ("h2", "Young people's area"), ("p", "[Supervision ratios, checks on staff, sign-in and collection.]"),
        ("h2", "Supplier management"), ("p", "[Documents each supplier sends, inductions and who checks their work.]"),
        ("h2", "Security"), ("p", "[Passes, searches, access control and the response to an incident.]"),
        ("h1", "Risk assessment"),
        ("p", "Score likelihood 1 to 5 (1 Rare, 2 Unlikely, 3 Possible, 4 Likely, 5 Almost certain) and severity 1 to 5 "
              "(1 Minor injury or inconvenience, 2 First aid required, 3 Injury requiring medical treatment, 4 Serious "
              "injury, 5 Major injury or fatality). Risk is likelihood times severity: Low 1 to 4, Medium 5 to 9, High "
              "10 to 15, Critical 16 to 25."),
        ("table", ["Ref", "Hazard", "Who could be harmed", "Controls", "L", "S", "Score", "Owner"],
         [["1", "Crowd movement at doors and between sessions", "Attendees", "Staggered doors, stewards at pinch points, "
           "one-way flow at peak times", "2", "3", "6 Medium", "[Role]"],
          ["2", "Cables and stage equipment", "Speakers, crew", "Cables taped or ramped, stage edge marked, crew briefed", "2",
           "2", "4 Low", "[Role]"],
          ["3", "Fire", "Everyone", "Fire plan, trained stewards, exits kept clear, no naked flames", "1", "5", "5 Medium",
           "[Role]"],
          ["4", "Alcohol at the reception and the after party", "Attendees", "Licensed bar, Challenge 25, water and food "
           "available, stewards watch for anyone unwell", "3", "2", "6 Medium", "[Role]"],
          ["5", "[Hazard]", "[Who]", "[Controls]", "[1-5]", "[1-5]", "[Score]", "[Role]"]],
         [1.0, 3.6, 2.4, 5.6, 0.8, 0.8, 1.6, 1.8]),
        ("h1", "Security, access and staff identification"),
        ("p", "[Pass types and colours, who checks them, what happens to anyone without one, and how staff are "
              "identified.]"),
        ("h1", "Emergency procedures"),
        ("bullets", ["Fire or evacuation: [the announcement, the exits, the assembly point and who sweeps each area].",
                     "Medical: [first aid points, the first aiders and how an ambulance is called and met].",
                     "Security incident: [the code word, who responds and when the police are called].",
                     "Missing child or vulnerable adult: [who is told, the search and the lockdown].",
                     "After any incident: record it in the incident log the same day."]),
        ("h1", "Insurance and documentation"),
        ("table", ["Document", "Held by", "Checked"], [["Public liability insurance", "ClimbGroup", "[Date]"],
                                                        ["Supplier insurance and RAMS", "[Role]", "[Date]"],
                                                        ["Site fire risk assessment", "[Owner]", "[Date]"]], [7.0, 5.0, 4.6]),
        ("h1", "Key contacts"),
        ("table", ["Role", "Name", "Phone"], [["Event manager", "[Name]", "[Phone]"], ["Control room", "[Name]", "[Phone]"],
                                              ["Security lead", "[Name]", "[Phone]"], ["First aid lead", "[Name]", "[Phone]"],
                                              ["Site contact", "[Name]", "[Phone]"]], [5.0, 6.0, 5.6]),
    ]


def exhibitor_risk_assessment(b):
    """The external exhibitor and partner version: the Word layout of the workbook, A4 landscape."""
    ed = edition(b)
    rows = [
        ["Visitors", "Moving in, out and around your space", "Congestion or blocked routes", "Visitors and your team",
         "Trips, falls or collisions", "Layout leaves a clear way in and out. The team watches numbers and pauses an "
         "activity if it gets too busy.", "", "2", "2", "4 Low", "[Name]"],
        ["Layout", "Your space and its footprint", "Items or queues spilling into aisles", "Visitors and other exhibitors",
         "Trips, or a slower evacuation", "Everything stays inside the space you were given. Aisles, exits and fire "
         "points are never blocked.", "", "2", "3", "6 Medium", "[Name]"],
        ["Your team", "Long days on your feet", "Tiredness and dehydration", "Your team", "Lower awareness, fainting",
         "A break rota, water on the stand and enough people to cover breaks.", "", "2", "1", "2 Low", "[Name]"],
        ["Set up and break down", "Lifting and moving equipment or stock", "Heavy or awkward loads", "Your team and "
         "contractors", "Strains, sprains and back injury", "Trolleys for heavy items. Two people for anything awkward.",
         "", "2", "2", "4 Low", "[Name]"],
        ["Interactive activity", "Games, challenges and competitions", "Crowding, over-excitement or misuse", "Visitors",
         "Trips, collisions, minor injury", "Clear rules on display. A team member runs the activity. The queue stays "
         "inside the space.", "", "2", "2", "4 Low", "[Name]"],
        ["Housekeeping", "Cables, boxes, waste and storage", "Trip hazards inside your space", "Your team and visitors",
         "Trips and falls", "Cables run behind the stand or under cable covers. Boxes and waste are cleared through the "
         "day.", "", "2", "2", "4 Low", "[Name]"],
        ["Electrical", "Screens, laptops, lighting and extension leads", "Faulty equipment, trailing or daisy-chained "
         "leads", "Your team and visitors", "Electric shock or fire", "Equipment is PAT tested or booked for testing on "
         "site. No extension leads plugged into each other. Power off at the end of each day.", "", "1", "4", "4 Low",
         "[Name]"],
        ["Demonstrations", "Live demos, moving parts, stock on display", "Contact with moving parts, distraction, items "
         "falling", "Your team and visitors", "Cuts, crush or impact injury", "Guards stay on. A clear area around the "
         "demo. Run by trained team members and switched off when nobody is with it.", "", "2", "3", "6 Medium", "[Name]"],
        ["Food and drink", "Samples, hot drinks and chilled food", "Allergens, poor hygiene, heat, wrong temperatures",
         "Visitors", "Allergic reaction, food poisoning, burns", "Allergen information on display. Trained handlers and "
         "sanitiser at the serving point. Hot equipment at the back, chilled food kept chilled.", "", "2", "3",
         "6 Medium", "[Name]"],
    ]
    return [
        ("eyebrow", "Exhibitor and partner risk assessment"),
        ("title", "Your stand at {%s}" % ed),
        ("lead", "Complete this for your stand or activation and send it to %s by the deadline in your contract. The "
                 "spreadsheet version scores each row for you." % EXHIBITOR_EMAIL),
        ("h2", "How to complete it"),
        ("numbers", ["Complete your details below.", "Each row is one hazard, not one item. Work left to right.",
                     "Add rows for anything unusual: games, interactive experiences, food or drink, machines or moving "
                     "parts.", "Score likelihood and severity 1 to 5 before and after your controls.",
                     "Check it before you submit, and update it if your plans change."]),
        ("kv", [("Company", "[Company]"), ("Event", "%s, %s" % (ed, event_dates(b))), ("Stand", "[Stand number]"),
                ("Contact", "[Name], [email], [phone]"), ("Completed by", "[Name], [Date]")]),
        ("h2", "Scoring"),
        ("p", "Likelihood: 1 Rare, 2 Unlikely, 3 Possible, 4 Likely, 5 Almost certain. Severity: 1 Minor injury or "
              "inconvenience, 2 First aid required, 3 Injury requiring medical treatment, 4 Serious injury, 5 Major "
              "injury or fatality. Score is likelihood times severity: Low 1 to 4, Medium 5 to 9, High 10 to 15, "
              "Critical 16 to 25. A High or Critical score needs more controls before the event; tell us at %s."
              % EXHIBITOR_EMAIL),
        ("table", ["Area or activity", "Item or task", "Hazard", "Who could be harmed", "Potential harm",
                   "Existing controls", "Additional controls for this event", "L", "S", "Score and band", "Person responsible"],
         rows, [2.2, 2.6, 2.6, 2.2, 2.4, 4.6, 3.0, 0.7, 0.7, 1.6, 1.9]),
        ("sigline", "[Name], [Role], [Company]"),
    ]


def event_day_pack(b):
    ed = edition(b)
    return [
        ("toc",),
        ("eyebrow", "Welcome to the team"),
        ("h1", "Welcome to {%s}" % ed),
        ("lead", "Our job is to connect people to opportunities that help them grow. The way we do it: welcoming, "
                 "inclusive, energetic, professional but never stiff."),
        ("h2", "Your role at a glance"),
        ("bullets", ["First impression: you are the first face most people see.",
                     "Go-to support: when someone is lost, you are the answer.",
                     "Connector: you know who is where, and you point people to the right room.",
                     "Problem-solver: small problems are fixed on the spot; big ones go to your team lead."]),
        ("table", ["Do", "Do not"],
         [["Smile and be approachable", "Use your phone in public areas"], ["Use positive language", "Leave someone "
           "without a direction"], ["Be proactive: offer help before it is asked for", "Argue with an attendee"],
          ["Escalate bad behaviour straight away", "Promise something you cannot deliver"]], [8.3, 8.3]),
        ("page",),
        ("h1", "The site"),
        ("table", ["Zone", "What happens there", "Opening times"],
         [["Registration", "Passes, help point, lost property", "[Times]"], ["Main stage", "Main stage moments, "
           "ClimbAwards", "[Times]"], ["Expo", "Stands, lunch", "[Times]"], ["Roundtable rooms", "Roundtables and "
           "workshops", "[Times]"], ["Green room", "Speakers, hosts and partners only", "[Times]"],
          ["[Zone]", "[What happens]", "[Times]"]], [4.0, 8.6, 4.0]),
        ("h1", "Timetable"),
        ("table", ["Time", "Day one", "Day two"], [["[Time]", "[What happens, where]", "[What happens, where]"],
                                                    ["[Time]", "[What happens, where]", "[What happens, where]"],
                                                    ["[Time]", "[What happens, where]", "[What happens, where]"]],
         [3.0, 6.8, 6.8]),
        ("page",),
        ("h1", "Radio"),
        ("h2", "Callsigns"),
        ("p", "First names, plus Control and Security. Say who you are calling first, then who you are: \"Control, from "
              "[your name]\". Control answers \"Go ahead\"."),
        ("h2", "General phrases"),
        ("table", ["Say", "Meaning"], [["Standby or Wait one", "I heard you; give me a moment"], ["So far", "Have you "
          "understood so far?"], ["Check", "Understood"], ["Priority", "This needs attention next"], ["Urgent", "Stop "
          "other traffic; this is urgent"]], [5.0, 11.6]),
        ("h2", "Emergency phrases"),
        ("table", ["Say", "Meaning"], [["Mr Sands", "A possible fire"], ["Inspector Gadget", "An unattended or suspicious "
          "item"], ["PANIC", "A life-threatening incident"]], [5.0, 11.6]),
        ("callout", "Never say fire, bomb or suspicious device on the radio. Use the phrase, give the location, and wait "
                    "for Control."),
        ("h1", "Escalation"),
        ("numbers", ["Who: your team lead, in person.", "What: say what happened, where and who is involved.",
                     "Solution: say what you have already done.", "Urgency: say how fast it needs an answer.",
                     "No team lead nearby: use the nearest radio and say \"Requesting Control\"."]),
        ("h1", "Emergency procedures"),
        ("bullets", ["Fire or evacuation: call it on the radio as Mr Sands with the location. When the evacuation "
                     "announcement plays, guide people to the nearest exit and the assembly point at [location].",
                     "Unwell or injured: stay with the person, call Control for first aid, do not move them.",
                     "Threatening behaviour: do not engage. Call Security on the radio with the location and a description.",
                     "Safeguarding: a missing child or vulnerable adult is called to Control at once with a description "
                     "and where they were last seen. Nobody leaves through the doors until Control says so.",
                     "Afterwards: record every incident in the log at the back of this pack, the same day."]),
        ("page",),
        ("h1", "Practical information"),
        ("bullets", ["Wear: [crew shirt, comfortable closed shoes]. Bring: [a charged phone, a water bottle].",
                     "Report to [location] at [time] each day.", "Lunch is in [location] between [times].",
                     "Keep your pass visible at all times.", "If you are ill or late, call the control room on [phone]."]),
        ("h2", "The app"),
        ("p", "The ClimbGroup Event App has the agenda, the map and the attendee list. Install it before the day and "
              "help attendees find sessions in it."),
        ("h1", "Roles"),
        ("table", ["Role", "What you do", "Where", "Reports to"],
         [["Registration", "Check in attendees and speakers, answer questions, hand out passes", "[Zone]", "[Lead]"],
          ["Stage steward", "Seat the room, keep aisles clear, hand mics for questions", "[Stage]", "[Lead]"],
          ["Expo steward", "Help exhibitors, keep gangways clear, point people to stands", "Expo", "[Lead]"],
          ["Runner", "Move people and things between zones", "Everywhere", "[Lead]"],
          ["[Role]", "[What you do]", "[Zone]", "[Lead]"]], [3.4, 7.4, 2.8, 3.0]),
        ("h1", "Key contacts"),
        ("table", ["Role", "Name", "Phone or radio"],
         [["Event manager", "[Name]", "[Phone]"], ["Control room", "[Name]", "Control"], ["Security", "[Name]", "Security"],
          ["First aid", "[Name]", "[Phone]"], ["Registration lead", "[Name]", "[Phone]"], ["Stage manager", "[Name]",
          "[Phone]"]], [5.0, 6.0, 5.6]),
        ("page",),
        ("h1", "Incident log"),
        ("table", ["Time", "Where", "What happened", "Who was involved", "Action taken", "Reported by"],
         [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
         [1.8, 2.4, 4.4, 3.0, 3.0, 2.0]),
        ("h1", "Thank you"),
        ("p", "You make the day. Thank you for being part of %s." % ed),
    ]


def memo(b):
    return [
        ("eyebrow", "Memo"),
        ("title", "[Subject] in one {line}"),
        ("kv", [("To", "[Names or team]"), ("From", "[Name, role]"), ("Date", "[Date]"), ("Subject", "[Subject]")]),
        ("h2", "Why you are reading this"),
        ("p", "[One paragraph: the decision, the change or the question, and why it matters to the people on the To "
              "line.]"),
        ("h2", "What is changing"),
        ("bullets", ["[What changes, from when]", "[What stays the same]", "[Who it affects]"]),
        ("h2", "What to do next"),
        ("callout", "Do [the one thing] by [date]. Questions to [Name] at [email]."),
    ]


CERT_MERGE = [("Name", "First_name"), ("", "Last_name")]


def certificate(b):
    """Three pages: award, completion, appreciation. Delete the two you do not need."""
    out = []
    for i, (eyebrow, line, after) in enumerate([
            ("Certificate of achievement", "is awarded to", "for [what they achieved]"),
            ("Certificate of completion", "certifies that", "has completed [course or activity] on [Date]"),
            ("Certificate of appreciation", "with thanks to", "for [what they did for us]")]):
        if i:
            out.append(("page",))
        out += [("cert", eyebrow, line, after, [("First_name", "First name"), ("Last_name", "Last name")],
                 "[Name], [Role], %s" % b)]
    return out


def attendance_certificate(b):
    return [("cert", "Certificate of attendance", "certifies that", "attended «Event» on «Date», «CPD_hours» hours of CPD",
             [("First_name", "First name"), ("Last_name", "Last name")], "[Name], [Role], %s" % b)]


COVERS = {
    "Business-plan": dict(label="Business plan", title="[Company] business {plan}",
                          sub="Where we are, where we are going and what it takes to get there.",
                          meta="Prepared by [Name], [Month Year]"),
    "Employee-handbook": dict(label="Employee handbook", title="How we {work}",
                              sub="What to expect from us, and what we ask of you.", meta="Version [1.0], [Month Year]"),
    "Board-report": dict(label="Board report", title="Board report, [Month {Year}]",
                         sub="Performance, finance, people, risks and the decisions this meeting needs.",
                         meta="Prepared by [Name], [Month Year]"),
    "Post-event-report": dict(label="Post-event report", title="[Edition] in {review}",
                              sub="What happened, what people said and what we will do next time.",
                              meta="Prepared by [Name], [Month Year]"),
    "Exhibitor-manual": dict(label="Exhibitor manual", title="Your stand at {[Edition]}",
                             sub="How to build, staff and break down your stand.", meta="[Edition], [Dates]"),
    "Event-risk-assessment": dict(label="Risk assessment", title="Risk assessment and method {statement}",
                                  sub="How the event runs safely, and what we do when it does not.",
                                  meta="Prepared by [Name], [Month Year]"),
    "Event-day-pack": dict(label="Event day pack", title="The {day}, in your _hands_",
                           sub="Your role, the site, the radio and what to do when something happens.",
                           meta="[Edition], [Dates]"),
}

DOCS = {
    "Memo": dict(kind="plain", label="Memo", blocks=memo),
    "Contract": dict(kind="plain", label="Agreement", blocks=contract),
    "Partnership-agreement": dict(kind="plain", label="Partnership agreement",
                                  blocks=event_agreement("Partnership", "Partner", PARTNER_DELIVERABLES)),
    "Award-sponsorship-agreement": dict(kind="plain", label="Award sponsorship agreement",
                                        blocks=event_agreement("Award sponsorship", "Sponsor", AWARD_DELIVERABLES)),
    "Exhibitor-agreement": dict(kind="plain", label="Exhibitor agreement",
                                blocks=event_agreement("Exhibitor", "Exhibitor", EXHIBITOR_DELIVERABLES)),
    "Non-disclosure-agreement": dict(kind="plain", label="Non-disclosure agreement", blocks=nda),
    "Statement-of-work": dict(kind="plain", label="Statement of work", blocks=statement_of_work),
    "Business-plan": dict(kind="cover", blocks=business_plan),
    "Policy": dict(kind="plain", label="Policy", blocks=policy),
    "Standard-operating-procedure": dict(kind="plain", label="Procedure", blocks=sop),
    "Job-description": dict(kind="plain", label="Job description", blocks=job_description),
    "Offer-letter": dict(kind="plain", label=None, blocks=offer_letter),
    "Employee-handbook": dict(kind="cover", blocks=employee_handbook),
    "Brief": dict(kind="plain", label="Brief", blocks=brief),
    "Case-study": dict(kind="plain", label="Case study", blocks=case_study),
    "Fact-sheet": dict(kind="plain", label="Fact sheet", blocks=fact_sheet),
    "Newsletter": dict(kind="plain", label="Newsletter", blocks=newsletter),
    "Certificate": dict(kind="landscape", label="Certificate", blocks=certificate),
    "Board-report": dict(kind="cover", blocks=board_report),
    "Terms-and-conditions": dict(kind="plain", label="Terms", blocks=terms_and_conditions),
    "Post-event-report": dict(kind="cover", blocks=post_event_report),
    "Exhibitor-manual": dict(kind="cover", blocks=exhibitor_manual),
    "Speaker-brief": dict(kind="plain", label="Speaker brief", blocks=speaker_brief),
    "Host-brief": dict(kind="plain", label="Host brief", blocks=lambda b: speaker_brief(b, host=True)),
    "Event-risk-assessment": dict(kind="cover", blocks=event_risk_assessment),
    "Event-day-pack": dict(kind="cover", blocks=event_day_pack),
    "Attendance-certificate": dict(kind="landscape", label="Certificate of attendance", blocks=attendance_certificate),
    "Exhibitor-risk-assessment": dict(kind="landscape-plain", label="Risk assessment", blocks=exhibitor_risk_assessment),
}


def all_copy(brands=("ClimbUK", "ClimbGroup", "Climb27")):
    """Every string a reader sees, for the copy checker."""
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, (list, tuple)):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for y in x.values():
                walk(y)
    for b in brands:
        for name, spec in DOCS.items():
            walk(spec["blocks"](b))
            if name in COVERS:
                walk(COVERS[name])
    return out
