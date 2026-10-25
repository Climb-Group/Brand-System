---
name: climb-voice
description: 'The ClimbUK, ClimbGroup and Climb27 brand voice and copy rules. Load it whenever you write or edit any words a customer, partner, attendee or the public will read for ClimbUK, ClimbGroup or a Climb edition (Climb27 and later): web pages, snippets, emails, social posts, ads, captions, scripts, slides, press releases, signage, merch lines, or alt text. Also load it to review or "make on-brand" copy someone else wrote, and whenever you publish or upload any text to the website (blog posts, news, newsletters, partner or client supplied text) even when it goes up word for word, so the glossary stays complete. Includes a copy checker script.'
license: Proprietary
metadata:
  owner: ClimbGroup marketing
  sources: ClimbUK voice guide, Climb27 marketing brief, the sales and partner review of the website (October 2026), the reviews of the Climb27 flyers (October 2026), the decision to keep every piece's words in an editable copy file (October 2026), the decision to keep team-only material in an internal folder that is never published (October 2026), the review of past testimonials (October 2026), the three reviews of the Climb27 sales brochures (October 2026) and the review of the partners web page (October 2026)
  version: "1.11"
---

# ClimbUK voice

ClimbUK is **business with a party, not a party for business**: a festival-energy event brand for growing companies, the people who fund them and the firms that help them. The ambition for Climb27 is to be the UK's answer to Slush. The copy has the energy of a headline act and the discipline of a good adviser: every line is exciting **and** useful.

## The voice in four lines

1. **Headline energy.** Write like it belongs on a billboard, a keynote slide or a festival poster. Short, rhythmic, confident.
2. **Doing, not dreaming.** Move the reader from inspiration to action: "learn how to grow your business", never "hear stories about growth". Name the outcome and the next step.
3. **Curated, not crowded.** Sell the right people in the room, quality of conversations, close and personal. Never sell size.
4. **Personal, not generic.** Every piece is written for one audience (see `references/audiences.md`). If it could be about any event, rewrite it.

## Hard rules (the checker enforces these)

