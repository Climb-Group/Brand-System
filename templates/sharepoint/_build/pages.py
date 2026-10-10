"""The SharePoint brand centre: every page, its sections and its copy. One source for the script, the guide and the
copy check. Text is HTML for the SharePoint text web part (h2, h3, p, ul, a, strong only).

{SITE} is the site address, {A} and {B} the two marketing content sites, {P} the brand pack download.
"""

NAV = [
    # (menu label, [page slugs]) ; a group with one page links straight to it
    ("Brand", ["our-brand", "voice", "logos", "colour-and-type"]),
    ("Artwork", ["photography", "drawings-and-devices", "artwork-library"]),
    ("Make", ["templates", "microsoft-365"]),
    ("Guidelines", ["guidelines"]),
    ("Get help", ["get-help"]),
]


def link(href, text):
    return '<a href="%s">%s</a>' % (href, text)


PAGES = {}


def page(slug, title, description, sections, tiles=None, hero=None):
    PAGES[slug] = {"slug": slug, "title": title, "description": description, "sections": sections,
                   "tiles": tiles or [], "hero": hero}


# A section: (layout, emphasis, [column html, ...]). layout: OneColumn, TwoColumn, ThreeColumn.
# emphasis: 0 none, 1 neutral, 2 soft, 3 strong (strong takes the theme's dark ground).

page("home", "Brand centre",
     "Everything that makes ClimbUK, ClimbGroup and Climb27 look and sound like themselves, in one place.",
     [
         ("OneColumn", 3, [
             "<h2>Business with a party. Built to the brand.</h2>"
             "<p>Logos, colours, type, photography, templates and the rules that tie them together. Start here, "
             "make it on brand and get it out the door.</p>"]),
         ("ThreeColumn", 0, [
             "<h3>New here?</h3><p>Read the story behind the name, the voice in four lines and the five visual "
             "rules. It takes ten minutes and it saves hours.</p><p>" + link("{SITE}/SitePages/our-brand.aspx",
                                                                             "Start with our brand") + "</p>",
             "<h3>Making something?</h3><p>Open a template that already has the fonts, colours and layouts set: "
             "documents, slides, spreadsheets, video titles and call backgrounds.</p><p>" +
             link("{SITE}/SitePages/templates.aspx", "Open the templates") + "</p>",
             "<h3>Need a file?</h3><p>Every logo, photo, drawing and finished piece of artwork lives in the "
             "marketing content library, sorted by brand.</p><p>" +
             link("{SITE}/SitePages/artwork-library.aspx", "Go to the artwork library") + "</p>"]),
         ("TwoColumn", 2, [
             "<h2>Three brands, one family</h2>"
             "<p><strong>ClimbUK</strong> is the brand on the poster: the festival and everything around it. "
             "<strong>Climb27</strong> is this year's edition and leads on event pieces, with ClimbUK as the "
             "endorsement. <strong>ClimbGroup</strong> is the company name, for legal lines, contracts and "
             "corporate pieces.</p>",
             "<h2>The tagline</h2><p><strong>The Festival for Business Growth.</strong> \"The Festival of "
             "Business Growth\" is the spoken form and is also right. Use one form per piece.</p>"
             "<p>Climb27 headline: <strong>Your business. Bigger stage.</strong></p>"]),
         ("OneColumn", 0, [
             "<h2>The rules on one page</h2><p>Short on time? The key rules for each brand fit on a single "
             "page.</p><ul>"
             "<li>" + link("{SITE}/BrandFiles/climbuk_key-rules.pdf", "ClimbUK key rules (PDF)") + "</li>"
             "<li>" + link("{SITE}/BrandFiles/climb27_key-rules.pdf", "Climb27 key rules (PDF)") + "</li>"
             "<li>" + link("{SITE}/BrandFiles/climbgroup_key-rules.pdf", "ClimbGroup key rules (PDF)") +
             "</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Questions about the brand?</h2><p>The marketing team checks artwork, answers questions and "
             "shares new files. Email " + link("mailto:marketing@climb-uk.com", "marketing@climb-uk.com") +
             " and say what you are making.</p>"]),
     ],
     hero=[
         ("Our brand", "our-brand", "The name, the voice and the five visual rules."),
         ("Templates", "templates", "Documents, slides and video, ready to go."),
         ("Logos", "logos", "The right logo for every ground."),
         ("Microsoft 365 kit", "microsoft-365", "Teams themes, backgrounds and signatures."),
         ("Artwork library", "artwork-library", "Every file, sorted by brand."),
     ],
     tiles=["voice", "colour-and-type", "photography", "drawings-and-devices", "guidelines", "get-help"])

