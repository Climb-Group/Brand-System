# Elements

How each motif is built so every app and every agent draws it the same way. Master artwork lives in the brand pack (`logos/`, `illustrations/`, `templates/`); this file is the recipe.

## Grid and scale

- Base unit: 8px on screen, 4mm in print. Margins are multiples of it.
- Motif stroke weight: 2 units on screen at 1920 wide (16px), scaled with the canvas. Never thinner than 1px on screen or 0.5pt in print.
- Motif colour: Climb Orange for the one marker; otherwise a tone of the ground: White at 8, 12 or 16 percent on dark grounds, Dark Brown at 6 or 10 percent on light grounds.

## The Ascent

- Steps: a run of 3 to 5 right-angled steps rising left to right, each step 1 unit tall and 2 units long, square ends.
- Chevrons: stacked upward chevrons at 60 degrees, 1 unit apart. Use 3 for a mark, 5 to 9 for a divider band.
- Use for dividers, corners, progress indicators, wayfinding arrows.

## Contours

- 6 to 14 closed, organic contour rings, evenly spaced (2 units), drawn as unfilled strokes, offset from the centre so they run off the edge of the canvas.
- One ring may be Climb Orange: that is the marker. All others are a ground tone.
- Use for wide fields: wallpapers, call backgrounds, merch backs, walls.

## Stage Light

- 2 or 3 soft-edged beams from a point off the top edge, fanning down at 15 to 35 degrees, Climb Orange to transparent, plus an Orange Tint glow at the source.
- Add fine grain (2 to 4 percent noise) so gradients do not band on screens and in print.
- Use for heroes, stage screens, video, Main Stage Moments.

## Connections

- 12 to 40 dots (1.5 units across) joined by hairlines (0.25 units), mostly ground tone, with one Climb Orange cluster of 3 joined dots as the marker.
- Use for Find Your People, networking, partner and audience pieces.

## Highlight bar

- A solid Climb Orange rectangle behind one word or phrase, padded 0.25em left and right, height 0.9 of the cap height plus descender, sitting on the baseline.
- Text on the bar is White only at large sizes (19px bold or 24px and up), otherwise Dark Brown.
- On the website this is `[[word]]` in page content.

## Outline numerals

- Montserrat ExtraBold (800), upright, tabular figures, letter spacing -0.04em, line height 0.8.
- Fill none, stroke Climb Orange centred, about 1% of the type size: 4px at 380px, 2px at stat sizes, never thinner.
- Section numbers at 280 to 380px, two digits (01 to 10), set beside or behind the heading; stats at 64 to 120px with a label in words underneath.
- On White or Light Grey the stroke is the darker text orange; on Climb Orange it is White.
- The quiet marquee: italic uppercase at about 92px, Orange Tint at 35% with a 2px stroke, running off the edge.
- Web: `color: transparent; -webkit-text-stroke: 4px var(--climb-orange);`

## Photography treatment

- Prefer warm, high-contrast frames. On dark layouts, darken the photo 25 to 50 percent, never with an orange wash over faces.
- Duotone (Dark Brown to Climb Orange) only for texture and backgrounds, never for portraits.
- Crop tight on faces and hands in conversation for Find Your People; wide with crowd and light for Main Stage Moments.