- **No emojis, no exclamation marks, no em or en dashes.** ASCII hyphen-minus only. Let design and imagery carry the energy.
- **Never "Climb" on its own.** Write ClimbUK (the brand on the poster), ClimbGroup (the company name, for legal lines and corporate pieces; never explain how it relates to ClimbUK in copy), or the edition: Climb27, Climb26. The app is the "ClimbGroup Event App". The Investor Ladder Ltd appears only in legal and invoice text.
- **Venue embargo.** Until ClimbUK announces it, public copy names no venue, city area, venue type or size, and does not hint ("somewhere new" and the word "venue" are both banned). After the announcement, use the line in the announcement brief. The checker takes `--announced` to switch, and loads the names it must catch from a private rules file (see the script).
- **No internal numbers.** No attendance targets, no "thousands", no audience size, no partner counts, no booking percentages. Past edition figures appear only as ClimbUK publishes them. Channel reach is the exception: partner materials may show the reach of ClimbUK's own channels (newsletter readers, monthly website and social views) and the share of attendees who follow up after meeting a partner, taken from the source data and written as a floor with a plus ("40k+ monthly newsletter readers"). Never an attendance figure, an audience size for the event or a promised number of meetings.
- **No promises we cannot keep.** No guarantees. Never promise a number of investor meetings, introductions or funding. Saying investors come looking for deal flow is fine ("Find investors looking for real deal flow", "Investors here to find their next deal"). Use "find", not "meet", so nothing reads as a promised meeting; promising they will meet or back the reader is not. Partners are sold "meetings with the right people", never a number of meetings or an audience size for the event.
- **Say who the right people are.** When a page sells "the right people", explain what makes them right for the reader (a reason to talk, a need for what they do, a door they can open), in our words. Do not repeat a list of segments a page has already given.
- **Scarcity only when it is true.** Ticket releases really do close, so say so: name the release, its price and its state ("Open now", "Next", "Final"), and that the price goes up when the release is gone. Never invent scarcity: no "sold out", "last few" or "selling fast" unless the shop says so, and no "premier", unsupported superlatives or trademark symbols. Do not quote the share of tickets in a release ("about 5% of tickets").
- **No hedges, no defensive wording.** No "TBC", "coming soon", "subject to", "we hope", "we never", "we do not promise". State what happens.
- **No reports we have not agreed.** Never promise partners or sponsors an impact report, a post-event report or audience data. Sell what happens in the room.
- **Real people only.** Testimonials and quotes are real and consented. Never invent a quote, a name or a company.
- **Testimonials without the date.** When a past quote goes into marketing, credit the person and organisation only: no edition, year or "Climb24 speaker" line. Pick quotes whose own words do not name an old edition ("#Climb24", "Climb 2025 next year"); a dated quote makes the festival look old.
- **Testimonials name a person.** Credit every quote to a named person, their role and their organisation ("Rachel Kelly, Partnership Manager, Caspian Insurance"). A quote credited only to a company, or carrying a role line such as "Climb26 exhibitor", is left out. The guest's words are printed exactly as they said them; the voice rules apply to our words, not theirs. To shorten, use whole sentences rather than editing them. A set of quotes on a page shows three; borrow a quote from a nearby audience to make three rather than show one or two.
- **Paying in instalments.** Name the providers (Klarna, PayPal Pay Later, Afterpay) and say the fee plainly: "A 5% financing fee is added to your total order." Prices say "ex. VAT".
- **Stand names.** The smallest stand is the "Startup pod", never "starter pod".
- **Other events.** Being named alongside other events is fine when it helps both sides. Never copy their formats, and never compare ClimbUK with another event in public copy.
- **Whitelabel.** No vendor or platform names (Canva, Cvent, Stripe and the like) unless the reader must recognise the integration.

## Clear for everyone (WCAG 2.2 AAA copy rules)

These come from the brand's WCAG 2.2 AAA review (codes in brackets). The public version is the "Clear for everyone" section of `guidelines/voice.md`.

- **Links say where they go (E13).** Link text names the destination or action ("See the Climb27 lineup", "Read the partner terms"). Banned as link text: "click here", "read more", "learn more", "find out more", "more info", and a bare "here", "this" or "link". The checker fails on these (a phrase in double quotes is treated as a quoted example and skipped). A link that opens a new tab says so in its text or accessible name (C8).
- **Buttons say what they do.** Button text is the action: "Get your ticket", "Book now", "Book a call". Never "call to action", "the main button" or "CTA" as button text, and never "Buy now". The checker fails on these as button or link labels.
- **Abbreviations in full on first use per page (E15).** "small and medium-sized businesses (SMEs)", then "SMEs". Allowed without spelling out: UK, CPD, AI, VIP, SME(s), QR, DJ, CEO, PR, AV, B2B, FAQ, OK, TV, PDF, URL, WCAG, AA, AAA. The checker prints a hint for any other all-caps token of 2 to 5 letters that is not spelled out in brackets on its first use.
- **Plain language (B4).** Aim for Flesch-Kincaid grade 9 or lower: short sentences, everyday words, one idea per sentence. Any long page (partner, press, investor) opens with a two-line summary of what it offers and what to do next. The checker prints the grade for every input and a hint above grade 9 once the body copy runs past 80 words.
- **Unusual words link to the glossary (C5).** The first time a page uses jargon a newcomer may not know (scale-up, exhibitor tiers, deal flow, release ladder), link it to the glossary at `/glossary` on climb-uk.com (each term has its own anchor, for example `/glossary#term-scale-up`), or explain it in a few words in the sentence. If the word is not in the glossary yet, add it there rather than leaving it unexplained.
- **Keep the glossary up to date, whatever the source (C5).** This applies to every piece of text that goes on the website, including blog posts, news, newsletters and text a client, partner or speaker supplied that is published word for word without applying this voice. Before it goes live, list the terms a newcomer may not know (industry jargon, funding and investment terms, programme and scheme names, abbreviations). For each one missing from `/glossary`, add an entry: the term, then one or two plain sentences in this voice, alphabetical under its letter, with an anchor `term-<slug>`. In the website repository the entries live in `climb_website_brand/views/pages/glossary.xml`. The page is set to not update, so on a running site also edit the page itself. Supplied text keeps its wording, but its first use of each term may still link to the glossary.

