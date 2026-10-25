# Internal

Team-only material for the ClimbUK brand: research, testimonial analysis, sales notes, anything that names people or an unannounced venue, and the internal tools that use and extend the brand system.

The master copy is the `internal` folder of the Brand System library in the Brand Centre, next to the rest of the pack, so the pack and its internal material stay in one place. The Brand Centre sync never brings that folder into GitHub, and git ignores everything in this folder except this README, so none of it is ever committed or published. A fresh clone has only this README: get the files from the library.

## What goes here

- Analysis and research the public should not see, such as the testimonial map of who was there.
- Internal tools built on the brand system (team-only generators, checkers, dashboards and their data), each in its own folder.
- Working data behind a public piece, when it holds names, contact details, targets or figures that are not public.
- Anything about a venue or plan that has not been announced.

Copy rules that must stay private belong in `private_rules.py` next to the copy checker, not here.

## Rules

- Keep each piece in its own folder with a short README that says what it is, where it came from and when.
- Never move a file from here into a tracked folder, link to it from a public document, or quote it in public copy unless the words are already public.
- Check a file is ignored before you share the repository: `git check-ignore -v internal/<file>` prints the rule that ignores it.
