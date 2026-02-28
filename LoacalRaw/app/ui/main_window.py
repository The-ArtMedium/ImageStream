import os
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QGridLayout,
    QSlider, QGroupBox, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from app.core.pipeline import Pipeline
from app.core.exporter import Exporter
from app.core.raw_loader import RawLoader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LocalRAW v1.0.0")
        self.setMinimumSize(1400, 850)

        self.pipeline = Pipeline()
        self.exporter = Exporter()
        self.raw_loader = RawLoader()

        self.current_image = None
        self.image_files = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # ================= LEFT (Thumbnails)
        left_layout = QVBoxLayout()

        self.import_button = QPushButton("Import Folder")
        self.import_button.clicked.connect(self.import_folder)

        self.status_label = QLabel("No folder loaded")

        left_layout.addWidget(self.import_button)
        left_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        # ================= CENTER (Preview)
        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)

        # ================= RIGHT (Controls)
        right_layout = QVBoxLayout()

        # ---- White Balance ----
        wb_group = QGroupBox("White Balance")

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(-50, 50)
        self.temp_slider.valueChanged.connect(self.update_pipeline)

        self.tint_slider = QSlider(Qt.Horizontal)
        self.tint_slider.setRange(-50, 50)
        self.tint_slider.valueChanged.connect(self.update_pipeline)

        wb_layout = QVBoxLayout()
        wb_layout.addWidget(QLabel("Temperature"))
        wb_layout.addWidget(self.temp_slider)
        wb_layout.addWidget(QLabel("Tint"))
        wb_layout.addWidget(self.tint_slider)
        wb_group.setLayout(wb_layout)

        # ---- Tone ----
        tone_group = QGroupBox("Tone")

        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(-30, 30)
        self.exposure_slider.valueChanged.connect(self.update_pipeline)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(10, 30)
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(self.update_pipeline)

        tone_layout = QVBoxLayout()
        tone_layout.addWidget(QLabel("Exposure"))
        tone_layout.addWidget(self.exposure_slider)
        tone_layout.addWidget(QLabel("Contrast"))
        tone_layout.addWidget(self.contrast_slider)
        tone_group.setLayout(tone_layout)

        # ---- Detail ----
        detail_group = QGroupBox("Detail")

        self.sharpen_slider = QSlider(Qt.Horizontal)
        self.sharpen_slider.setRange(0, 20)
        self.sharpen_slider.valueChanged.connect(self.update_pipeline)

        detail_layout = QVBoxLayout()
        detail_layout.addWidget(QLabel("Sharpen"))
        detail_layout.addWidget(self.sharpen_slider)
        detail_group.setLayout(detail_layout)

        # Export Button
        self.export_button = QPushButton("Export Image")
        self.export_button.clicked.connect(self.export_image)

        right_layout.addWidget(wb_group)
        right_layout.addWidget(tone_group)
        right_layout.addWidget(detail_group)
        right_layout.addWidget(self.export_button)
        right_layout.addStretch()

        # ================= Layout Assembly
        main_layout.addLayout(left_layout, 2)
        main_layout.addWidget(self.scroll_area, 4)
        main_layout.addWidget(self.preview_label, 5)
        main_layout.addLayout(right_layout, 3)

    # --------------------------------------------------

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            supported = (".jpg", ".jpeg", ".png", ".cr2", ".nef", ".arw", ".dng")

            self.image_files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(supported)
            ]

            self.status_label.setText(f"{len(self.image_files)} images found")
            self.display_thumbnails()

    # --------------------------------------------------

    def display_thumbnails(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if