## Words we use, and words we do not

From the sales and partner review of the Climb27 pages (October 2026). The checker flags the banned side of each pair.

| Write | Not | Why |
| --- | --- | --- |
| agenda | programme (for the event schedule) | It is what buyers search for. "Programme" stays for real programmes: the Affiliate Programme, accelerator programmes. |
| Affiliate Programme (people in it are affiliates) | referral scheme, referrals | That is its name, so it takes capitals. |
| public sector | councils, government and councils | Covers councils, combined authorities and agencies in one phrase. |
| Partner Manager | partner manager | It is a job title. Capitalise job titles. |
| connect you with, bring you | introduce you to, matched | We put the right people in the same place; we do not promise a personal introduction or an algorithm's match. |
| fractional (leaders who take responsibility for a function) | consultant, for the same people | Fractional leaders dislike "consultant". Consultants give advice; fractional leaders take responsibility. They are separate audiences. |
| advisers (the advice) and professional services firms (who implement it) | one blurred group | Keep the two roles clear. |
| fellow founders, peers who are one step ahead | other founders | They have been through what the reader is going through. "Learned the expensive way" is fine with this framing. |
| investors, advisers, fellow founders, partners | buyers, as the reason scaling companies come | We cannot show buyers in the room yet. Name the people we can show. |
| find investors looking for real deal flow, investors here to find their next deal | meet investors, investors ready to invest, chequebooks, a seat on the stage, investors who came to meet you | "Find" keeps it from reading as a promised meeting. |
| why the team should come | can I bring the team? | Lead with the benefit, then the team offer. |
| the community, people referring each other | a crowd, an audience | ClimbUK is a community that shares experience and sends each other work. |

Sectors (Health, Creative) cut across the audiences: write for the audience, with the sector's people and examples. Creative UK can be named publicly as the ClimbCreative partner; check before naming any other sector partner.

Phrases to drop: "with your eyes open", "in their patch" or "in your patch", "and a budget to solve it", "at least three", "unmatched". A heading always carries a benefit: "Why Climb27?" says nothing on its own, "New clients, from the businesses you want to serve" does.

## Headlines and titles

From the review of the Climb27 flyers (October 2026). They apply to every headline, title and list heading, and most of all to flyers, banners, posters and social cards, which a stranger reads first.

- **Open positive.** The first line says what ClimbUK is, never what it is not. "The Festival for Business Growth." works; "Not a conference. A festival for business growth." does not. The checker fails "not a conference" and its cousins. "Business with a party, not a party for business" describes the voice; it is never an opening line.
- **Name the benefit, not the slot.** A title says what the reader gets: "Connections that lead to work", not "New partners"; "Roundtables and workshops", not "Time to talk". If a point is not a reason to come, drop it rather than give it a title: booking meetings in the app ("Plan your days") is not worth a place on a flyer.
- **Advice from one step ahead.** When the point is peers, frame them as people a step further on who share what worked: "Advice from one step ahead", never "Founders at your stage".
- **The investor side is part of the offer, not the headline of it.** The investor side can be mentioned, but it is never the main point of a message. "The Investor Ladder" is not a title on its own: lead with what the reader gets ("Funding that fits", "Your next step").
- **The whole funding journey.** ClimbUK supports businesses through the whole funding journey. Never cap it: no "up to Series A", no "first cheque to Series A". Say "the whole funding journey" or "any stage of your funding journey". The checker fails "to Series A".
- **Music is not a feature.** Only the grand opening has live music. Do not list live music or DJ sets as a reason to come; the big moments are the announcements, the ClimbAwards and the stories behind growing businesses. The checker prints a hint for "live music" and "DJ set".
- **One orange word and one italic word** on designed pieces, and the headline still reads as a sentence without them.

