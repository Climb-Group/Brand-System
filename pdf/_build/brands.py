"""Per-brand settings for the brand PDFs. Copy follows the ClimbUK voice guide."""

COMMON = dict(
    phone="+44 113 541 2999",
    web="climb-uk.com",
    dates="30 June and 1 July 2027",
    tagline="The Festival for Business Growth",
)


def contact(brand):
    """Press and brand support, then partnerships. ClimbGroup pieces use the company domain."""
    domain = "climb-group.com" if brand == "ClimbGroup" else "climb-uk.com"
    return "marketing@" + domain, "partnerships@" + domain

BRANDS = {
    "ClimbUK": dict(
        key="climbuk",
        name="ClimbUK",
        ground="",            # Dark Brown
        role="The brand and the festival",
        role_line="ClimbUK is the brand on the poster: the festival, the website, the socials and everything people see first.",
        cover_photo="climb_crowd_wide.jpg",
        cover_eyebrow="Brand guidelines",
        cover_h='NOT A<br><em>CONFERENCE</em>.<br>A <span class="o">FESTIVAL</span>.',
        cover_size=140,
        cover_sub="Business with a party, not a party for business. The look, the sound and the rules that make every ClimbUK piece feel like opening night.",
        cover_sticker="Brand book",
        sheet_h='KEEP IT <em>LOUD</em>.<br>KEEP IT <span class="o">RIGHT</span>.',
        naming=[
            ("ClimbUK", "the brand and the festival. One word, capital C, capital UK."),
            ("Never", "\u201cClimb\u201d on its own, \u201cClimb UK\u201d with a space, or \u201cCLIMBUK\u201d in running text."),
            ("Editions", "Climb27 is this year, Climb26 was last year. ClimbUK endorses the edition."),
        ],
        closing_h='SEE YOU IN THE <span class="o">CROWD</span>.',
    ),
    "ClimbGroup": dict(
        key="climbgroup",
        name="ClimbGroup",
        ground="ch",          # Charcoal
        role="The company name",
        role_line="ClimbGroup is the company name: contracts, invoices, legal lines, company documents and decks, and the ClimbGroup Event App.",
        cover_photo="climb_recap_03.jpg",
        cover_eyebrow="Brand guidelines",
        cover_h='EVEN THE<br><em>SMALL</em> PRINT<br>GETS A <span class="o">STAGE</span>.',
        cover_sub="The company name, dressed for the festival. How ClimbGroup looks and sounds on contracts, documents, decks and footers.",
        cover_sticker="Brand book",
        sheet_h='<em>SMALL</em> PRINT.<br>BIG <span class="o">ENERGY</span>.',
        naming=[
            ("ClimbGroup", "the company name, for legal lines, contracts and company pieces. One word."),
            ("Never", "\u201cClimb Group\u201d with a space, \u201cClimb\u201d on its own, or a line explaining who runs what."),
            ("The app", "is the ClimbGroup Event App, always in full."),
        ],
        closing_h='SIGNED. SEALED. <span class="o">SORTED</span>.',
    ),
    "Climb27": dict(
        key="climb27",
        name="Climb27",
        ground="",
        role="This year's edition",
        role_line="Climb27 is this year's edition of ClimbUK. The edition mark leads on every event piece, with ClimbUK as the endorsement.",
        cover_photo="media_02.jpg",
        cover_eyebrow="Edition guidelines",
        cover_h='YOUR <em>BUSINESS</em>.<br>BIGGER <span class="o">STAGE</span>.',
        cover_sub="Two days of Main Stage Moments and the people you came to meet. How every Climb27 piece looks, moves and sells.",
        cover_sticker="30 June and 1 July 2027",
        sheet_h='<em>BIGGER</em> STAGE.<br>SAME <span class="o">RULES</span>.',
        naming=[
            ("Climb27", "this year's edition. One word, no space, no apostrophe."),
            ("Dates", "30 June and 1 July 2027, written in full."),
            ("Themes", "Find Your People and Main Stage Moments, always capitalised."),
        ],
        closing_h='FIND YOUR <span class="o">PEOPLE</span>.<br>THEN DO <em>BUSINESS</em>.',
    ),
}
