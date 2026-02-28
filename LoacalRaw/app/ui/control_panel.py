from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ControlsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Adjustments")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addStretch()--