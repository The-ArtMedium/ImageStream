import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ui.controls_panel import ControlsPanel
from ui.preview_widget import PreviewWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LocalRAW")
        self.setMinimumSize(1200, 800)

        self.image_files = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # LEFT PANEL
        left_panel = QVBoxLayout()

        self.import_button = QPushButton("Import Folder")
        self.import_button.clicked.connect(self.import_folder)

        self.status_label = QLabel("No folder loaded")

        left_panel.addWidget(self.import_button)
        left_panel.addWidget(self.status_label)

        # THUMBNAIL AREA
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.grid_layout = QGridLayout()

        self.scroll_area_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)

        # CENTER PREVIEW
        self.preview = PreviewWidget()

        # RIGHT CONTROLS
        self.controls = ControlsPanel()

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.scroll_area, 2)
        main_layout.addWidget(self.preview, 3)
        main_layout.addWidget(self.controls, 1)

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            files = []
            supported_extensions = (".jpg", ".jpeg", ".png", ".cr2", ".nef", ".arw", ".dng")

            for f in os.listdir(folder):
                if f.lower().endswith(supported_extensions):
                    files.append(os.path.join(folder, f))

            self.image_files = files
            self.status_label.setText(f"{len(files)} images found")

            self.display_thumbnails()

    def display_thumbnails(self):
        # Clear existing thumbnails
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        row = 0
        col = 0

        for file_path in self.image_files:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(pixmap)

            self.grid_layout.addWidget(label, row, col)

            col += 1
            if col > 4:
                col = 0
                row += 1