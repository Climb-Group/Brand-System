# Filming and photo release

A two-page A4 form for people we film or photograph for ClimbUK social media and marketing, at events we attend, events our partners run and our own events. It is the separate release that clause 12.2 of the ClimbUK Terms and Conditions (climb-uk.com/terms, version 2026-10) refers to.

It collects:

- full name and email (required), phone number and the event or place (optional)
- social handles to tag: LinkedIn, Instagram, Facebook, TikTok and X (optional), with a tick box to allow tagging
- three optional choices: the ClimbUK newsletter, an invite to the Affiliate Programme, and a copy of the edited video
- a signature, printed name and date, with a second signature for a parent or guardian when the person is under 18

## Files

| File | What it is |
| --- | --- |
| `ClimbUK_filming-and-photo-release.pdf` | The form with a free copy of the edited video. |
| `ClimbUK_filming-and-photo-release_paid-video.pdf` | The same form where the edited video is sold. The person filming writes the price in pounds on page 1, and the video is sent once the invoice is paid. |
| `release-text.md` | Every word on both versions, for review and for setting the form up in an e-signature tool. |
| `release_copy.py` | The words. Change them here. |
| `build.py` | Builds both PDFs and `release-text.md`. |

Both PDFs are fillable on screen and print cleanly for a pen signature. The signature boxes are signature fields; to collect signatures through an e-signature tool, upload the PDF as a template and place the tool's own fields over the printed boxes, so the signed copy is emailed to the signer.

## Rebuild

```bash
python3 -m pip install reportlab pypdf
python3 templates/forms/filming-release/build.py
python3 templates/forms/filming-release/build.py --paid
python3 .agents/skills/climb-voice/scripts/check_copy.py --no-hints templates/forms/filming-release/release-text.md
```

`--brand-pack PATH` points the build at another checkout of the brand pack; it defaults to this one.

## Brand

- Colours from `tokens/brand.tokens.json`: the White preset for the form, a Dark Brown header, the brand orange for the rule and the Ascent chevrons, Orange Text for small orange numbers.
- Montserrat for headings and Open Sans for body text, from `fonts/ttf/`.
- The ClimbUK reversed logo from `logos/ClimbUK/PNG/`.
- Words follow the `climb-voice` skill and pass its copy checker; layout follows `climb-visual-style`.
- Accessibility: text pairs meet WCAG 2.2 AA, every field has a label and a tooltip, the document has a title and its language is set to en-GB.
