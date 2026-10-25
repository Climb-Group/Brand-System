# Motion

For motion designers, front-end engineers and animators. Motion is a **festival crowd, not a slideshow**: things rise into place like someone stepping up onto a stage, cards spring when you touch them, logos and names drift past like a crowd, and stickers look slapped on. Punchy and quick, with one joyful overshoot on touch. The reference is the Climb27 homepage at climb-uk.com.

## Principles

1. **Rise, then settle.** Entrances travel upward and decelerate (`motion-easing-rise`). Exits accelerate away and are shorter.
2. **One thing leads.** In any moment, one element moves with intent; everything else is still or follows in a short stagger.
3. **Light and crowds move, type holds.** Stage light, glows, marquees and contours can drift. Headlines arrive once and then stay put.
4. **Touch gets a spring.** Hovering a card, photo tile or sticker lifts it with `motion-easing-spring`, a small overshoot that feels alive. Page-level movement never overshoots.
5. **Motion has a job.** Show where something came from, confirm an action, or direct the eye. If it does none of these, cut it.
6. **Always optional.** Everything has a reduced-motion version (below).

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| `motion-duration-instant` | 100ms | Hover and press colour |
| `motion-duration-quick` | 160ms | Buttons, toggles, tooltips, focus rings |
| `motion-duration-base` | 240ms | Card lift, menus, accordions |
| `motion-duration-slow` | 400ms | Panels, modals, scroll reveals |
| `motion-duration-stage` | 700ms | Hero entrances, video title cards, logo reveals. Ceiling for the web |
| `motion-easing-rise` | cubic-bezier(0.16, 1, 0.3, 1) | Anything entering |
| `motion-easing-spring` | cubic-bezier(0.34, 1.56, 0.64, 1) | Hover lift on cards, photo tiles and stickers, at `slow` duration |
| `motion-easing-standard` | cubic-bezier(0.2, 0, 0, 1) | Moving or changing in place |
| `motion-easing-exit` | cubic-bezier(0.4, 0, 1, 1) | Anything leaving, at about two thirds of the entrance time |
| `motion-easing-linear` | linear | Progress, marquees, stage-light drift |
| `motion-distance-lift` | 4px | Hover raise |
| `motion-distance-rise` | 16px | Scroll reveal travel |
| `motion-distance-rise-large` | 48px | Hero lines, video titles |
| `motion-stagger` | 60ms | Between siblings, at most 6 in a sequence |

## Transforms

- Use `transform` and `opacity` only, so motion stays on the compositor. Never animate width, height, top or left.
- Allowed: `translateY` (the rise), `translateX` for carousels and marquees, `scale` between 0.98 and 1.04, and `clip-path` wipes that reveal upward.
- Rotation: stickers sit at -3 to -4 degrees and may tip to +2 degrees on hover; a card may tilt 0.4 degrees as it lifts; the Ascent chevron turns 90 degrees to point. Nothing spins.
- Photos inside cards may scale to 1.06 on hover (the card clips them).
- No 3D flips, no skew, no bounce on entrances, no parallax deeper than 20% of scroll speed.

## Web recipes

Reference CSS for the ClimbUK web components, using the brand tokens. Copy the values, not just the look.

```css
/* Scroll rise: content slides up as it enters, driven by scroll where supported. No fade from 0: a
   full-page screenshot or link preview captures items before they scroll in, and they would show blank. */
@supports (animation-timeline: view()) {
  .climb-rise { animation: climb-rise linear both; animation-timeline: view(); animation-range: entry 0% entry 35%; }
}
@keyframes climb-rise { from { transform: translateY(var(--climb-motion-distance-rise)); } }

/* Card lift with a spring */
.climb-moment { transition: transform var(--climb-motion-duration-slow) var(--climb-motion-easing-spring),
                            box-shadow var(--climb-motion-duration-base) var(--climb-motion-easing-rise); }
.climb-moment:hover { transform: translateY(-6px) rotate(-0.4deg); box-shadow: var(--climb-shadow-4); }
.climb-moment:hover > img { transform: scale(1.05); }

/* Primary button: orange glow, darker and higher on hover */
.btn-primary { box-shadow: 0 8px 24px rgba(232, 113, 42, 0.35); }
.btn-primary:hover { background: var(--climb-color-orange-text); transform: translateY(-2px); }

/* Marquee: a seamless loop of two copies of the same row */
@keyframes climb-marquee { to { transform: translateX(-100%); } }

/* Live dot: an orange ring pulses three times, then rests */
@keyframes climb-pulse { from { box-shadow: 0 0 0 0 rgba(232, 113, 42, 0.6); } to { box-shadow: 0 0 0 1em rgba(232, 113, 42, 0); } }
```

- Entrance: rise from below as the element enters the screen (from the right for a ticket card beside a headline). Duration 0.4s to 0.7s, and delay steps of 0.06s across a row of cards. Use the page tool's own entrance animation where it has one. A scroll-driven entrance never starts invisible: slide only, so cards and quotes are never blank in a screenshot, a print or a link preview.
- Hero sequence: eyebrow, display line, lead, buttons, each rising at `stage` duration, staggered by `motion-stagger`. Total under 1 second.
- Marquees (logo walls, speaker names) are linear and slow: 40 to 60px per second, which is 60 to 160 seconds per loop on a long row. Alternate rows run in opposite directions so it reads as a crowd. They pause on hover and focus.
- Loading: a thin Climb Orange progress bar or three Ascent chevrons pulsing in sequence. No spinners.

## Reduced motion

Under `prefers-reduced-motion: reduce`: no translation, scale, spring, parallax, marquee, pulse or auto-play (marquee rows simply wrap). Replace entrances with a fade at `motion-duration-quick`. Video stays paused until played. Nothing flashes more than three times a second, ever (WCAG 2.3.1).

## Motion graphics and animation

- **Logo reveal (sting):** the li mark rises into place (`rise-large`, `stage`), the wordmark wipes in upward behind it, then one Climb Orange contour ring draws around it. 3 seconds; 5 seconds with the tagline. Ends on the static master.
- **Kinetic type:** one line at a time, Montserrat Black, each word rising with a 60ms stagger, held at least 1.5 seconds per line (long enough to read twice). The orange word turns orange, or the highlight bar wipes in under it, after the line lands.
- **Backgrounds:** Contours drift (0.5% scale breathing over 8 seconds), Stage Light beams sweep slowly (10 to 20 seconds per pass), Connections draw line by line. Always loopable and seamless.
- **Transitions between scenes:** a hard cut, an upward wipe, or an Ascent chevron wipe. No cross-dissolves longer than 8 frames, no spins, no flashy presets.
- Hand-off: open motion design project files at 3840x2160 (or the screen's native size, whichever is larger), 25fps for UK broadcast or 30fps for social, plus Lottie for web (under 150KB, no raster images inside).
