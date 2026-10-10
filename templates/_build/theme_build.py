"""Office theme files: a .thmx per brand (Design > Themes > Browse for Themes in Word, Excel and PowerPoint), plus the
colour and font schemes on their own for the Office Document Themes folder.

python3 theme_build.py
"""
import os
import zipfile

import brand as B
import ooxml_theme as T

XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
NS_A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'


def main():
    d = os.path.join(B.OUT, "office", "_shared", "office-theme")
    for sub in ("Theme Colors", "Theme Fonts"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for b in B.BRANDS:
        p = os.path.join(d, "%s.thmx" % b)
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                       '<Default Extension="xml" ContentType="application/xml"/><Override PartName="/theme/theme/theme1.xml" '
                       'ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
            z.writestr("_rels/.rels", XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" '
                       'Target="theme/theme/theme1.xml"/></Relationships>')
            z.writestr("theme/theme/theme1.xml", T.theme_xml(b))
        print(p)
    open(os.path.join(d, "Theme Colors", "Climb.xml"), "w").write(XML + T.clr_scheme("Climb").replace("<a:clrScheme", "<a:clrScheme " + NS_A, 1))
    open(os.path.join(d, "Theme Fonts", "Climb.xml"), "w").write(XML + T.font_scheme("Climb").replace("<a:fontScheme", "<a:fontScheme " + NS_A, 1))


if __name__ == "__main__":
    main()
