#!/bin/bash
# LocalRAW macOS Build Script
# Creates LocalRAW.app and LocalRAW.dmg
#
# Requirements:
#   pip install pyinstaller
#   brew install create-dmg
#
# Run from the root of the project:
#   chmod +x installer/build_mac.sh
#   ./installer/build_mac.sh

set -e  # Stop on any error

APP_NAME="LocalRAW"
VERSION="1.0.0"
DIST_DIR="dist"
DMG_DIR="dist/dmg"

echo "========================================"
echo "  LocalRAW macOS Build"
echo "  Version: $VERSION"
echo "========================================"

# ─── Step 1: Clean previous build
echo ""
echo "[1/4] Cleaning previous build..."
rm -rf build dist __pycache__
echo "Done."

# ─── Step 2: Build .app with PyInstaller
echo ""
echo "[2/4] Building LocalRAW.app with PyInstaller..."
pyinstaller LocalRAW.spec --clean
echo "Done. App at: dist/LocalRAW.app"

# ─── Step 3: Prepare DMG staging folder
echo ""
echo "[3/4] Preparing DMG contents..."
mkdir -p "$DMG_DIR"
cp -r "$DIST_DIR/LocalRAW.app" "$DMG_DIR/"
echo "Done."

# ─── Step 4: Create DMG
echo ""
echo "[4/4] Creating LocalRAW.dmg..."
create-dmg \
    --volname "$APP_NAME $VERSION" \
    --volicon "resources/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "LocalRAW.app" 175 190 \
    --hide-extension "LocalRAW.app" \
    --app-drop-link 425 190 \
    --background "resources/dmg_background.png" \
    "dist/$APP_NAME-$VERSION-macOS.dmg" \
    "$DMG_DIR/"

echo ""
echo "========================================"
echo "  BUILD COMPLETE"
echo "  App:  dist/LocalRAW.app"
echo "  DMG:  dist/LocalRAW-$VERSION-macOS.dmg"
echo "========================================"
