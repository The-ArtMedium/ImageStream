import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LocalRAW")
        self.setMinimumSize(1200, 800)

        self.image_files = []

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel
        left_panel = QVBoxLayout()

        self.import_button = QPushButton("Import Folder")
        self.import_button.clicked.connect(self.import_folder)

        self.status_label = QLabel("No folder loaded")

        left_panel.addWidget(self.import_button)
        left_panel.addWidget(self.status_label)
        left_panel.addStretch()

        # Thumbnail area
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()

        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        # Add to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.scroll_area, 4)

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            supported = (
                ".jpg", ".jpeg", ".png",
                ".cr2", ".nef", ".arw", ".dng"
            )

            self.image_files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(supported)
            ]

            self.status_label.setText(f"{len(self.image_files)} images found")
            self.display_thumbnails()

    def display_thumbnails(self):
        # Clear old thumbnails
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        row = 0
        col = 0

        for file_path in self.image_files:
            pixmap = QPixmap(file_path)

            if pixmap.isNull():
                continue

            pixmap = pixmap.scaled(
                150, 150,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            label = QLabel()
            label.setPixmap(pixmap)

            self.grid_layout.addWidget(label, row, col)

            col += 1
            if col > 4:
                col = 0
                row += 1