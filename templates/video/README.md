# Video templates

Motion graphics, title templates, a grade and caption settings for ClimbUK, ClimbGroup and Climb27 films, made to the brand's video and motion guidelines: 3840x2160 at 25fps, things rise into place and never bounce, Montserrat for names and titles, Open Sans for roles and captions.

## What is in it

| Folder | What | Works in |
| --- | --- | --- |
| `_shared/motion/` | Lower third (classic) with sample text and as a plate, six stickers that pop on (Main stage, VIP, ClimbAwards, Live, Find your people, New), a slab wipe transition (16:9 and 9:16), stage-light background loops (16:9 and 9:16, 8 s, seamless) | Any editor |
| `<Brand>/motion/` | Festival lower third with the brand mark (sample and plate), title card, end card with the logo sting (16:9 and 9:16) | Any editor |
| `_shared/stills/`, `<Brand>/stills/` | 4K stills of every graphic (PNG where transparent, JPG where full frame), safe-area and caption guides, the bug (monogram at 60 percent, 160px, top right) | Any editor, design apps |
| `<Brand>/davinci-resolve/` | `<Brand>_Titles.drfx`: editable Fusion titles (Lower Third, Lower Third Festival, Title Card, End Card, Sticker), plus the loose `.setting` files and the logo PNGs the titles load | DaVinci Resolve 18 and later (tested in 21) |
| `<Brand>/premiere-pro/` | `<Brand>_Graphics_4K25.xml`: a 4K 25p sequence with every graphic laid out on tracks, ready to copy from | Premiere Pro (also imports into Resolve and Final Cut Pro) |
| `_shared/luts/` | `Climb_Grade_v1.cube` (33-point 3D LUT, the starting look for every edition; save an edition's tuned copy as `climb27_grade_v1.cube` and so on) and a before and after frame | Premiere Pro (Lumetri), Resolve, Final Cut Pro, most cameras and monitors |
| `_shared/resolve-presets/` | `Climb UHD 25p Rec709 Settings.preset` (project: 3840x2160, 25fps, Rec.709 Gamma 2.4) and render presets: ProRes 4444 with alpha (master), H.264 YouTube 16:9 UHD, H.264 Social 9:16 2160x3840. Import the project preset in Project Settings (the ... menu, Import Preset) and the render presets in the Deliver page (Render Settings, the ... menu, Import Preset). Set the render location after importing. | DaVinci Resolve 18 and later (tested in 21) |
| `_shared/captions/` | An example `.srt` showing the caption rules | Any editor or player |

Formats: transparent clips are QuickTime ProRes 4444 with alpha; full-frame clips are H.264 MP4. Clips with alpha are large, so the `motion/` folders ship as a release download next to this repository rather than in it.

## Install the fonts

Install Montserrat and Open Sans from `../office/_shared/fonts/` before opening any template. Resolve and Premiere list them by family and style (Montserrat Bold, Montserrat Black, Open Sans SemiBold).

## DaVinci Resolve

1. Close Resolve and double-click `Install Climb Titles (Resolve).command`. It installs the three `.drfx` packs, the logo PNGs and the LUT. The `.drfx` on its own is not enough: the Lower Third Festival and End Card load the brand logo from PNG files, and Resolve cannot read images from inside a `.drfx`, so the PNGs go to `Fusion/Templates/Edit/Titles/<Brand>/`.
2. In the Edit page, open Effects, Titles, and scroll to Fusion Titles. The brand's titles are in a folder with the brand name.
3. Drag a title onto a track above your footage. In the Inspector, type the name and role (or the two title lines, or the sticker text). The Lower Third has a Bar width control for long names, and the End Card a Button width control for long web addresses.
4. Titles rise in over their first 18 frames and drop out over their last 10, whatever the clip length, so trim the clip to set the exit. Hold every lower third for at least 4 seconds. Every title has a Colour variant control in the Inspector (Dark Brown, the default, Charcoal or Climb Orange), and colour pickers for the main text.
5. Grade: in the Color page, right-click a node, LUT, and pick `Climb_Grade_v1` after adding the `.cube` to Resolve's LUT folder (Project Settings, Color Management, Open LUT Folder, then Update Lists).
6. Captions: import the `.srt` (File, Import, Subtitle). In the subtitle track's Inspector set Open Sans SemiBold, White, background Dark Brown (#1E0F05) at 70 percent opacity, two lines at most.

The titles are 4K comps; on an HD timeline Resolve scales them to fit.

## Premiere Pro

1. Import `<Brand>_Graphics_4K25.xml` (File, Import). Premiere opens a sequence with every graphic on its own track. When it asks to locate the first clip, point it at the `video` folder of this kit and it relinks the rest.
2. Lower thirds: either drop in the sample clip and replace it, or use the plate (`..._Plate_4K25.mov`) and type over it with the Type tool (Essential Graphics):
   - Classic: name Montserrat Bold 104px White at x 264, y 1694; role Open Sans Regular 60px Light Grey (#E9E9E9) at x 266, y 1824 (positions are the top left of the text on a 3840x2160 frame).
   - Festival: name Montserrat Black 132px White, uppercase, two lines from x 282, y 1490; role Open Sans SemiBold Italic 58px Orange Tint (#F2AE86) at x 284, y 1840.
   Save each as a Text Style in Essential Graphics so the team reuses it.
3. Stickers and the slab wipe sit on a track above the cut. Cut between shots at frame 12 of the wipe, when the slab covers the frame.
4. Grade: Lumetri Color, Creative, Look, Browse, and pick `Climb_Grade_v1.cube`. Use it after Basic Correction (exposure and white balance).
5. Captions: import the `.srt`, then in the Essential Graphics panel set Open Sans SemiBold, White, background Dark Brown at 70 percent, and save it as a caption style.

## Rules that travel with the files

- Open with a moment, not the logo. The end card and sting go last: 3 seconds of sting, then the card.
- Title safe is 5 percent of the frame (192px at 4K); every graphic here sits inside it.
- One sticker per scene.
- Captions always on for social, 42 characters a line, two lines at most; never caption words the speaker did not say.
- No exclamation marks or emojis on screen, even when the speaker is excited.
- Never upscale: if a shot only exists below 4K, use it small or not at all.

## Accessibility

White on the lower third bar (Dark Brown at 85 percent) stays above 12:1 over any footage, even pure white; Orange Tint on Dark Brown is 9.93:1; White on Climb Orange is used only for large stickers and buttons (3.08:1, the large-text level). Captions follow WCAG 2.2 and the brand's audio rules (speech 20 dB above music, a dialogue-only mix, a transcript for every film).

## Not included, and why

- Premiere Motion Graphics templates (`.mogrt`) can only be exported from After Effects or Premiere itself. The plates, the text positions above and the sequence give the same result; a `.mogrt` set can be exported once from that sequence and added here.
- The DaVinci titles were generated and then tested in DaVinci Resolve 21 (type sizes checked against the stills). The Premiere sequence was generated, not authored in the app: open it once and check it against the stills before sharing it widely.

## Rebuild

Everything here is generated from the brand tokens, logos and motif recipes. See `../_build/README.md`.
