import os
import numpy as np
from pathlib import Path

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
from app.utils.i18n import Translator


PREVIEW_MAX = 1200

LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("pt", "Português"),
    ("ar", "العربية"),
    ("hi", "हिन्दी"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.i18n = Translator("en")

        self.setWindowTitle(f"{self.i18n.t('app_name')} v1.2.0")
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

        # Language selector
        lang_row = QHBoxLayout()
        self.language_label_widget = QLabel(self.i18n.t("language_label"))
        self.language_combo = QComboBox()
        for code, name in LANGUAGES:
            self.language_combo.addItem(name, code)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.language_label_widget)
        lang_row.addWidget(self.language_combo)
        left_layout.addLayout(lang_row)

        self.import_button = QPushButton(self.i18n.t("import_folder"))
        self.import_button.clicked.connect(self.import_folder)
        self.status_label = QLabel(self.i18n.t("no_folder"))
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
        self.batch_rename_button = QPushButton(self.i18n.t("batch_rename_button"))
        self.batch_rename_button.clicked.connect(self.open_batch_rename)
        self.metadata_button = QPushButton(self.i18n.t("metadata_button"))
        self.metadata_button.clicked.connect(self.open_metadata)
        tools_layout.addWidget(self.batch_rename_button)
        tools_layout.addWidget(self.metadata_button)
        left_layout.addLayout(tools_layout)

        # ===== CENTER PANEL
        self.preview_label = QLabel(self.i18n.t("preview_placeholder"))
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1a1a1a; color: #555;")
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ===== RIGHT PANEL
        right_layout = QVBoxLayout()

        # White Balance
        self.wb_group = QGroupBox(self.i18n.t("white_balance"))
        self.temp_slider = self._make_slider(-50, 50, 0)
        self.tint_slider = self._make_slider(-50, 50, 0)
        wb_layout = QVBoxLayout()
        self.temperature_label_widget = QLabel(self.i18n.t("temperature"))
        wb_layout.addWidget(self.temperature_label_widget)
        wb_layout.addWidget(self.temp_slider)
        self.tint_label_widget = QLabel(self.i18n.t("tint"))
        wb_layout.addWidget(self.tint_label_widget)
        wb_layout.addWidget(self.tint_slider)
        self.wb_group.setLayout(wb_layout)

        # Tone
        self.tone_group = QGroupBox(self.i18n.t("tone"))
        self.exposure_slider = self._make_slider(-30, 30, 0)
        self.contrast_slider = self._make_slider(-50, 50, 0)
        tone_layout = QVBoxLayout()
        self.exposure_label_widget = QLabel(self.i18n.t("exposure"))
        tone_layout.addWidget(self.exposure_label_widget)
        tone_layout.addWidget(self.exposure_slider)
        self.contrast_label_widget = QLabel(self.i18n.t("contrast"))
        tone_layout.addWidget(self.contrast_label_widget)
        tone_layout.addWidget(self.contrast_slider)
        self.tone_group.setLayout(tone_layout)

        # Detail
        self.detail_group = QGroupBox(self.i18n.t("detail"))
        self.sharpen_slider = self._make_slider(0, 20, 0)
        detail_layout = QVBoxLayout()
        self.sharpen_label_widget = QLabel(self.i18n.t("sharpen"))
        detail_layout.addWidget(self.sharpen_label_widget)
        detail_layout.addWidget(self.sharpen_slider)
        self.detail_group.setLayout(detail_layout)

        # Noise Reduction
        self.nr_group = QGroupBox(self.i18n.t("noise_reduction"))
        self.nr_lum_slider = self._make_slider(0, 100, 0)
        self.nr_color_slider = self._make_slider(0, 100, 0)
        nr_layout = QVBoxLayout()
        self.luminance_label_widget = QLabel(self.i18n.t("luminance"))
        nr_layout.addWidget(self.luminance_label_widget)
        nr_layout.addWidget(self.nr_lum_slider)
        self.color_label_widget = QLabel(self.i18n.t("color"))
        nr_layout.addWidget(self.color_label_widget)
        nr_layout.addWidget(self.nr_color_slider)
        self.nr_group.setLayout(nr_layout)

        # Dehaze
        self.dehaze_group = QGroupBox(self.i18n.t("dehaze"))
        self.dehaze_slider = self._make_slider(0, 100, 0)
        dehaze_layout = QVBoxLayout()
        self.amount_label_widget = QLabel(self.i18n.t("amount"))
        dehaze_layout.addWidget(self.amount_label_widget)
        dehaze_layout.addWidget(self.dehaze_slider)
        self.dehaze_group.setLayout(dehaze_layout)

        # Watermark
        self.wm_group = QGroupBox(self.i18n.t("watermark"))
        self.watermark_button = QPushButton(self.i18n.t("add_watermark_button"))
        self.watermark_button.clicked.connect(self.open_watermark)
        wm_layout = QVBoxLayout()
        wm_layout.addWidget(self.watermark_button)
        self.wm_group.setLayout(wm_layout)

        # Reset + Export
        self.reset_button = QPushButton(self.i18n.t("reset_all"))
        self.reset_button.clicked.connect(self.reset_sliders)
        self.export_button = QPushButton(self.i18n.t("export_image_button"))
        self.export_button.clicked.connect(self.export_image)

        right_layout.addWidget(self.wb_group)
        right_layout.addWidget(self.tone_group)
        right_layout.addWidget(self.detail_group)
        right_layout.addWidget(self.nr_group)
        right_layout.addWidget(self.dehaze_group)
        right_layout.addWidget(self.wm_group)
        right_layout.addWidget(self.reset_button)
        right_layout.addWidget(self.export_button)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.preview_label, 6)
        main_layout.addLayout(right_layout, 3)

    # ─────────────────────────────────────────────────

    def _on_language_changed(self, index):
        code = self.language_combo.itemData(index)
        self.i18n.set_language(code)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(f"{self.i18n.t('app_name')} v1.2.0")
        self.language_label_widget.setText(self.i18n.t("language_label"))
        self.import_button.setText(self.i18n.t("import_folder"))
        if not self.image_files:
            self.status_label.setText(self.i18n.t("no_folder"))
        else:
            self.status_label.setText(self.i18n.t("images_found", n=len(self.image_files)))
        self.batch_rename_button.setText(self.i18n.t("batch_rename_button"))
        self.metadata_button.setText(self.i18n.t("metadata_button"))
        if self.current_image is None:
            self.preview_label.setText(self.i18n.t("preview_placeholder"))

        self.wb_group.setTitle(self.i18n.t("white_balance"))
        self.temperature_label_widget.setText(self.i18n.t("temperature"))
        self.tint_label_widget.setText(self.i18n.t("tint"))

        self.tone_group.setTitle(self.i18n.t("tone"))
        self.exposure_label_widget.setText(self.i18n.t("exposure"))
        self.contrast_label_widget.setText(self.i18n.t("contrast"))

        self.detail_group.setTitle(self.i18n.t("detail"))
        self.sharpen_label_widget.setText(self.i18n.t("sharpen"))

        self.nr_group.setTitle(self.i18n.t("noise_reduction"))
        self.luminance_label_widget.setText(self.i18n.t("luminance"))
        self.color_label_widget.setText(self.i18n.t("color"))

        self.dehaze_group.setTitle(self.i18n.t("dehaze"))
        self.amount_label_widget.setText(self.i18n.t("amount"))

        self.wm_group.setTitle(self.i18n.t("watermark"))
        self.watermark_button.setText(self.i18n.t("add_watermark_button"))

        self.reset_button.setText(self.i18n.t("reset_all"))
        self.export_button.setText(self.i18n.t("export_image_button"))

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
        folder = QFileDialog.getExistingDirectory(self, self.i18n.t("select_folder_dialog"))
        if folder:
            self.image_files = get_files_in_folder(folder)
            self.status_label.setText(self.i18n.t("images_found", n=len(self.image_files)))
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
            QMessageBox.critical(self, self.i18n.t("load_error_title"), str(e))
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
            QMessageBox.warning(self, self.i18n.t("export_title"), self.i18n.t("export_no_image"))
            return
        # Shared LocalSuite folder — same place LocalClip and LocalEdit
        # use, so everything you produce across the suite lands in one
        # predictable spot with no connection needed between the apps.
        suite_folder = Path.home() / "Documents" / "LocalSuite" / "Saved" / "LocalRAW"
        suite_folder.mkdir(parents=True, exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(
            self, self.i18n.t("export_dialog_title"), str(suite_folder), "JPEG (*.jpg);;PNG (*.png)"
        )
        if path:
            self.update_pipeline_values()
            processed = self.pipeline.apply(self.current_image)
            self.exporter.save(processed, path)
            QMessageBox.information(self, self.i18n.t("export_title"), self.i18n.t("export_success"))

    # ─────────────────────────────────────────────────

    def open_batch_rename(self):
        if not self.image_files:
            QMessageBox.warning(self, self.i18n.t("batch_rename_title"), self.i18n.t("batch_rename_no_folder"))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(self.i18n.t("batch_rename_title"))
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

        layout.addRow(self.i18n.t("pattern_label"), pattern_input)
        layout.addRow(self.i18n.t("prefix_label"), prefix_input)
        layout.addRow(self.i18n.t("preview_label"), preview_box)

        hint = QLabel(self.i18n.t("tokens_hint"))
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

            msg = self.i18n.t("batch_rename_result", success=success)
            if failed:
                msg += "\n" + self.i18n.t("batch_rename_failed", n=len(failed))
            QMessageBox.information(self, self.i18n.t("batch_rename_title"), msg)
            self.import_folder()

    # ─────────────────────────────────────────────────

    def open_watermark(self):
        if self.current_image is None:
            QMessageBox.warning(self, self.i18n.t("watermark_title"), self.i18n.t("watermark_no_image"))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(self.i18n.t("watermark_dialog_title"))
        layout = QFormLayout()

        text_input = QLineEdit("© Your Name")
        position_combo = QComboBox()
        position_combo.addItems(self.watermarker.POSITIONS)
        position_combo.setCurrentText("bottom_right")

        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(10, 100)
        opacity_slider.setValue(60)

        layout.addRow(self.i18n.t("text_label"), text_input)
        layout.addRow(self.i18n.t("position_label"), position_combo)
        layout.addRow(self.i18n.t("opacity_label"), opacity_slider)

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
            suite_folder = Path.home() / "Documents" / "LocalSuite" / "Saved" / "LocalRAW"
            suite_folder.mkdir(parents=True, exist_ok=True)
            path, _ = QFileDialog.getSaveFileName(
                self, self.i18n.t("export_watermarked_title"), str(suite_folder), "JPEG (*.jpg);;PNG (*.png)"
            )
            if path:
                self.exporter.save(watermarked, path)
                QMessageBox.information(self, self.i18n.t("watermark_title"), self.i18n.t("watermark_success"))

    # ─────────────────────────────────────────────────

    def open_metadata(self):
        if not self.current_file_path:
            QMessageBox.warning(self, self.i18n.t("metadata_title"), self.i18n.t("metadata_no_image"))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(self.i18n.t("metadata_dialog_title"))
        dialog.setMinimumWidth(480)
        layout = QFormLayout()

        summary = self.metadata_editor.summary(self.current_file_path)
        exif_box = QTextEdit(summary)
        exif_box.setReadOnly(True)
        exif_box.setMaximumHeight(180)

        artist_input = QLineEdit()
        copyright_input = QLineEdit()
        description_input = QLineEdit()

        layout.addRow(self.i18n.t("exif_label"), exif_bo