page("our-brand", "Our brand",
     "Where the name comes from, what the brand stands for and the rules every piece follows.",
     [
         ("OneColumn", 3, [
             "<h2>Not a conference. A festival for business growth.</h2>"
             "<p>ClimbUK is business with a party, not a party for business. Real crowds under stage light, big "
             "type and an orange that glows, with a clear next step every time.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Where the name comes from</h2>"
             "<p>The name comes from the Investor Ladder. A business climbs the ladder to reach the next rung: an "
             "investor who fits where it is now. Investors pass businesses up and down the ladder to the rung that "
             "suits what they need.</p><p>ClimbUK is a business event, never a sport or outdoors event. Talk "
             "about climbing only when the business meaning is clear in the same line, and never use ropes, walls "
             "or mountain pictures.</p>",
             "<h2>Our two themes</h2><p><strong>Find Your People.</strong> The people you meet are the reason to "
             "come: fellow founders, investors, advisers and partners.</p><p><strong>Main Stage Moments.</strong> "
             "Short, big moments: sets, announcements, awards and our own formats.</p>"]),
         ("OneColumn", 1, [
             "<h2>The five visual rules</h2><ul>"
             "<li><strong>Dark first.</strong> Dark Brown or Charcoal is the default ground. Light grounds are for "
             "reading-heavy pieces.</li>"
             "<li><strong>Orange leads, it does not flood.</strong> One orange button per view, with orange "
             "markers around it.</li>"
             "<li><strong>Type does the shouting.</strong> Big uppercase Montserrat, one word in orange and one in "
             "italic.</li>"
             "<li><strong>Real people, real light.</strong> Our own festival photos, never stock.</li>"
             "<li><strong>Contrast is not optional.</strong> Every text colour has a tested pair.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Writing the words?</h2><p>The voice has four lines and a short list of rules. Read them before "
             "you write a headline.</p><p>" + link("{SITE}/SitePages/voice.aspx", "Read the voice guide") +
             "</p>"]),
     ],
     tiles=["voice", "logos", "colour-and-type", "photography"])

page("voice", "Voice",
     "How ClimbUK sounds: headline energy with the discipline of a good adviser.",
     [
         ("OneColumn", 3, [
             "<h2>Exciting and useful, in every line.</h2>"
             "<p>Write like it belongs on a festival poster, then make sure the reader knows exactly what to do "
             "next.</p>"]),
         ("TwoColumn", 0, [
             "<h2>The voice in four lines</h2><ul>"
             "<li><strong>Headline energy.</strong> Short, rhythmic, confident.</li>"
             "<li><strong>Doing, not dreaming.</strong> Name the outcome and the next step.</li>"
             "<li><strong>Curated, not crowded.</strong> Sell the right people in the room, never size.</li>"
             "<li><strong>Personal, not generic.</strong> Write for one audience at a time.</li></ul>",
             "<h2>Rules that always apply</h2><ul>"
             "<li>No emojis, no exclamation marks and no long dashes.</li>"
             "<li>Always write the full name: ClimbUK, ClimbGroup or Climb27.</li>"
             "<li>No promised outcomes and no promised number of meetings.</li>"
             "<li>No audience sizes or numbers we have not published.</li>"
             "<li>Links say where they go, never \"click here\".</li></ul>"]),
         ("OneColumn", 1, [
             "<h2>Words we use</h2><ul>"
             "<li><strong>agenda</strong> for the event schedule.</li>"
             "<li><strong>Find investors looking for real deal flow</strong>, so nothing reads as a promised "
             "meeting.</li>"
             "<li><strong>connect you with</strong> the right people.</li>"
             "<li><strong>fractional leaders</strong> take responsibility for a function; keep them "
             "separate from advisers.</li>"
             "<li><strong>public sector</strong> for every public body in one phrase.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Want the full guide?</h2><p>The voice chapter covers audiences, channels, the glossary and worked "
             "examples.</p><p>" + link("{SITE}/SitePages/guidelines.aspx", "Open the guidelines") + "</p>"]),
     ],
     tiles=["our-brand", "guidelines", "templates", "get-help"])

