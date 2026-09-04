"""
LocalClip - Entry point
Simple. Local. Yours.
"""
import sys
import os

# Make sure Src/ is on the path regardless of where this is launched from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.clipper_window import ClipperWindow
from locale_manager import LocaleManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LocalClip")

    locale = LocaleManager()
    window = ClipperWindow(locale=locale)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    
