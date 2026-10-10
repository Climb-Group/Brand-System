#!/bin/bash
# Build Climb-Templates-<version>.pkg for Jamf (or any MDM) from the unzipped package.
# Run on a Mac with Xcode command line tools: ./macos/build-pkg.sh [output-dir]
# Set SIGN_IDENTITY="Developer ID Installer: ..." to sign it with productsign.
#
# The pkg drops the package into /private/tmp/climb-templates and its postinstall
# runs install-climb-templates.sh, then deletes the temporary copy.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$HERE/.." && pwd)"
VERSION="$(head -n1 "$PKG/VERSION")"
OUT="${1:-$PKG}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

STAGE="$WORK/root/private/tmp/climb-templates"
mkdir -p "$STAGE" "$WORK/scripts"
cp -R "$PKG/payload" "$PKG/macos" "$PKG/VERSION" "$STAGE/"

cat > "$WORK/scripts/postinstall" <<'EOF'
#!/bin/bash
set -e
/bin/bash "/private/tmp/climb-templates/macos/install-climb-templates.sh" "$@"
rm -rf "/private/tmp/climb-templates"
exit 0
EOF
chmod 755 "$WORK/scripts/postinstall"

UNSIGNED="$WORK/Climb-Templates-$VERSION-unsigned.pkg"
pkgbuild --root "$WORK/root" --install-location / --scripts "$WORK/scripts" \
  --identifier com.climb-uk.templates --version "$VERSION" "$UNSIGNED"

TARGET="$OUT/Climb-Templates-$VERSION.pkg"
if [ -n "${SIGN_IDENTITY:-}" ]; then
  productsign --sign "$SIGN_IDENTITY" "$UNSIGNED" "$TARGET"
else
  cp "$UNSIGNED" "$TARGET"
  echo "Not signed: set SIGN_IDENTITY to sign it."
fi
echo "Built $TARGET"
