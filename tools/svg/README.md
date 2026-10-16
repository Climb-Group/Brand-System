# Layered SVG export

Turns a print build's laid-out page into a layered SVG that people edit in Inkscape or Affinity, beside the PDF the build already makes.

- `layered_svg.js` runs in the page after fonts load and text is fitted. `layeredSVG(title)` returns the SVG text. Groups come from `data-layer="back/reasons/reason-1/title"` on each element, names from `data-label`, and the copy file section from `data-copy`. The top level groups become Inkscape layers.
- `layered_svg.py` finishes it: `finish(raw, out, pack)` links each `<img data-photo='{"photo", "size", "crop", "fade"}'>` photo from the pack with its crop as a clip and its fades as gradients, embeds every other image at up to 1600px, and writes the file.

The flyer builds use both through `write_svgs(jobs, pack)` in `pdf/flyers/_build/build.py`; a job with `svg`, `svg_js` and `svg_out` gets an SVG. The rules for grouping are in the climb-visual-style skill, "Editable sources".
