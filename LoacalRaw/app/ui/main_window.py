from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QFileDialog, QLabel
)
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

        # Left side (Library area)
        left_panel = QVBoxLayout()

        self.import_button = QPushButton("Import Folder")
        self.import_button.clicked.connect(self.import_folder)

        self.status_label = QLabel("No folder loaded")

        left_panel.addWidget(self.import_button)
        left_panel.addWidget(self.status_label)

        # Center + Right
        self.preview = PreviewWidget()
        self.controls = ControlsPanel()

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.preview, 3)
        main_layout.addWidget(self.controls, 1)

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            import os

            supported_extensions = (".jpg", ".jpeg", ".png", ".cr2", ".nef", ".arw", ".dng")

            files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(supported_extensions)
            ]

            self.image_files = files
            self.status_label.setText(f"{len(files)} images found")