page("logos", "Logos",
     "Every logo for ClimbUK, ClimbGroup and Climb27, and the right one for each ground.",
     [
         ("OneColumn", 3, [
             "<h2>The right logo. Every time.</h2>"
             "<p>Use the master files only. Never redraw, recolour, stretch or outline a logo.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Which file to use</h2><ul>"
             "<li><strong>Reversed</strong>: the default, for Dark Brown, Charcoal and dark photos.</li>"
             "<li><strong>Full colour light</strong>: for white grounds.</li>"
             "<li><strong>Full colour grey</strong>: for Light Grey grounds.</li>"
             "<li><strong>Mono white or mono dark</strong>: one colour print and busy photos.</li>"
             "<li><strong>Tagline lockup</strong>: with The Festival for Business Growth.</li></ul>",
             "<h2>Square icons</h2><p>The <strong>li monogram</strong> is for favicons, app icons and anything "
             "under 64 pixels. The <strong>stacked tile</strong>, with the name on two lines, is for social avatars and larger "
             "squares.</p><h3>Clear space and size</h3><p>Keep the height of the large C clear on every side. "
             "Minimum width is 120 pixels on screen and 30 millimetres in print.</p>"]),
         ("OneColumn", 1, [
             "<h2>Get the files</h2><p>Logo masters for every brand, as scalable vector graphics (SVG) and PNG images, with a contact "
             "sheet that "
             "shows each one on every ground.</p><p>" + link("{A}", "Open the logo folders in marketing content") +
             "</p>"]),
         ("OneColumn", 3, [
             "<h2>Putting a logo on a photo?</h2><p>Sit it on the darkened part of the picture, or use the mono "
             "white version.</p><p>" + link("{SITE}/SitePages/photography.aspx", "See the photography rules") +
             "</p>"]),
     ],
     tiles=["colour-and-type", "photography", "templates", "artwork-library"])

page("colour-and-type", "Colour and type",
     "The palette, the five presets that keep text readable, and the two typefaces.",
     [
         ("OneColumn", 3, [
             "<h2>Orange leads. Contrast decides.</h2>"
             "<p>Five colours, five tested presets and two typefaces. Pick a preset and the readable pairs come "
             "with it.</p>"]),
         ("ThreeColumn", 0, [
             "<h3>The palette</h3><ul>"
             "<li><strong>Brand orange</strong> #E8712A</li><li><strong>Dark Brown</strong> #1E0F05</li>"
             "<li><strong>Charcoal</strong> #242322</li><li><strong>Light Grey</strong> #E9E9E9</li>"
             "<li><strong>White</strong> #FFFFFF</li></ul>",
             "<h3>Orange for small text</h3><ul>"
             "<li>On white: <strong>Orange Text</strong> #C55308</li>"
             "<li>On Light Grey: #B04902</li>"
             "<li>On Dark Brown and Charcoal: <strong>Orange Tint</strong> #F2AE86 for links, brand orange for "
             "everything else</li></ul>",
             "<h3>Type</h3><p><strong>Montserrat</strong> Bold, ExtraBold and Black for headlines, uppercase with "
             "tight leading. <strong>Open Sans</strong> for everything you read.</p><p>Both are free to use under "
             "a free, open font licence.</p>"]),
         ("OneColumn", 1, [
             "<h2>Never do this</h2><ul>"
             "<li>White text on brand orange below 19 pixels bold.</li>"
             "<li>Light Grey or slate text on any orange.</li>"
             "<li>Dark Brown labels on orange buttons.</li>"
             "<li>Orange on orange, or a hover state lighter than the button.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Building for screens?</h2><p>The digital user interface (UI) guide has the type scale, spacing, buttons and the "
             "accessible AAA themes.</p><p>" + link("{SITE}/SitePages/guidelines.aspx", "Open the guidelines") +
             "</p>"]),
     ],
     tiles=["logos", "templates", "guidelines", "drawings-and-devices"])

