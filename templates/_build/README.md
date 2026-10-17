# Template build

Scripts that generate every Office and video template from the brand tokens, the logo masters in `logos/`, the photos in `photos/` and the motif recipes in `generators/motifs.py`. Change a colour, a logo or a photo, rebuild, and every template follows.

Needs Python 3 with Pillow, numpy, python-docx and openpyxl; Node with Playwright and Chromium (for the art and type layers); ffmpeg (for the clips); LibreOffice and poppler-utils (for previews and the LibreOffice copies). Install the fonts in `office/_shared/fonts/` first so Chromium and LibreOffice render with them.

```bash
cd templates/_build
python3 art.py              # background art for slides, document covers and sheet banners (templates/_art, not committed)
python3 pptx_build.py       # office/<Brand>/powerpoint/*.potx and office/<Brand>/external/*.potx
python3 word_build.py       # office/<Brand>/word/*.dotx and office/<Brand>/external/*.dotx
python3 excel_build.py      # office/<Brand>/excel/*.xltx and office/<Brand>/external/*.xltx
python3 theme_build.py      # office/_shared/office-theme/
python3 defaults_build.py   # office/<Brand>/defaults/: Normal.dotm, Blank.potx, Book.xltx, Default Theme.thmx (run after the three above)
python3 previews_build.py   # office/previews/*.jpg and office/libreoffice/
python3 video_build.py      # video/_shared and video/<Brand>: motion clips and stills (slow: about 8 minutes a brand)
python3 resolve_build.py    # video/<Brand>/davinci-resolve/*.drfx and setting-files/ (resolve_setup.lua tests them inside Resolve)
python3 premiere_build.py   # video/<Brand>/premiere-pro/*.xml
python3 lut_build.py        # video/_shared/luts/
python3 video_previews.py   # video/previews/*.jpg
```

`video_build.py shared` builds only the shared clips; `video_build.py Climb27` builds one brand. A new edition (Climb28) is a new entry in `BRANDS` in `brand.py` plus its logo masters; every script picks it up.

The Office builders take `--only <Name> ...` to rebuild a few templates and `--copy` to print every string a reader sees, so the copy checker can run over it:

```bash
for s in word excel pptx; do python3 ${s}_build.py --copy; done | python3 ../../.agents/skills/climb-voice/scripts/check_copy.py --no-hints -
```

## Words: the copy files

Every word a template prints is in a copy file (`<name>.copy.md`) beside the template, never in a script. The builders read them through `copy_io.py` and keep only layout and logic. Change the words in the copy file, rebuild, and the template follows. The standard is `.agents/skills/climb-voice/references/copy-files.md`.

| Copy file | Holds | Read by |
| --- | --- | --- |
| `templates/brands.copy.md` | The legal line, and each brand's website, email, tagline and edition dates | `brand.py`, so every script |
| `office/<Brand>/word/<Template>.copy.md`, `office/<Brand>/external/<Template>-word.copy.md` | One Word template's words, covering its `.dotx` and its LibreOffice `.ott` | `word_build.py` (through `word_content.py`) |
| `office/word-shared.copy.md` | Lines every Word template shares: signature blocks, contents, alt text | `word_build.py` |
| `office/<Brand>/powerpoint/<Template>.copy.md`, `.../external/<Template>-powerpoint.copy.md` | One deck's example slides, one marker per slide (`<!-- @slide-3 layout="Two columns" -->`) and one section per placeholder | `pptx_build.py` (through `copy_samples.py`) |
| `office/powerpoint-layouts.copy.md` | The layout prompts every deck shares | `pptx_build.py` |
| `office/<Brand>/excel/<Template>.copy.md`, `.../external/<Template>-excel.copy.md` | One workbook's labels, headings, hints and sample rows | `excel_build.py`, `excel_books.py`, `xl.py` (through `xl_copy.py`) |
| `office/excel-shared.copy.md` | Lines every workbook shares | the same |
| `video/_shared/stills/shared-stills.copy.md`, `video/<Brand>/stills/<Brand>-stills.copy.md` | The lower thirds, stickers, caption guide, end card and title card | `video_build.py` |
| `video/resolve-titles.copy.md`, `video/<Brand>/davinci-resolve/<Brand>-titles.copy.md` | The Resolve titles' sample text, control names and brand lines | `resolve_build.py` |
| `video/_shared/luts/luts.copy.md` | The LUT title and header lines | `lut_build.py` |

A file with no words of its own (a preview sheet, a logo copy, a background) gets an `@alt` section with its alt text. A copy file marked `source: mirror` holds words a build here cannot read yet, as they print (the default files, the Office theme, the example captions): change those words where its note says, and in the mirror.

Some names stay in the scripts because other parts look them up by name: Word content-control names, PowerPoint layout and shape names, Excel sheet names and the codes in the leave planner and feedback sheets, the Resolve title names, and the core-property titles in `catalog.py`.

Check every copy file and find any template without one:

```bash
python3 ../../.agents/skills/climb-voice/scripts/check_copy.py --no-hints $(find .. -name '*.copy.md')
python3 ../../.agents/skills/climb-voice/scripts/copy_md.py coverage ../.. | grep templates/
```

`catalog.py` is the one table of templates: app, name, brands, group (Company or Events) and whether it is a co-branded external version. Adding a template is one row there plus its copy file and its content: body sections in its Word copy file, a builder in `excel_books.py` (on the helpers in `xl.py`, with its words in the workbook's copy file) or slide sections in its deck copy file (and its layouts in `deck_samples.py`). The first set (letterhead, report, proposal, press release, meeting notes, the four event sheets and the presentation template) keeps its hand-written builders and is never remade. `previews_build.py --new` renders only the catalogue templates, so the first set's sheets stay as they are.

| Script | Follows |
| --- | --- |
| `brand.py`, `ooxml_theme.py` | `tokens/brand.tokens.json` colours and fonts, the legal line, brand URLs and edition dates |
| `copy_io.py`, `xl_copy.py`, `copy_samples.py`, `deck_samples.py`, `word_content.py`, `word_build.py`, `excel_build.py`, `excel_books.py` | the climb-voice skill and its copy file standard; all sample copy passes `check_copy.py` |
| `art.py`, `pptx_build.py`, `video_build.py` | the climb-visual-style skill, `guidelines/video.md` and `guidelines/motion.md` |

The motion clips (`video/*/motion/`) and the install package (`templates/dist/`) are not committed. The `release` workflow builds both and attaches them to GitHub releases, so nothing is uploaded by hand:

- `Climb-Templates-<version>.zip` (`python3 templates/_build/package_build.py`) is built on every push to main that changes the templates and published as the `templates-v<version>` release. Releases cannot change once published, so each version is released once: bump `templates/install/VERSION` in the pull request that changes the package. The `templates version` check fails a pull request that changes the package while its version is already released.
- `climb-video-motion.zip` (`python3 templates/_build/video_build.py`, a long render) is built on a push to main that changes what the clips are drawn from (`templates/_build/`, `generators/motifs.py`, `tokens/`, `logos/` or the fonts), or when no motion release exists yet, and published as a new `climb-video-motion-<date>-<commit>` release. The newest one is current.

Every release is created as a draft, given its file, then published. Nothing needs starting by hand; running the workflow from the Actions tab rebuilds both.

See `templates/install/README.md`.
