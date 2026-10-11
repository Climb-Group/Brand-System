# Template build

Scripts that generate every Office and video template from the brand tokens, the logo masters in `logos/`, the photos in `photos/` and the motif recipes in `generators/motifs.py`. Change a colour, a logo or a photo, rebuild, and every template follows.

Needs Python 3 with Pillow, numpy, python-docx and openpyxl; Node with Playwright and Chromium (for the art and type layers); ffmpeg (for the clips); LibreOffice and poppler-utils (for previews and the LibreOffice copies). Install the fonts in `office/_shared/fonts/` first so Chromium and LibreOffice render with them.

```bash
cd templates/_build
python3 art.py              # background art for slides, document covers and sheet banners (templates/_art, not committed)
python3 pptx_build.py       # office/<Brand>/powerpoint/*.potx
python3 word_build.py       # office/<Brand>/word/*.dotx
python3 excel_build.py      # office/<Brand>/excel/*.xltx
python3 theme_build.py      # office/_shared/office-theme/
python3 previews_build.py   # office/previews/*.jpg and office/libreoffice/
python3 video_build.py      # video/_shared and video/<Brand>: motion clips and stills (slow: about 8 minutes a brand)
python3 resolve_build.py    # video/<Brand>/davinci-resolve/*.drfx and setting-files/ (resolve_setup.lua tests them inside Resolve)
python3 premiere_build.py   # video/<Brand>/premiere-pro/*.xml
python3 lut_build.py        # video/_shared/luts/
python3 video_previews.py   # video/previews/*.jpg
```

`video_build.py shared` builds only the shared clips; `video_build.py Climb27` builds one brand. A new edition (Climb28) is a new entry in `BRANDS` in `brand.py` plus its logo masters; every script picks it up.

| Script | Follows |
| --- | --- |
| `brand.py`, `ooxml_theme.py` | `tokens/brand.tokens.json` colours and fonts, the legal line, brand URLs and edition dates |
| `copy_samples.py`, `word_build.py`, `excel_build.py` | the climb-voice skill; all sample copy passes `check_copy.py` |
| `art.py`, `pptx_build.py`, `video_build.py` | the climb-visual-style skill, `guidelines/video.md` and `guidelines/motion.md` |

The motion clips (`video/*/motion/`) and the install package (`templates/dist/`) are not committed. The `release` workflow builds both and attaches them to GitHub releases, so nothing is uploaded by hand:

- `Climb-Templates-<version>.zip` (`python3 templates/_build/package_build.py`) is built on every push to main that changes the templates and published as the `templates-v<version>` release. Releases cannot change once published, so each version is released once: bump `templates/install/VERSION` in the pull request that changes the package. The `templates version` check fails a pull request that changes the package while its version is already released.
- `climb-video-motion.zip` (`python3 templates/_build/video_build.py`, a long render) is built on a push to main that changes what the clips are drawn from (`templates/_build/`, `generators/motifs.py`, `tokens/`, `logos/` or the fonts), or when no motion release exists yet, and published as a new `climb-video-motion-<date>-<commit>` release. The newest one is current.

Every release is created as a draft, given its file, then published. Nothing needs starting by hand; running the workflow from the Actions tab rebuilds both.

See `templates/install/README.md`.
