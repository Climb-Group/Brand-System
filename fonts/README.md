# Fonts

Montserrat (headlines) and Open Sans (body text), both free under the SIL Open Font License. Each font comes in three formats, so there is a file for every kind of app.

| Folder | Format | Use it for |
| --- | --- | --- |
| `ttf/` | TrueType (`.ttf`) | Installing on a computer, office suites, and any tool or brand centre that asks for TTF. |
| `otf/` | OpenType with PostScript outlines (`.otf`) | Design and print apps, and any tool or brand centre that asks for OTF. |
| `fonts/` itself | Web font (`.woff2`) | Web pages only. Desktop apps and font uploads do not accept it. |

Install one format per computer, not both: two copies of the same font can confuse apps. When a tool says a `.woff2` file "is not a supported format", upload the matching file from `ttf/` or `otf/` instead.

## Styles

Every style the brand uses is in both `ttf/` and `otf/`, named `<Family>-<Style>`:

- Montserrat: Regular, Medium, SemiBold, Bold, ExtraBold and Black, each with an Italic.
- Open Sans: Regular, SemiBold and Bold, each with an Italic.

| Web font | Desktop file |
| --- | --- |
| `montserrat-latin-600-normal.woff2` | `Montserrat-SemiBold` |
| `montserrat-latin-700-normal.woff2` | `Montserrat-Bold` |
| `montserrat-latin-800-normal.woff2` | `Montserrat-ExtraBold` |
| `open-sans-latin-400-normal.woff2` | `OpenSans-Regular` |
| `open-sans-latin-600-normal.woff2` | `OpenSans-SemiBold` |
| `open-sans-latin-700-normal.woff2` | `OpenSans-Bold` |

The web fonts hold the Latin characters only; the desktop files hold each family's full character set.

## Where the files come from

The desktop files are the official builds from each family's own repository, pinned to one commit:

- Montserrat: `JulietaUla/Montserrat`, `fonts/ttf` and `fonts/otf`, as published.
- Open Sans: `googlefonts/opensans`, `fonts/ttf`, as published. Open Sans has no official OTF, so `otf/OpenSans-*.otf` is made from the official TTF: the outlines are redrawn as PostScript curves (exact, with no change in shape) and the names, spacing and kerning are kept.

To fetch them again, for example after moving the pinned commits in the script:

```bash
python3 -m pip install fonttools
python3 fonts/_build/fetch_fonts.py
python3 -m unittest discover -s fonts/tests
```

The script writes every file in `ttf/` and `otf/`; a re-run with the same commits gives the same files. The tests check that every style is in both formats with the right outlines and names, and that every web font has a desktop match.

## Licence

`OFL-Montserrat.txt` and `OFL-OpenSans.txt`. Keep the licence with the fonts when you pass them on.
