#!/bin/bash
echo "================================================"
echo "LocalEdit Installer"
echo "Simple. Local. Yours."
echo "================================================"
echo ""

echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Mac: brew install python3"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi

echo "Python found!"
echo ""

echo "Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg not found!"
    echo ""
    echo "Please install FFmpeg:"
    echo "  Mac: brew install ffmpeg"
    echo "  Linux: sudo apt install ffmpeg"
    echo ""
fi

echo "Installing LocalEdit dependencies..."
pip3 install -r Requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Installation failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "To run LocalEdit type:"
echo "  ./run.sh"
echo ""