## Answer the question

- **Every claim gets its answer on the same page.** If a line makes the reader ask something ("two days", a price, who they will meet, what happens after), the same page answers it.
- **Answer first.** An FAQ answer opens with the answer, in one sentence, then the reason. "When is the agenda published?" starts with the timing (the agenda goes live a few weeks before the event), not with why agendas are hard.
- **Write questions from the buyer's side.** People reading the page have not bought yet: "I want a one-day ticket. Which day should I pick?", not "I bought a one-day ticket".
- **Say when something happens in the app.** "Book meetings in the ClimbGroup Event App before you arrive", "Your contacts stay in the app after the festival".
- **Be specific about who is in the room.** Name the kinds of people and what they bring, for this audience. A list that would fit any event is too generic.
- **Prices people remember.** Round, steady steps: £250, not £252. Each release step should feel like a sensible jump.
- **End every page well.** The last section and the footer are a real closing line in the voice with one next step, not a leftover label. Partner calls to action say what they are for: "Interested in partnering? Book a call with the team."

## Where the name comes from

"Climb" comes from the Investor Ladder. A business climbs the ladder to reach the next rung, an investor who fits where it is now, and investors pass businesses up and down the ladder to the rung that suits what they need. Use this story when someone asks about the name, in an about page, a press line or an opening from the stage. It is never a heading or the main point of a piece (see Headlines and titles).

ClimbUK is a business event, never a sport-climbing or outdoors event. People do mistake it for one, so:

- "Climb" and "climbing" are fine when the business meaning is clear in the same line: climbing the Investor Ladder, the next rung for your business.
- Never use climbing-sport words or images: ropes, walls, harnesses, belays, outdoor gear, "climbers" for attendees, or a photo or icon of rock or wall climbing.
- When a piece leads on "climb" with nothing around it, add the business words: growth, investors, the next stage.

## Words and lines we own

- Company tagline: **The Festival for Business Growth.** "The Festival of Business Growth" is the established spoken form and is also correct; use one form per piece.
  In a sentence it is a description, so it is lower case: "Climb27 is the festival for business growth." Capitals only when the tagline stands on its own.
- Web addresses on print and PDFs are written in full with www: **www.climb-uk.com/partnerships**, never "climb-uk.com/partnerships". Email addresses stay as they are.
- Describe a zone or a format by what people do there (mentoring, meeting, discussing, pitching), not by its furniture or how many there are: write "Advisers and fractional leaders mentoring founders and talking through what comes next", never "Advisers and fractional leaders, in 24 pods".
- Subheadings and straplines say something concrete: who it is for or what they get. Never a pair of clever opposites that could describe anything ("Small by design. Powerful by intent.", "Big enough to be seen. Sharp enough to close.").
- Climb27 working headline: **Your business. Bigger stage.**
- General Climb27 flyer (the piece for readers who do not know ClimbUK yet): **Bring your ambition. Find your people. Accelerate your growth.**
- Climb27 themes: **Find Your People** (networking is the reason to come) and **Main Stage Moments** (short, big moments: the grand opening, announcements, the ClimbAwards, our own formats). Big moments, not keynotes.
- Earlier tagline, retired from new work: "where momentum meets opportunity".

## Public brand documents

The brand book, guidelines, one-page rules, press and partner packs are public. Write them for anyone who builds with the brand (UI and motion engineers, videographers, animators, press, partners, printers): guiding, not over-restrictive. No repository or folder paths, no internal tool or vendor names (except install notes for a module), no internal notes or decisions in progress.

