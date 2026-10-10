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

LEGAL = ("The Investor Ladder Limited trading as ClimbGroup. Registered in England and Wales, "
         "company number 10289755. VAT GB335770882. Registered office: Suite 3, Bignell Park Barns, "
         "Chesterton, Bicester, OX26 1TD.")

BRANDS = {
    "ClimbUK": dict(url="climb-uk.com", email="queries@climb-group.com",
                    line="The Festival for Business Growth", edition=None),
    "ClimbGroup": dict(url="climb-group.com", email="queries@climb-group.com",
                       line="The Festival for Business Growth", edition=None),
    "Climb27": dict(url="climb-uk.com", email="queries@climb-group.com",
                    line="The Festival for Business Growth", edition="30 June and 1 July 2027"),
}


def logo(brand, variant, size=2048):
    """PNG of a master logo. variant: full-colour-light, full-colour-grey, reversed-dark, mono-dark, mono-white,
    icon, icon-monogram, tagline-lockup, tagline-lockup-reversed."""
    return os.path.join(LOGOS, brand, "PNG", "%s_%s_%d.png" % (brand, variant, size))


def logo_svg(brand, variant):
    return os.path.join(LOGOS, brand, "%s_%s.svg" % (brand, variant))


def photo(name):
    return os.path.join(PHOTOS, "climb_%s.jpg" % name)
