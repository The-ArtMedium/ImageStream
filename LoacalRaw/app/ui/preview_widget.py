from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


class PreviewWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("Preview Area")
        self.setStyleSheet("background-color: #222; color: white;")