page("photography", "Photography",
     "Real people under real stage light: how to choose and use festival photos.",
     [
         ("OneColumn", 3, [
             "<h2>Real people. Real light.</h2>"
             "<p>Our own festival photos of real attendees, speakers and stage moments, used with consent. Never "
             "stock handshakes or empty rooms.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Choose a photo that</h2><ul>"
             "<li>shows faces, laughter and close conversations;</li>"
             "<li>has orange lanyards, branded backdrops or stage light in it;</li>"
             "<li>has no readable name badges and no children;</li>"
             "<li>is at least 4K, and never upscaled.</li></ul>",
             "<h2>Put words on it like this</h2><p>Text on a photo always sits on a solid ground or a proper fade "
             "to Dark Brown, never over a busy part of the picture.</p><p>Dense photo walls beat one lonely "
             "picture.</p>"]),
         ("OneColumn", 1, [
             "<h2>Find the photos</h2><p>The full candid set from Climb26 lives in marketing content, sorted by "
             "moment: crowds, stage, meetings, joy, awards and more.</p><p>" +
             link("{B}", "Open the photo library in marketing content") + "</p>"]),
         ("OneColumn", 3, [
             "<h2>Shooting or filming at an event?</h2><p>Capture at 4K or above, 8K where you can.</p><p>" +
             link("{SITE}/SitePages/guidelines.aspx", "Read the photography and video guides") + "</p>"]),
     ],
     tiles=["artwork-library", "drawings-and-devices", "logos", "guidelines"])

page("drawings-and-devices", "Drawings and devices",
     "The hand drawn line set, the background motifs and the festival devices that carry the energy.",
     [
         ("OneColumn", 3, [
             "<h2>Make it feel like a festival.</h2>"
             "<p>Smooth, tablet-drawn lines, four motif families and a handful of poster devices. Use two or three "
             "per piece, not all of them at once.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Drawings</h2><p>One clean line drawing per object, from tickets and microphones to rockets and "
             "ladders. Each has a soft fill shape behind it for depth.</p><p>They default to brand orange and "
             "work on every ground.</p>",
             "<h2>Motifs</h2><ul>"
             "<li><strong>The Ascent</strong>: rising steps, the rungs of the Investor Ladder.</li>"
             "<li><strong>Contours</strong>: rings of growth spreading out from one point.</li>"
             "<li><strong>Stage Light</strong>: soft orange beams on a dark ground.</li>"
             "<li><strong>Connections</strong>: dots joined by fine lines, people finding each other.</li></ul>"]),
         ("OneColumn", 1, [
             "<h2>Festival devices</h2><ul>"
             "<li>The orange word and the italic word in a headline.</li>"
             "<li>The short orange rule above a statement.</li>"
             "<li>Stickers tilted a few degrees on a card corner.</li>"
             "<li>Ticket cards with stub notches and a dashed tear line.</li>"
             "<li>Outline numerals for section numbers.</li>"
             "<li>Photo fades and an orange stage glow.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Need a drawing?</h2><p>Every drawing is in marketing content, ready for print and screen.</p><p>" +
             link("{A}", "Open the drawings in marketing content") + "</p>"]),
     ],
     tiles=["photography", "colour-and-type", "artwork-library", "templates"])

