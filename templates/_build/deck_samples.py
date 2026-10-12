"""Example slides for every PowerPoint deck after the presentation template, in the brand voice (checked with the
climb-voice check_copy.py through pptx_build.py --copy).

DECKS is keyed by (catalogue name, external?) and holds:
    layouts   the layouts the deck carries, in order (None: all 19 of the presentation template, plus extra)
    extra     extra layouts from pptx_build.EXTRA
    slides    a function of the brand returning [(layout name, fill(tree, spec)), ...]

{word} is Climb Orange, _word_ is italic. Every number is a slot; every name is a slot.
"""
from xml.sax.saxutils import escape

import brand as B
from copy_samples import sph, sphoto

PARTNER_EMAIL = "partnerships@climb-uk.com"


def edition(b):
    return b if B.BRANDS[b]["edition"] else "[Edition]"


def host_line(b, verb="Speaking at"):
    return "%s %s" % (verb, "a ClimbGroup event" if b == "ClimbGroup" else b)


def partner_contact(b):
    return "climb-group.com" if b == "ClimbGroup" else PARTNER_EMAIL


# ---------- shapes for the org chart ----------

def org_box(t, x, y, w, h, name, role, top=False):
    fill = B.CHARCOAL if top else B.GREY
    colour, sub = (B.WHITE, B.TINT) if top else (B.CHARCOAL, B.SLATE_GREY)
    body = ('<p:txBody><a:bodyPr anchor="ctr" lIns="91440" rIns="91440"><a:normAutofit/></a:bodyPr><a:lstStyle/>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-GB" sz="1400" b="1"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/></a:rPr><a:t>%s</a:t></a:r></a:p>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-GB" sz="1200"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody>'
            % (colour, B.DISPLAY, escape(name), sub, B.BODY, escape(role)))
    t.shape(x, y, w, h, '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill, geom="roundRect",
            adj='<a:gd name="adj" fmla="val 12000"/>', name="Org box: %s" % name, text=body)


