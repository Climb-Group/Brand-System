"""Brand values for the template pack. Every colour comes from docs/brand-system/tokens/brand.tokens.json."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
LOGOS = os.environ.get("CLIMB_LOGOS", os.path.join(REPO, "logos"))
PHOTOS = os.environ.get("CLIMB_PHOTOS", os.path.join(REPO, "photos"))
FONTS = os.environ.get("CLIMB_FONTS", os.path.join(REPO, "templates", "office", "_shared", "fonts"))
OUT = os.environ.get("CLIMB_TEMPLATES_OUT", os.path.join(REPO, "templates"))

# The motif recipes live with the other generators.
sys.path.insert(0, os.path.join(REPO, "generators"))

ORANGE = "E8712A"        # Climb Orange: fills, large text on white, any text on dark
DARK = "1E0F05"          # Dark Brown: default ground
CHARCOAL = "242322"      # Charcoal: second dark ground, headings on white
GREY = "E9E9E9"          # Light Grey
WHITE = "FFFFFF"
ORANGE_TEXT = "C55308"   # small orange text on white
ORANGE_TEXT_GREY = "B04902"
ORANGE_DEEP = "8D4419"   # links on white
TINT = "F2AE86"          # Orange Tint: links and small accents on dark
SLATE = "4A5878"         # body text on white
SLATE_GREY = "404C68"    # body text on Light Grey

DISPLAY = "Montserrat"
DISPLAY_XB = "Montserrat ExtraBold"
DISPLAY_BLACK = "Montserrat Black"
BODY = "Open Sans"
BODY_SEMI = "Open Sans SemiBold"

# The words every template shares (legal line, website, email, tagline, edition dates) live in templates/brands.copy.md.
sys.path.insert(0, os.path.join(REPO, ".agents", "skills", "climb-voice", "scripts"))
import copy_md  # noqa: E402

_LINES = copy_md.load(os.path.join(REPO, "templates", "brands.copy.md"))
LEGAL = _LINES.one("legal").text

BRANDS = {
    b: dict(url=_LINES.one(b.lower() + ".url").text, email=_LINES.one(b.lower() + ".email").text,
            line=_LINES.one(b.lower() + ".line").text, edition=_LINES.words(b.lower() + ".edition"))
    for b in ("ClimbUK", "ClimbGroup", "Climb27")
}


def logo(brand, variant, size=2048):
    """PNG of a master logo. variant: full-colour-light, full-colour-grey, reversed-dark, mono-dark, mono-white,
    icon, icon-monogram, tagline-lockup, tagline-lockup-reversed."""
    return os.path.join(LOGOS, brand, "PNG", "%s_%s_%d.png" % (brand, variant, size))


def logo_svg(brand, variant):
    return os.path.join(LOGOS, brand, "%s_%s.svg" % (brand, variant))


def photo(name):
    return os.path.join(PHOTOS, "climb_%s.jpg" % name)
