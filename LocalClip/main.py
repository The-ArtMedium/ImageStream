#!/usr/bin/env python3
"""
LocalClip - Simple. Local. Yours.
A lightweight video trimming tool for creators.
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

try:
    from PyQt5.QtWidgets import QApplication
    from ui.clipper_window import ClipperWindow
    from locale_manager import get_locale_manager
except ImportError:
    print("PyQt5 not found. Please run install.bat or install.sh first!")
    sys.exit(1)


def main():
    locale = get_locale_manager()
    
    print("================================================")
    print("LocalClip - Simple. Local. Yours.")
    print("================================================")
    print(f"Language: {locale.get_language_name(locale.get_current_language())}")
    print("Starting...")
    print()

    app = QApplication(sys.argv)
    app.setApplicationName("LocalClip")
    app.setOrganizationName("LocalClip")

    window = ClipperWindow(locale=locale)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
