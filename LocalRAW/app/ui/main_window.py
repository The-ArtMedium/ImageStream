import os
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QScrollArea, QGridLayout,
    QSlider, QGroupBox, QMessageBox,
    QSizePolicy, QInputDialog, QLineEdit,
    QDialog, QFormLayout, QDialogButtonBox,
    QComboBox, QTextEdit
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from app.core.pipeline import Pipeline
from app.core.exporter import Exporter
from app.core.raw_loader import RawLoader
from app.core.batch_renamer import BatchRenamer
from app.core.watermarker import Watermarker
from app.core.metadata_editor import MetadataEditor
from app.utils.file_utils import get_files_in_folder
from app.utils.image_utils import numpy_to_pixmap, resize_for_preview


PREVIEW_MAX = 1200


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LocalRAW v1.2.0")
        self.setMinimumSize(1400, 850)

        self.pipeline = Pipeline()
        self.exporter = Exporter()
        self.raw_loader = RawLoader()
        self.batch_renamer = BatchRenamer()
        self.watermarker = Watermarker()
        self.metadata_editor = MetadataEditor()

        self.current_image = None
        self.current_file_path = None
        self.preview_image = None
        self.image_files = []

        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(80)
        self._preview_timer.timeout.connect(self.apply_pipeline)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # ===== LEFT PANEL
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
        left_layout.addWidget(self.scroll_area)

        # Tools row
        tools_layout = QVBoxLayout()
        self.batch_rename_button = QPushButton("Batch Rename")
        self.batch_rename_button.clicked.connect(self.open_batch_rename)
        self.metadata_button = QPushButton("Metadata")
        self.metadata_button.clicked.connect(self.open_metadata)
        tools_layout.addWidget(self.batch_rename_button)
        tools_layout.addWidget(self.metadata_button)
        left_layout.addLayout(tools_layout)

        # ===== CENTER PANEL
        self.preview_label = QLabel("Open a folder and select an image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1a1a1a; color: #555;")
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ===== RIGHT PANEL
        right_layout = QVBoxLayout()

        # White Balance
        wb_group = QGroupBox("White Balance")
        self.temp_slider = self._make_slider(-50, 50, 0)
        self.tint_slider = self._make_slider(-50, 50, 0)
        wb_layout = QVBoxLayout()
        wb_layout.addWidget(QLabel("Temperature"))
        wb_layout.addWidget(self.temp_slider)
        wb_layout.addWidget(QLabel("Tint"))
        wb_layout.addWidget(self.tint_slider)
        wb_group.setLayout(wb_layout)

        # Tone
        tone_group = QGroupBox("Tone")
        self.exposure_slider = self._make_slider(-30, 30, 0)
        self.contrast_slider = self._make_slider(-50, 50, 0)
        tone_layout = QVBoxLayout()
        tone_layout.addWidget(QLabel("Exposure"))
        tone_layout.addWidget(self.exposure_slider)
        tone_layout.addWidget(QLabel("Contrast"))
        tone_layout.addWidget(self.contrast_slider)
        tone_group.setLayout(tone_layout)

        # Detail
        detail_group = QGroupBox("Detail")
        self.sharpen_slider = self._make_slider(0, 20, 0)
        detail_layout = QVBoxLayout()
        detail_layout.addWidget(QLabel("Sharpen"))
        detail_layout.addWidget(self.sharpen_slider)
        detail_group.setLayout(detail_layout)

        # Noise Reduction
        nr_group = QGroupBox("Noise Reduction")
        self.nr_lum_slider = self._make_slider(0, 100, 0)
        self.nr_color_slider = self._make_slider(0, 100, 0)
        nr_layout = QVBoxLayout()
        nr_layout.addWidget(QLabel("Luminance"))
        nr_layout.addWidget(self.nr_lum_slider)
        nr_layout.addWidget(QLabel("Color"))
        nr_layout.addWidget(self.nr_color_slider)
        nr_group.setLayout(nr_layout)

        # Dehaze
        dehaze_group = QGroupBox("Dehaze")
        self.dehaze_slider = self._make_slider(0, 100, 0)
        dehaze_layout = QVBoxLayout()
        dehaze_layout.addWidget(QLabel("Amount"))
        dehaze_layout.addWidget(self.dehaze_slider)
        dehaze_group.setLayout(dehaze_layout)

        # Watermark
        wm_group = QGroupBox("Watermark")
        self.watermark_button = QPushButton("Add Watermark...")
        self.watermark_button.clicked.connect(self.open_watermark)
        wm_layout = QVBoxLayout()
        wm_layout.addWidget(self.watermark_button)
        wm_group.setLayout(wm_layout)

        # Reset + Export
        self.reset_button = QPushButton("Reset All")
        self.reset_button.clicked.connect(self.reset_sliders)
        self.export_button = QPushButton("Export Image")
        self.export_button.clicked.connect(self.export_image)

        right_layout.addWidget(wb_group)
        right_layout.addWidget(tone_group)
        right_layout.addWidget(detail_group)
        right_layout.addWidget(nr_group)
        right_layout.addWidget(dehaze_group)
        right_layout.addWidget(wm_group)
        right_layout.addWidget(self.reset_button)
        right_layout.addWidget(self.export_button)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.preview_label, 6)
        main_layout.addLayout(right_layout, 3)

    # ─────────────────────────────────────────────────

    def _make_slider(self, min_val, max_val, default):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(self._on_slider_changed)
        return slider

    def _on_slider_changed(self):
        self._preview_timer.start()

    # ─────────────────────────────────────────────────

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.image_files = get_files_in_folder(folder)
            self.status_label.setText(f"{len(self.image_files)} images found")
            self.display_thumbnails()

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
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label = QLabel()
            label.setPixmap(pixmap)
            label.setCursor(Qt.PointingHandCursor)
            label.setToolTip(os.path.basename(file_path))
            label.mousePressEvent = lambda event, path=file_path: self.load_image(path)
            self.grid_layout.addWidget(label, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    # ─────────────────────────────────────────────────

    def load_image(self, file_path):
        try:
            image = self.raw_loader.load_image(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            return
        if image is None:
            return
        self.current_image = image
        self.current_file_path = file_path
        self.preview_image = resize_for_preview(image, max_size=PREVIEW_MAX)
        self.apply_pipeline()

    # ─────────────────────────────────────────────────

    def update_pipeline_values(self):
        self.pipeline.temperature = self.temp_slider.value()
        self.pipeline.tint = self.tint_slider.value()
        self.pipeline.exposure = self.exposure_slider.value() / 10.0
        self.pipeline.contrast = self.contrast_slider.value()
        self.pipeline.sharpen_amount = self.sharpen_slider.value() / 10.0
        self.pipeline.nr_luminance = self.nr_lum_slider.value() / 100.0
        self.pipeline.nr_color = self.nr_color_slider.value() / 100.0
        self.pipeline.dehaze = self.dehaze_slider.value() / 100.0

    def apply_pipeline(self):
        if self.preview_image is None:
            return
        self.update_pipeline_values()
        processed = self.pipeline.apply(self.preview_image)
        pixmap = numpy_to_pixmap(processed)
        self.preview_label.setPixmap(
            pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    # ─────────────────────────────────────────────────

    def reset_sliders(self):
        for slider in [
            self.temp_slider, self.tint_slider,
            self.exposure_slider, self.contrast_slider,
            self.sharpen_slider, self.nr_lum_slider,
            self.nr_color_slider, self.dehaze_slider
        ]:
            slider.blockSignals(True)
            slider.setValue(0)
            slider.blockSignals(False)
        self.pipeline.reset()
        self.apply_pipeline()

    # ─────────────────────────────────────────────────

    def export_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Export", "No image loaded.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Image", "", "JPEG (*.jpg);;PNG (*.png)"
        )
        if path:
            self.update_pipeline_values()
            processed = self.pipeline.apply(self.current_image)
            self.exporter.save(processed, path)
            QMessageBox.information(self, "Export", "Image exported successfully.")

    # ─────────────────────────────────────────────────

    def open_batch_rename(self):
        if not self.image_files:
            QMessageBox.warning(self, "Batch Rename", "No folder loaded.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Batch Rename")
        dialog.setMinimumWidth(500)
        layout = QFormLayout()

        pattern_input = QLineEdit("{prefix}_{date}_{n}")
        prefix_input = QLineEdit()
        preview_box = QTextEdit()
        preview_box.setReadOnly(True)
        preview_box.setMaximumHeight(200)

        def update_preview():
            results = self.batch_renamer.preview(
                self.image_files,
                pattern_input.text(),
                prefix_input.text()
            )
            lines = [f"{os.path.basename(old)} → {new}" for old, new in results[:10]]
            if len(self.image_files) > 10:
                lines.append(f"... and {len(self.image_files) - 10} more")
            preview_box.setText("\n".join(lines))

        pattern_input.textChanged.connect(update_preview)
        prefix_input.textChanged.connect(update_preview)

        layout.addRow("Pattern:", pattern_input)
        layout.addRow("Prefix:", prefix_input)
        layout.addRow("Preview:", preview_box)

        hint = QLabel("Tokens: {name} {n} {date} {prefix} {ext}")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addRow(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.setLayout(layout)
        update_preview()

        if dialog.exec() == QDialog.Accepted:
            results = self.batch_renamer.execute(
                self.image_files,
                pattern_input.text(),
                prefix_input.text()
            )
            success = sum(1 for _, _, ok, _ in results if ok)
            failed = [(old, err) for old, _, ok, err in results if not ok]

            msg = f"{success} files renamed successfully."
            if failed:
                msg += f"\n{len(failed)} failed."
            QMessageBox.information(self, "Batch Rename", msg)
            self.import_folder()

    # ─────────────────────────────────────────────────

    def open_watermark(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Watermark", "No image loaded.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Watermark")
        layout = QFormLayout()

        text_input = QLineEdit("© Your Name")
        position_combo = QComboBox()
        position_combo.addItems(self.watermarker.POSITIONS)
        position_combo.setCurrentText("bottom_right")

        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(10, 100)
        opacity_slider.setValue(60)

        layout.addRow("Text:", text_input)
        layout.addRow("Position:", position_combo)
        layout.addRow("Opacity:", opacity_slider)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            self.update_pipeline_values()
            processed = self.pipeline.apply(self.current_image)
            watermarked = self.watermarker.apply_text(
                processed,
                text=text_input.text(),
                position=position_combo.currentText(),
                opacity=opacity_slider.value() / 100.0
            )
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Watermarked Image", "", "JPEG (*.jpg);;PNG (*.png)"
            )
            if path:
                self.exporter.save(watermarked, path)
                QMessageBox.information(self, "Watermark", "Watermarked image exported.")

    # ─────────────────────────────────────────────────

    def open_metadata(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "Metadata", "No image loaded.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Metadata Editor")
        dialog.setMinimumWidth(480)
        layout = QFormLayout()

        summary = self.metadata_editor.summary(self.current_file_path)
        exif_box = QTextEdit(summary)
        exif_box.setReadOnly(True)
        exif_box.setMaximumHeight(180)

        artist_input = QLineEdit()
        copyright_input = QLineEdit()
        description_input = QLineEdit()

        layout.addRow("EXIF Data:", exif_box)
        layout.addRow("Artist:", artist_input)
        layout.addRow("Copyright:", copyright_input)
        layout.addRow("Description:", description_input)

        note = QLabel("Changes are written to exported JPEG files only.")
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addRow(note)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            ext = os.path.splitext(self.current_file_path)[1].lower()
            if ext not in [".jpg", ".jpeg"]:
                QMessageBox.information(self, "Metadata", "Metadata writing is only supported for JPEG files.\nExport as JPEG first.")
                return
            try:
                self.metadata_editor.write(
                    self.current_file_path,
                    artist=artist_input.text(),
                    copyright=copyright_input.text(),
                    description=description_input.text()
                )
                QMessageBox.information(self, "Metadata", "Metadata saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Metadata Error", str(e))
