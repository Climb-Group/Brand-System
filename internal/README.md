# Internal

Team-only material for the ClimbUK brand: research, testimonial analysis, sales notes and anything that names people or an unannounced venue.

Git ignores everything in this folder except this README, so none of it is ever committed or published. The team's computers keep the folder and copy it into the team's brand centre library with the rest of the pack. A fresh clone has only this README: get the files from the team's brand centre library.

## What goes here

- Analysis and research the public should not see, such as the testimonial map of who was there.
- Working data behind a public piece, when it holds names, contact details, targets or figures that are not public.
- Anything about a venue or plan that has not been announced.

Copy rules that must stay private belong in `private_rules.py` next to the copy checker, not here.

## Rules

- Keep each piece in its own folder with a short README that says what it is, where it came from and when.
- Never move a file from here into a tracked folder, link to it from a public document, or quote it in public copy unless the words are already public.
- Check a file is ignored before you share the repository: `git check-ignore -v internal/<file>` prints the rule that ignores it.
