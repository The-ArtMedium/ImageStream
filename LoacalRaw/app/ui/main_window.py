import os
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QGridLayout,
    QSlider, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

from app.core.pipeline import Pipeline
from app.core.exporter import Exporter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LocalRAW v1.0.0")
        self.setMinimumSize(1300, 800)

        self.pipeline = Pipeline()
        self.exporter = Exporter()

        self.image_files = []
        self.current_image = None

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # ================= LEFT PANEL (Thumbnails)
        left_panel = QVBoxLayout()

        self.import_button = QPushButton("Import Folder")
        self.import_button.clicked.connect(self.import_folder)

        self.status_label = QLabel("No folder loaded")

        left_panel.addWidget(self.import_button)
        left_panel.addWidget(self.status_label)

        # Thumbnail scroll area
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()

        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        # ================= CENTER (Preview)
        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumWidth(600)

        # ================= RIGHT PANEL (Controls)
        right_panel = QVBoxLayout()

        # Exposure Slider
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(-30)
        self.exposure_slider.setMaximum(30)
        self.exposure_slider.setValue(0)
        self.exposure_slider.valueChanged.connect(self.update_adjustments)

        # Sharpen Slider
        self.sharpen_slider = QSlider(Qt.Horizontal)
        self.sharpen_slider.setMinimum(0)
        self.sharpen_slider.setMaximum(20)
        self.sharpen_slider.setValue(0)
        self.sharpen_slider.valueChanged.connect(self.update_adjustments)

        # Export Button
        self.export_button = QPushButton("Export Image")
        self.export_button.clicked.connect(self.export_image)

        right_panel.addWidget(QLabel("Exposure"))
        right_panel.addWidget(self.exposure_slider)
        right_panel.addWidget(QLabel("Sharpen"))
        right_panel.addWidget(self.sharpen_slider)
        right_panel.addWidget(self.export_button)
        right_panel.addStretch()

        # ================= Add to Main Layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.scroll_area, 3)
        main_layout.addWidget(self.preview_label, 4)
        main_layout.addLayout(right_panel, 2)

    # -------------------------
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

    # -------------------------
    def display_thumbnails(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        row, col = 0, 0

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
            label.mousePressEvent = lambda event, path=file_path: self.load_image(path)

            self.grid_layout.addWidget(label, row, col)

            col += 1
            if col > 4:
                col = 0
                row += 1

    # -------------------------
    def load_image(self, file_path):
        image = cv2.imread(file_path)

        if image is None:
            return

        self.current_image = image
        self.apply_pipeline()

    # -------------------------
    def update_adjustments(self):
        self.pipeline.exposure = self.exposure_slider.value() / 10.0
        self.pipeline.sharpen_amount = self.sharpen_slider.value() / 10.0
        self.apply_pipeline()

    # -------------------------
    def apply_pipeline(self):
        if self.current_image is None:
            return

        processed = self.pipeline.apply(self.current_image)

        height, width, channel = processed.shape
        bytes_per_line = 3 * width

        qimg = QImage(
            processed.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        ).rgbSwapped()

        pixmap = QPixmap.fromImage(qimg)

        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # -------------------------
    def export_image(self):
        if self.current_image is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            "JPEG (*.jpg);;PNG (*.png)"
        )

        if path:
            processed = self.pipeline.apply(self.current_image)
            self.exporter.save(processed, path)
            QMessageBox.information(self, "Export", "Image exported successfully.")