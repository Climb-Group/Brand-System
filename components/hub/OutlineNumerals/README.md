# Outline numerals

Outline numerals are giant numbers drawn as an orange outline with no fill. They number chapters and sections and carry the odd big stat, like a festival poster.

- `climb-outline-num`: Montserrat ExtraBold (800), upright, tabular figures, letter spacing -0.04em, line height 0.8, no fill and a Climb Orange stroke of about 1% of the size (4px at 380px). `climb-outline-num-sm` is the stat size with a 2px stroke. Never go below a 2px stroke.
- Best on a dark ground or over a photo on a Dark Brown fade. On White or Light Grey the stroke turns to the darker text orange; on Climb Orange it turns White.
- Section numbers are two digits (01 to 10) and decorative: mark them `aria-hidden` and put the real heading in text beside them (`climb-numbered` lines them up).
- A stat number stays readable text with its label underneath in words. With `data-climb-size="aaa"` the stat fills solid.
- Use one size of outline numeral per view. Never outline words or headlines with it; the only outlined words are the quiet marquee.
- `climb-outline-marquee`: a giant italic uppercase line in Orange Tint at 35% with a 2px stroke, running off the edge behind a section. Decorative only, so `aria-hidden`, and never the only place the words appear.
- In design apps: same font, weight and tracking, fill none, stroke Climb Orange centred at about 1% of the point size.