page("templates", "Templates",
     "Documents, slides, spreadsheets and video templates with the fonts, colours and layouts already set.",
     [
         ("OneColumn", 3, [
             "<h2>Start from the right file.</h2>"
             "<p>Never start from a blank page. Every template has the brand fonts, colours and layouts built "
             "in.</p>"]),
         ("ThreeColumn", 0, [
             "<h3>In Word and PowerPoint</h3><p>Choose <strong>New</strong>, then the <strong>ClimbUK</strong> "
             "tab under your organisation's templates. Letterhead, proposal, report, press release, meeting "
             "notes and the 16:9 deck, for each brand.</p>",
             "<h3>In Excel</h3><p>Event budget, run sheet, content calendar and partner pipeline, with the brand "
             "table styles and chart colours. Find "
             "them in the same place as the Word and PowerPoint templates.</p>",
             "<h3>For video</h3><p>Titles, lower thirds, a colour look and motion loops for editing apps. The "
             "install package sets them up on Windows, macOS and Linux.</p>"]),
         ("OneColumn", 1, [
             "<h2>Get the template files</h2><ul>"
             "<li>" + link("{SITE}/BrandTemplates", "Open the brand templates library") + "</li>"
             "<li>" + link("{P}", "Download the full brand pack") + "</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Presenting on a call?</h2><p>Use a branded meeting theme and background as well.</p><p>" +
             link("{SITE}/SitePages/microsoft-365.aspx", "Open the Microsoft 365 kit") + "</p>"]),
     ],
     tiles=["microsoft-365", "colour-and-type", "logos", "get-help"])

page("microsoft-365", "Microsoft 365 kit",
     "Teams meeting themes and backgrounds, email signatures and the brand across Microsoft 365.",
     [
         ("OneColumn", 3, [
             "<h2>Show up on brand.</h2>"
             "<p>Branded meetings, backgrounds and signatures, so every call and email looks like the "
             "festival.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Meeting backgrounds</h2><p>Twelve 4K backgrounds for each brand: photo, calm, festival and "
             "frosted glass. In Teams, open <strong>Effects and avatars</strong>, then "
             "<strong>Video effects</strong>, and pick one from the organisation set.</p><p>The logo sits top "
             "left and the middle stays calm for you.</p>",
             "<h2>Meeting themes</h2><p>Branded meetings show the brand logo, image and colour in the join screen "
             "and meeting window. Your meeting policy sets the theme for you.</p>"]),
         ("TwoColumn", 1, [
             "<h2>Email signatures</h2><p>Signatures are set centrally with the social buttons for LinkedIn, "
             "Instagram, TikTok, X and Bluesky. Do not add your own logo or banner.</p>",
             "<h2>Fonts and colours in your apps</h2><p>Montserrat and Open Sans are set as the brand fonts across "
             "the brand centre and the templates.</p>"]),
         ("OneColumn", 3, [
             "<h2>Making slides for a call?</h2><p>Start from the brand deck.</p><p>" +
             link("{SITE}/SitePages/templates.aspx", "Open the templates") + "</p>"]),
     ],
     tiles=["templates", "artwork-library", "logos", "get-help"])

page("artwork-library", "Artwork library",
     "Finished artwork and source files for every brand: social, print, stage, email and video.",
     [
         ("OneColumn", 3, [
             "<h2>Every file. One place.</h2>"
             "<p>Social posts, banners, print, stage screens and email artwork, ready to use or adapt.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Marketing content</h2><p>The working library for campaigns: finished artwork, photos and "
             "drawings, sorted by brand and campaign.</p><p>" + link("{A}", "Open marketing content") + "</p>",
             "<h2>Photos and video</h2><p>Festival photography and video, sorted by moment, ready for layouts and "
             "posts.</p><p>" + link("{B}", "Open the photo and video library") + "</p>"]),
         ("OneColumn", 1, [
             "<h2>What you will find</h2><ul>"
             "<li>Social banners, headers, posts and stories at twice the platform size.</li>"
             "<li>Posters, pull-up banners, badges, lanyards and merch at print resolution.</li>"
             "<li>Holding slides, lower thirds and name cards for the big screen, all 4K.</li>"
             "<li>Email banners and the signature footer.</li>"
             "<li>Desktop and phone wallpapers.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Cannot find it?</h2><p>Ask the marketing team before you make a new version.</p><p>" +
             link("{SITE}/SitePages/get-help.aspx", "Get help with artwork") + "</p>"]),
     ],
     tiles=["photography", "logos", "templates", "drawings-and-devices"])