def org_line(t, x, y, w, h):
    t.shape(x, y, w, h, '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % B.SLATE, name="Org line")


def org_chart(t, spec):
    sph(t, "body", 13, "Who does what")
    sph(t, "title", None, "How the {team} fits together")
    bw, bh = 2.6, 0.95
    cx = 13.333 / 2
    org_box(t, cx - bw / 2, 2.35, bw, bh, "[Name]", "[Chief Executive]", top=True)
    org_line(t, cx - 0.02, 3.3, 0.04, 0.4)
    xs = [1.4, 4.3, 7.2, 10.1]
    org_line(t, xs[0] + bw / 2, 3.7, xs[-1] - xs[0], 0.04)
    for k, x in enumerate(xs):
        org_line(t, x + bw / 2 - 0.02, 3.7, 0.04, 0.35)
        org_box(t, x, 4.05, bw, bh, "[Name]", ["[Head of Events]", "[Head of Partnerships]", "[Head of Marketing]",
                                             "[Head of Finance]"][k])
        org_line(t, x + bw / 2 - 0.02, 5.0, 0.04, 0.3)
        org_box(t, x, 5.3, bw, bh, "[Name]", "[Role]")


# ---------- slide lists ----------

def S(**kw):
    """The fill for one slide: kw maps placeholder keys to text. Keys: eyebrow, title, sub, body, body2, col1, col2,
    date, times, numbers, labels, name, role, session, statement, line, speakers, time, stage, contact, host, end."""
    def fill(t, spec):
        m = {"eyebrow": ("body", 13), "title": ("title", None), "ctr": ("ctrTitle", None), "sub": ("subTitle", 1),
             "body": (None, 1), "body2": (None, 2), "line": ("body", 1), "col1": ("body", 16), "col2": ("body", 17),
             "date": ("body", 14), "times": ("body", 19), "role": ("body", 18), "n1": ("body", 20), "n2": ("body", 21),
             "n3": ("body", 22), "l1": ("body", 23), "l2": ("body", 24), "l3": ("body", 25), "sticker": ("body", 30),
             "time": ("body", 14), "stage": ("body", 15), "host": ("body", 14), "contact": ("body", 13),
             "section": ("body", 13)}
        for k, v in kw.items():
            if k == "photo":
                sphoto(t, 15, v[0], v[1], v[2])
                continue
            typ, idx = m[k]
            if (typ, idx) not in t.layout.phs:  # the same slot is a body or an object placeholder, by layout
                for alt in ((None, idx), ("body", idx)):
                    if alt in t.layout.phs:
                        typ, idx = alt
            sph(t, typ, idx, v)
    return fill


W, H = 13.333, 7.5
PHOTO_FULL = ("band_stage", (0, 0, W, H - 1.55), "The band playing on the main stage under orange light")
PHOTO_TITLE = ("crowd_wide", (6.2, 0, W - 6.2, H), "A packed festival crowd watching the main stage")


def title(b, eyebrow, title, sub, date=None):
    return ("Title", S(eyebrow=eyebrow, ctr=title, sub=sub, date=date or B.BRANDS[b]["edition"] or B.BRANDS[b]["url"]))


def end(b, line, button=None):
    return ("End card", S(title=line, eyebrow=B.BRANDS[b]["edition"] or B.BRANDS[b]["line"], date=button or B.BRANDS[b]["url"]))


def investor_pitch(b, external=False):
    def slides(b):
        first = (("Co-branded title", S(eyebrow=host_line(b, "Pitching at"), ctr="[Company]: {the} one-line _pitch_",
                                       sub="[Your name], [Role], [Company]"))
                 if external else title(b, "[Company]", "[Company]: {the} one-line _pitch_", "[What you do, for whom, in one line.]",
                                        "[Your name], [Role]"))
        out = [
            first,
            ("Big statement", S(title="The {problem}, in one _line_.", line="[Who has it, how often, and what it costs them.]")),
            ("Title and content", S(eyebrow="Solution", title="What we {built}",
                                    body=["[What the product does, in the customer's words]", "[Why it is different]",
                                          "[What it replaces]"])),
            ("Big numbers", S(eyebrow="Market", title="The {market}", n1="[00]", l1="[Who could buy it, with the source]",
                              n2="[00]", l2="[Who we can reach first]", n3="[00]", l3="[What they pay today]")),
            ("Title and content (light)", S(eyebrow="Product", title="How it {works}",
                                            body=["[Step one, from the customer's side]", "[Step two]", "[Step three]",
                                                  "[Add a screenshot or a photo of it in use]"])),
            ("Big numbers", S(eyebrow="Traction", title="What has {happened} so far", n1="[00]", l1="[Customers, with the date]",
                              n2="[00]", l2="[Revenue, with the period]", n3="[00]", l3="[Growth, with the period]")),
            ("Two columns (light)", S(eyebrow="Business model", title="How we make {money}", col1="Who pays", col2="What it costs us",
                                      body=["[Customer type and price]", "[How often they pay]"],
                                      body2=["[Cost to serve]", "[Margin]"])),
            ("Two columns (light)", S(eyebrow="Team", title="Who is {building} it", col1="Founders", col2="Advisers",
                                      body=["[Name, role, the one thing they have done before]", "[Name, role]"],
                                      body2=["[Name, what they bring]", "[Name, what they bring]"])),
            ("Title and content (light)", S(eyebrow="Competition", title="Who else is {here}",
                                            body=["[Competitor]: [what they do well, where we win]",
                                                  "[Competitor]: [what they do well, where we win]",
                                                  "[The way customers solve it today without any of us]"])),
            ("Section (orange)", S(eyebrow="10", title="The _ask_: [amount]", line="[What it funds and the milestone it reaches.]")),
        ]
        if external:
            out.append(("Co-branded end", S(title="Thank {you}", contact="[Your name]\n[email]\n[website]",
                                            host=host_line(b, "Pitching at"))))
        else:
            out.append(end(b, "Let's {talk}", "[email]"))
        return out
    return slides


def sales_deck(b):
    ed = edition(b)
    return [
        title(b, "For [audience]", "The room where {growth} _starts_.", "What %s gives [audience], and how to be part of it." % ed),
        ("Two columns (light)", S(eyebrow="Who it is for", title="Two ways to get {more} from it", col1="For founders", col2="For partners",
                                  body=["Learn from peers who are one step ahead", "Find investors looking for real deal flow",
                                        "Leave with follow-ups that matter"],
                                  body2=["Put your brand in front of the people you want to reach",
                                         "Host a roundtable on the problem you solve", "Meetings with the right people"])),
        ("Title and content", S(eyebrow="What you get", title="What is {included}",
                                body=["[The thing they get first]", "[The thing they get next]", "[What happens after the event]"])),
        ("Agenda (light)", S(eyebrow="How it works", title="From {booking} to the day",
                             times=["Step 1", "Step 2", "Step 3", "Step 4"],
                             body=["Book a call with the team", "Pick the package that fits", "We build it with you",
                                   "The day, and the follow-ups"])),
        ("Quote", S(body="[Put the quote here, word for word, exactly as it was said, with permission.]",
                    title="[First name Last name]", eyebrow="[Role], [Company]")),
        ("Two columns (light)", S(eyebrow="Packages", title="Pick the {package} that fits", col1="[Package one]", col2="[Package two]",
                                  body=["[What is included]", "[What is included]", "[Price]"],
                                  body2=["[What is included]", "[What is included]", "[Price]"])),
        end(b, "Book a {call}", "Book a call"),
    ]


def qbr(b):
    return [
        title(b, "Quarterly business review", "[Quarter] in {review}", "Where we are against plan, and what changes next quarter.",
              "[Date]"),
        ("Agenda (light)", S(eyebrow="Agenda", title="What we will {cover}", times=["1", "2", "3", "4", "5"],
                             body=["Headlines", "What went well and what did not", "Pipeline and finance", "Next quarter",
                                   "Decisions needed"])),
        ("Big numbers", S(eyebrow="Headlines", title="The quarter in {numbers}", n1="[00]", l1="[Revenue against plan]",
                          n2="[00]", l2="[Tickets or customers against plan]", n3="[00]", l3="[Cash at quarter end]")),
        ("Two columns (light)", S(eyebrow="Review", title="What {worked}, what did _not_", col1="Went well", col2="Did not",
                                  body=["[What, and why]", "[What, and why]"], body2=["[What, why, and the fix]", "[What]"])),
        ("Title and content (light)", S(eyebrow="Pipeline", title="What is {coming}",
                                        body=["[Signed this quarter]", "[In negotiation]", "[Lost, and why]"])),
        ("Big numbers", S(eyebrow="Finance", title="Money in, money {out}", n1="[00]", l1="[Income]", n2="[00]", l2="[Costs]",
                          n3="[00]", l3="[Net]")),
        ("Title and content", S(eyebrow="Next quarter", title="What {changes}",
                                body=["[Priority one, owner, date]", "[Priority two, owner, date]", "[Priority three, owner, date]"])),
        ("Title and content (light)", S(eyebrow="Decisions", title="What we need to {decide}",
                                        body=["[Decision, recommendation, by when]", "[Decision, recommendation, by when]"])),
        end(b, "Thank {you}", "[Next review date]"),
    ]


def board_presentation(b):
    return [
        title(b, "Board meeting", "Board {update}, [Month Year]", "Performance, finance, risks and the decisions this meeting needs.",
              "[Date]"),
        ("Agenda (light)", S(eyebrow="Agenda", title="This {meeting}", times=["1", "2", "3", "4", "5"],
                             body=["Summary", "Performance against plan", "Finance", "Risks", "Decisions"])),
        ("Big statement", S(title="[The one line the board should {remember}.]", line="[The two things that changed since last time.]")),
        ("Big numbers", S(eyebrow="Performance", title="Against {plan}", n1="[00]", l1="[Revenue, plan and actual]",
                          n2="[00]", l2="[Tickets or customers, plan and actual]", n3="[00]", l3="[Cash]")),
        ("Two columns (light)", S(eyebrow="Finance", title="Profit and {cash}", col1="Profit and loss", col2="Cash and forecast",
                                  body=["[Revenue]", "[Costs]", "[Net]"], body2=["[Cash today]", "[Forecast to year end]", "[Runway]"])),
        ("Title and content (light)", S(eyebrow="Risks", title="What could go {wrong}",
                                        body=["[Risk, score, trend, what we are doing]", "[Risk, score, trend, what we are doing]"])),
        ("Title and content (light)", S(eyebrow="Decisions", title="What we ask the {board}",
                                        body=["[Decision, recommendation, by when]", "[Decision, recommendation, by when]"])),
        end(b, "Thank {you}", "[Next meeting date]"),
    ]


def kick_off(b):
    return [
        title(b, "Project kick-off", "[Project] starts {here}", "What we are doing, who is doing it and how we will work.", "[Date]"),
        ("Big statement", S(title="Why this {project}, why _now_", line="[The problem it solves and what happens if we do nothing.]")),
        ("Title and content", S(eyebrow="Goals", title="What {done} looks like",
                                body=["[Goal one, and how we will measure it]", "[Goal two]", "[Goal three]"])),
        ("Two columns (light)", S(eyebrow="Scope", title="In and {out}", col1="In scope", col2="Out of scope",
                                  body=["[What we will do]", "[What we will do]"], body2=["[What we will not do]", "[What waits]"])),
        ("Two columns", S(eyebrow="Team", title="Who does {what}", col1="Core team", col2="Who we need",
                          body=["[Name, role]", "[Name, role]", "[Name, role]"], body2=["[Decision maker]", "[Supplier or partner]"])),
        ("Agenda (light)", S(eyebrow="Timeline", title="The {milestones}", times=["[Date]", "[Date]", "[Date]", "[Date]"],
                             body=["Kick-off", "[First version]", "[Review]", "Launch"])),
        ("Title and content (light)", S(eyebrow="Ways of working", title="How we {work} together",
                                        body=["[Where the plan lives and who updates it]", "[The weekly check-in]",
                                              "[How decisions get made]", "[Where to raise a risk]"])),
        end(b, "Let's {go}", "[First check-in date]"),
    ]


def training_deck(b):
    return [
        title(b, "Training", "[Course title] in {practice}", "What you will learn, and what you will be able to do afterwards.",
              "[Trainer name], [Date]"),
        ("Agenda (light)", S(eyebrow="Agenda", title="What you will {learn}", times=["1", "2", "3", "4"],
                             body=["[Topic one]", "[Topic two]", "[Topic three]", "Check your understanding"])),
        ("Section (orange)", S(eyebrow="01", title="[Topic one]", line="[What this part covers, in one line.]")),
        ("Title and content (light)", S(eyebrow="[Topic one]", title="The {key} points",
                                        body=["[Point one]", "[Point two]", "[Point three]"])),
        ("Two columns (light)", S(eyebrow="[Topic one]", title="Do and {do not}", col1="Do", col2="Do not",
                                  body=["[Do this]", "[Do this]"], body2=["[Not this]", "[Not this]"])),
        ("Quote", S(body="[A line from someone who learned this the expensive way, with permission.]",
                    title="[First name Last name]", eyebrow="[Role], [Company]")),
        ("Title and content (light)", S(eyebrow="Check your understanding", title="Try {it}",
                                        body=["[Question one]", "[Question two]", "[Question three]"])),
        end(b, "Thank {you}", "[Where to find the materials]"),
    ]


def all_hands(b):
    return [
        title(b, "All-hands", "[Month] all-{hands}", "What happened, what is next and who made it happen.", "[Date]"),
        ("Agenda (light)", S(eyebrow="Agenda", title="Today", times=["1", "2", "3", "4", "5"],
                             body=["Headlines", "Wins", "Team news", "What is next", "Shout-outs"])),
        ("Big numbers", S(eyebrow="Headlines", title="The month in {numbers}", n1="[00]", l1="[What it measures]", n2="[00]",
                          l2="[What it measures]", n3="[00]", l3="[What it measures]")),
        ("Full photo", S(photo=PHOTO_FULL, sticker="Wins", title="[The {win} of the month]", line="[Who, where, what happened]")),
        ("Title and content (light)", S(eyebrow="Team news", title="Who is {new}, who is _moving_",
                                        body=["[Name joins as Role]", "[Name moves to Team]", "[Birthdays and milestones]"])),
        ("Title and content", S(eyebrow="What is next", title="The next {month}",
                                body=["[Priority one, owner]", "[Priority two, owner]", "[Date everyone should know]"])),
        ("Quote", S(body="[A thank-you to someone who went the extra mile, in the words of the person they helped.]",
                    title="[First name Last name]", eyebrow="[Team]")),
        end(b, "Thank {you}", "[Next all-hands date]"),
    ]


def org_chart_deck(b):
    return [
        title(b, "Org chart", "How the {team} fits _together_", "Who does what, and who to ask.", "[Date]"),
        ("Title only (light)", org_chart),
        ("Title and content (light)", S(eyebrow="How to use this", title="Editing the {chart}",
                                        body=["Each box is a shape: click it and type the name and role",
                                              "Copy a box and its line to add a person; delete both to remove one",
                                              "Keep one level per row so the chart reads top to bottom"])),
    ]


def partner_prospectus(b):
    ed = edition(b)
    packages = [("Headline", ["Your brand across the festival: stage screens, signage, the website and the app",
                             "A main stage moment", "Expo space, delegate passes and drinks reception tickets"]),
                ("Digital", ["Your brand on the website, the app and every email", "A feature in the agenda"]),
                ("Event", ["Your brand on the day: signage, screens and the agenda", "Delegate passes"]),
                ("Stage", ["A talk or panel slot on a stage", "Your brand on that stage's screens"]),
                ("Showcase stage", ["Your name on a stage for the two days", "A slot in its running order"]),
                ("Meeting space", ["A hosted space for meetings with the right people", "Your brand on the space"]),
                ("Award sponsor", ["A ClimbAwards category presented by you", "A seat on the judging panel",
                                   "Your brand on the award and the awards night screens"])]
    out = [
        title(b, "Partner prospectus", "Partner with _us_ at {%s}" % ed, "Put your brand in front of the people you want to reach."),
        ("Big statement", S(title="Not a conference. A {festival} for _business_ growth.",
                            line="Two days of main stage moments, roundtables and the people who move businesses forward.")),
        ("Title and content", S(eyebrow="Why partner", title="What you {get}",
                                body=["Meetings with the right people, in a room built for conversation",
                                      "Your brand where the people you want to reach are looking",
                                      "A stage, a roundtable or an award that puts your expertise in the open",
                                      "A team that builds the partnership with you, before, during and after"])),
        ("Two columns (light)", S(eyebrow="Who you meet", title="The {room}", col1="Growing companies",
                                  col2="The people around them",
                                  body=["Founders and growing companies", "Fellow founders one step ahead"],
                                  body2=["Investors here to find their next deal", "Industry leaders and advisers",
                                         "Universities and researchers", "Public sector"])),
        ("Quote", S(body="[A partner's words, exactly as they said them, with their permission.]", title="[First name Last name]",
                    eyebrow="[Role], [Partner company]")),
        ("Section (orange)", S(eyebrow="02", title="Pick your {package}", line="Every package comes with a named Partner Manager.")),
    ]
    for name, inc in packages:
        out.append(("Title and content (light)", S(eyebrow="Package", title="{%s}" % name, body=inc + ["Price: [amount] plus VAT"])))
    out.append(("End card", S(title="Book a {call}", eyebrow="with the partnerships team: %s" % partner_contact(b),
                               date="Book a call")))
    return out


def stage_holding(b, external=False):
    def slides(b):
        ed = edition(b)
        line = B.BRANDS[b]["line"]
        out = []
        if external:
            out.append(("Co-branded title", S(eyebrow=host_line(b, "Hosted at"), ctr="[Your stage] {welcomes} you",
                                               sub="[The first session starts at 09:30]")))
        else:
            out.append(("Holding", S(title="Welcome to {%s}" % ed, line="Find your seat. The first session starts at [09:30].",
                                     eyebrow=line)))
        out += [
            ("Up next", S(eyebrow="Up next", title="[Session title]", body="[Speaker name], [Company]\n[Speaker name], [Company]",
                          time="[11:00]", stage="[Main stage]")),
            ("Holding", S(title="{Break}", line="Back at [14:00]. The expo and coffee are through the doors behind you.",
                          eyebrow=line)),
            ("Holding", S(title="Back at {[14:00]}", line="[Session title] with [Speaker name]", eyebrow=line)),
        ]
        if not external:
            out += [
                ("Logo grid (light)", S(eyebrow="Thank you to our partners", title="Made possible by our {partners}")),
                ("Title and content", S(eyebrow="House rules", title="Three things before we {start}",
                                        body=["Phones on silent, cameras welcome",
                                              "The agenda, the map and your meetings are in the ClimbGroup Event App",
                                              "Ask a crew member in a crew shirt if you need anything"])),
                ("Holding", S(title="See you {tomorrow}", line="Doors open at [08:30]. Tonight: the after party.", eyebrow=line)),
            ]
        out.append(("Co-branded end", S(title="Thank {you}", contact="[Your stage], hosted by [Company]", host=host_line(b, "Hosted at")))
                   if external else end(b, "See you {there}"))
        return out
    return slides


def speaker_slides(b, external=False):
    def slides(b):
        first = (("Co-branded title", S(eyebrow=host_line(b), ctr="[Your talk {title}]", sub="[Your name], [Role], [Company]"))
                 if external else title(b, host_line(b), "[Your talk {title}]", "[Your name], [Role], [Company]"))
        out = [
            first,
            ("Agenda (light)", S(eyebrow="Agenda", title="What we will {cover}", times=["1", "2", "3"],
                                 body=["[Point one]", "[Point two]", "[What to do next]"])),
            ("Title and content (light)", S(eyebrow="[Section]", title="[Slide {title}]",
                                            body=["[One idea per line]", "[Short enough to read in a glance]", "[Three lines at most]"])),
            ("Quote", S(body="[A line worth remembering, from someone who said it, with permission.]", title="[First name Last name]",
                        eyebrow="[Role], [Company]")),
            ("Big numbers", S(eyebrow="The number", title="One {fact}", n1="[00]", l1="[What it measures, and the source]",
                              n2="[00]", l2="[What it measures, and the source]", n3="[00]", l3="[What it measures, and the source]")),
            ("Full photo", S(photo=PHOTO_FULL, sticker="[Sticker]", title="[Caption {headline}]", line="[Who, where, what is happening]")),
        ]
        if external:
            out.append(("Co-branded end", S(title="Thank {you}", contact="[Your name]\n[email]\n[website]", host=host_line(b))))
        else:
            out.append(end(b, "Thank {you}", "[email]"))
        return out
    return slides


EXTERNAL_LAYOUTS = ["Co-branded title", "Agenda (light)", "Title and content", "Title and content (light)",
                    "Two columns (light)", "Section (orange)", "Big statement", "Big numbers", "Quote", "Full photo",
                    "Holding", "Up next", "Co-branded end"]
EXTERNAL_EXTRA = ("Holding", "Up next", "Co-branded title", "Co-branded end")

DECKS = {
    ("Investor-pitch-deck", False): dict(slides=investor_pitch(None)),
    ("Sales-deck", False): dict(slides=sales_deck),
    ("Quarterly-business-review", False): dict(slides=qbr),
    ("Board-presentation", False): dict(slides=board_presentation),
    ("Project-kick-off", False): dict(slides=kick_off),
    ("Training-deck", False): dict(slides=training_deck),
    ("All-hands", False): dict(slides=all_hands),
    ("Org-chart", False): dict(slides=org_chart_deck),
    ("Partner-prospectus", False): dict(slides=partner_prospectus),
    ("Stage-holding-slides", False): dict(slides=stage_holding(None), extra=("Holding", "Up next", "Logo grid (light)")),
    ("Speaker-slides", False): dict(slides=speaker_slides(None)),
    ("Investor-pitch-deck", True): dict(slides=investor_pitch(None, True), layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
    ("Stage-holding-slides", True): dict(slides=stage_holding(None, True), layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
    ("Speaker-slides", True): dict(slides=speaker_slides(None, True), layouts=EXTERNAL_LAYOUTS, extra=EXTERNAL_EXTRA),
}
