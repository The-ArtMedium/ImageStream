#!/usr/bin/env python3
"""
LocalEdit - Simple. Local. Yours.
A lightweight video editor for creators who value ownership and privacy.
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from utils.config import get_config
from utils.locale_manager import get_locale_manager

try:
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import MainWindow
except ImportError:
    print("PyQt5 not found. Please run install.bat or install.sh first!")
    sys.exit(1)


def main():
    config = get_config()
    locale = get_locale_manager()
    locale.switch_language(config.get_language())

    print("================================================")
    print("LocalEdit - Simple. Local. Yours.")
    print("================================================")
    print(f"Language: {locale.get_current_language_name()}")
    print("Starting...")
    print()

    app = QApplication(sys.argv)
    app.setApplicationName("LocalEdit")
    app.setOrganizationName("LocalEdit")

    window = MainWindow(config=config, locale=locale)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()