page("guidelines", "Guidelines",
     "The full brand book chapters: voice, digital UI, motion, photography, video, print, press and signatures.",
     [
         ("OneColumn", 3, [
             "<h2>The whole brand book.</h2>"
             "<p>Guiding, not restrictive. Read the chapter for what you are making.</p>"]),
         ("ThreeColumn", 0, [
             "<h3>Brand books</h3><ul>"
             "<li>" + link("{SITE}/BrandFiles/climbuk_brand-guidelines.pdf", "ClimbUK brand guidelines (PDF)") +
             "</li><li>" + link("{SITE}/BrandFiles/climb27_brand-guidelines.pdf",
                                "Climb27 brand guidelines (PDF)") +
             "</li><li>" + link("{SITE}/BrandFiles/climbgroup_brand-guidelines.pdf",
                                "ClimbGroup brand guidelines (PDF)") + "</li></ul>",
             "<h3>One page rules</h3><ul>"
             "<li>" + link("{SITE}/BrandFiles/climbuk_key-rules.pdf", "ClimbUK key rules (PDF)") + "</li>"
             "<li>" + link("{SITE}/BrandFiles/climb27_key-rules.pdf", "Climb27 key rules (PDF)") + "</li>"
             "<li>" + link("{SITE}/BrandFiles/climbgroup_key-rules.pdf", "ClimbGroup key rules (PDF)") +
             "</li></ul>",
             "<h3>Chapters</h3><ul>"
             "<li>Voice</li><li>Digital user interface</li><li>Motion</li><li>Photography</li><li>Video</li>"
             "<li>Print, merch and signage</li><li>Press and partners</li><li>Email signatures</li></ul>"]),
         ("OneColumn", 1, [
             "<h2>Accessibility</h2><p>Everything meets WCAG 2.2 AA, and AAA where it is small and easy. Every "
             "colour and size has an AAA version, and every text colour pair is tested.</p>"]),
         ("OneColumn", 3, [
             "<h2>Working with press or partners?</h2><p>The press and partners chapter has the boilerplate, logo "
             "rules and contacts.</p><p>" +
             link("{SITE}/SitePages/get-help.aspx", "Contact the marketing team") + "</p>"]),
     ],
     tiles=["voice", "colour-and-type", "photography", "get-help"])

page("get-help", "Get help",
     "Who to ask about artwork, files, partners and press.",
     [
         ("OneColumn", 3, [
             "<h2>Ask early. Ship on brand.</h2>"
             "<p>Send it to us before it goes out and we will check it against the brand.</p>"]),
         ("TwoColumn", 0, [
             "<h2>Brand, artwork and press</h2><p>" + link("mailto:marketing@climb-uk.com",
                                                          "marketing@climb-uk.com") +
             "</p><p>Artwork checks, new files, logo requests and press questions.</p>",
             "<h2>Partnerships</h2><p>" + link("mailto:partnerships@climb-uk.com", "partnerships@climb-uk.com") +
             "</p><p>Partner logos, co-branded pieces and partner packs.</p>"]),
         ("OneColumn", 1, [
             "<h2>When you ask, include</h2><ul>"
             "<li>what you are making and for which brand;</li>"
             "<li>where it will appear and at what size;</li>"
             "<li>the date it needs to go out.</li></ul>"]),
         ("OneColumn", 3, [
             "<h2>Start with the basics</h2><p>Most answers are in the brand rules.</p><p>" +
             link("{SITE}/SitePages/our-brand.aspx", "Read our brand") + "</p>"]),
     ],
     tiles=["our-brand", "templates", "artwork-library", "guidelines"])


def nav_label(slug):
    return PAGES[slug]["title"] if slug != "home" else "Home"