## Team-only material

Some work is for the team only: testimonial analysis, audience research, sales notes, people's details, anything about an unannounced venue. It goes in the pack's `internal/` folder, which is never committed or published and reaches only the team's computers and the team's brand centre library. Never put it in a public folder, a copy file, a skill or a public document, and never quote it in public copy without checking that the words are already public. Read `internal/README.md` for what goes there.

## Channels and handles

Social: LinkedIn, Instagram, TikTok, X and Bluesky, all as `climbuk`. In email signatures the socials are icon buttons, not text links.

## How to write a piece

1. Pick the audience and channel. Read that audience's row in `references/audiences.md`.
2. Write the headline first: 3 to 8 words, one idea, ideally a two-beat or three-beat rhythm ("Iconic speakers. Real advice. No fluff."). On the website, wrap the one word to highlight in orange as `[[word]]`.
3. Write the body as short, complete paragraphs, each a mini pitch: what happens, why it matters to this reader, what to do next. Strong verbs, varied sentence length, no filler.
4. End with one clear call to action that names the action ("Get your ticket", "Book your meetings", "Apply to pitch").
5. Run the checker, then re-read once against the four voice lines.

Shapes for each channel (lengths, structure, CTA style) are in `references/channels.md`. Good and bad examples, including rewrites, are in `references/examples.md`. For email, also read `references/email-deliverability.md`: words spam filters weigh, link, image and HTML limits, tracking, and what newsletters may relax. Add whatever a spam test flags to it.

## Copy files

Every piece the pack builds keeps all its words in a Markdown copy file beside its build, `<name>.copy.md`, so people can review and edit the words without touching the design, and the build reads it. Design sections are marked `<!-- @front.headline -->` on their own line, with design settings after the name (`<!-- @back.reason icon=people -->`) and reviewer notes as `<!-- note: ... -->`. When you write or change words for a built piece, change its copy file, never the build script; when you make a new piece, write its copy file first. The standard, with a full example, is in `references/copy-files.md`; `scripts/copy_md.py` reads the files.

## Check your copy

```bash
python3 .agents/skills/climb-voice/scripts/check_copy.py path/to/copy.txt            # before the venue announcement
python3 .agents/skills/climb-voice/scripts/check_copy.py --announced path/to/copy.txt # after it
echo "Your text" | python3 .agents/skills/climb-voice/scripts/check_copy.py -
python3 .agents/skills/climb-voice/scripts/check_copy.py pdf/flyers/copy/segments/investors.copy.md  # a copy file: markers, then words
```

It prints each problem with the rule it breaks and exits 1 when anything fails, including vague link text. After the problems it prints, per input, a reading level (Flesch-Kincaid grade, a rough estimate) and "hint" lines for abbreviations to spell out; hints never change the exit code. Add `--no-hints` for hard rules only. It does not judge tone: that is your job, against the four lines above. The website pages have a stricter, page-aware linter in the website repository (`docs/climb27-for-pages/deploy/lint_copy.py`); keep the two ban lists in step when either changes.

## Before you finish

- The checker passes, and you have acted on its reading level and abbreviation hints.
- The words of a built piece are in its copy file, and none are typed in its build script.
- Every link says where it goes, and unusual words link to the glossary.
- Any new term in this piece, or in supplied text going up as-is, has a glossary entry.
- The piece names one audience and gives them one reason and one next step.
- Nothing in it would still be true of any other event.
- If you used a fact (date, price, format, speaker), it came from the brief, the website or the person who asked, not from memory.
- Any brand preference or decision a person gave you while you worked is now in this skill, its guideline and, where it can be checked, the copy checker (see "The pack learns as it goes" in the brand pack's AGENTS.md). Do not leave it only in a chat or a memory.
