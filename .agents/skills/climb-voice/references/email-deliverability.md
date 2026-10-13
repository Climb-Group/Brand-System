# Email deliverability

What spam and inbox-placement tests flag in ClimbUK emails, and what to do about it. This is a living list: after
every spam test (or a send that lands in spam), add what it flagged and what we decided.

Two kinds of email follow different rules here:

- **Single-message emails** (a ticket release, a partner invitation, an event reminder): one message, one button
  (see `channels.md`). Follow every rule below.
- **Newsletters**: many stories from many senders, so some flags cannot be avoided without breaking the format. The
  "Newsletters" line under each rule says what to do instead.

## Words spam filters weigh

Words and phrases spam tests have flagged in our emails. One on its own rarely matters; several close together, in
the subject line or in capitals, add up. Prefer the alternative where it reads as well. Never change a partner's
offer code or the name of their offer.

| Flagged | Prefer | Note |
|---|---|---|
| free | at no cost, no charge, included | Keep "free" when it is the offer itself, but not in the subject line and never in capitals ("FREE"). |
| get | book, claim, find, join | Button labels such as "Get your ticket" are fine; avoid stacking several in one email. |
| order | booking, purchase | |
| unsubscribe | (required) | Every marketing email needs it. Keep it in the footer, in plain small text. |
| win | take home, be chosen for | Competitions and prizes: say what the prize is. |
| access | use, get into, entry | |
| email marketing, marketing | (avoid in body copy) | Fine in a job title or a team address. |
| offer | discount, partner price, deal | |
| 50% off (any "% off") | half price, save half | Keep the partner's exact discount wording in the post; in the email say it once. |
| problem | challenge, question | |
| hidden | (avoid) | |
| score | rating, result, benchmark | Keep it in product names (the ClimbUK Growth Score). |

**Newsletters:** partner copy is published as supplied, so some of these words stay. Keep them out of the subject
line and the preview text, and do not repeat an offer in capitals or in more than one place per story.

## Links

Spam tests count every link (45 links in the October 2026 newsletter was "way too many"). Fewer links read as less
like a link farm.

- Single-message emails: aim for 10 links or fewer, including the footer.
- **Newsletters:** aim for 25 or fewer. One link per story (the button), the story's image not linked, no "read the
  full story" line as well as the button, footer links kept to unsubscribe, the website and one social row.
- Never use URL shorteners. Keep partners' tracked links as supplied.

## HTML weight and complexity

Spam tests prefer light, simple HTML. Gmail also cuts any email whose HTML is over 102 KB behind "View entire
message", which hides the unsubscribe link.

- Keep the HTML under 50 KB (newsletters under 75 KB), with inline styles and one table layout. No pasted
  word-processor markup, no nested tables deeper than the layout needs.
- **Newsletters:** the October 2026 newsletter was 33 KB for nine stories, which is a good ceiling. Fewer stories
  beats a heavier email.

## Images

Spam tests prefer a low share of image content. An email that is mostly images, or has words only inside images,
reads as spam and is unreadable with images off.

- Every word that matters is live text; images carry no essential words. Every image has alt text.
- Single-message emails: one image (a header or one hero) is plenty.
- **Newsletters:** one image per story at most; consider images on the first three stories only and text for the
  rest. Images are hosted on climb-uk.com, never attached, and compressed (JPEG, about 40 KB each at 1072px; not
  WebP, which Outlook for Windows cannot show).

## Tracking

Spam tests count tracking pixels and prefer a tracking domain of our own.

- Use one tracker, not two. If the mailing platform tracks opens and clicks, switch off open and click tracking in
  the sending service, so the email carries one pixel and each link one redirect (two layers of redirects also look
  suspicious to filters).
- Whichever service tracks, its links and pixel must use a ClimbUK domain (a branded link subdomain of
  climb-uk.com), not the service's own domain.

## Before every send

1. Run the copy checker, then read the subject and preview text against the word list above.
2. Count links and images and check the HTML size against the limits above.
3. Send a test to a Gmail and an Outlook inbox, and run a spam test. Add anything new it flags to this file.
