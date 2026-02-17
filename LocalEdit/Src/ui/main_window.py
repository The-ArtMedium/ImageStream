"""
Main application window for LocalEdit.
Contains the timeline, preview, and controls.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QSplitter, QMenuBar, QMenu, QAction, QStatusBar
)
from PyQt5.QtCore import Qt
from .timeline import Timeline


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config=None, locale=None):
        super().__init__()
        self.config = config
        self.locale = locale
        self.project_data = {
            'video_layer': None,
            'image_layer': None,
            'text_layer': None,
            'audio_layer': None
        }
        self.init_ui()

    def t(self, key, default=''):
        """Translate a key using locale manager."""
        if self.locale:
            return self.locale.get(key, default)
        return default

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("LocalEdit - Simple. Local. Yours.")
        self.setMinimumSize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.create_menu_bar()

        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Vertical)

        preview_widget = self.create_preview_area()
        splitter.addWidget(preview_widget)

        self.timeline = Timeline()
        splitter.addWidget(self.timeline)

        splitter.setSizes([400, 400])

        main_layout.addWidget(splitter)

        self.statusBar().showMessage(self.t('status.ready', 'Ready'))

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.t('menu.file', 'File'))

        new_action = QAction(self.t('menu.new_project', 'New Project'), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction(self.t('menu.open_project', 'Open Project'), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction(self.t('menu.save_project', 'Save Project'), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction(self.t('menu.exit', 'Exit'), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu(self.t('menu.edit', 'Edit'))

        undo_action = QAction(self.t('menu.undo', 'Undo'), self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction(self.t('menu.redo', 'Redo'), self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        export_menu = menubar.addMenu(self.t('menu.export', 'Export'))

        export_action = QAction(self.t('menu.export_mp4', 'Export to MP4'), self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_video)
        export_menu.addAction(export_action)

        help_menu = menubar.addMenu(self.t('menu.help', 'Help'))

        about_action = QAction(self.t('menu.about', 'About LocalEdit'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        language_menu = menubar.addMenu("🌍 Language")

        if self.locale:
            available = self.locale.get_available_languages()
            for code, name in available.items():
                lang_action = QAction(name, self)
                lang_action.triggered.connect(
                    lambda checked, c=code: self.switch_language(c)
                )
                language_menu.addAction(lang_action)

    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QHBoxLayout()

        video_btn = QPushButton("📹 " + self.t('toolbar.add_video', 'Add Video/Image'))
        video_btn.clicked.connect(self.import_video)
        toolbar.addWidget(video_btn)

        overlay_btn = QPushButton("🖼️ " + self.t('toolbar.add_overlay', 'Add Overlay'))
        overlay_btn.clicked.connect(self.import_overlay)
        toolbar.addWidget(overlay_btn)

        text_btn = QPushButton("📝 " + self.t('toolbar.add_text', 'Add Text'))
        text_btn.clicked.connect(self.add_text)
        toolbar.addWidget(text_btn)

        audio_btn = QPushButton("🎵 " + self.t('toolbar.add_audio', 'Add Audio'))
        audio_btn.clicked.connect(self.import_audio)
        toolbar.addWidget(audio_btn)

        toolbar.addStretch()

        export_btn = QPushButton("💾 " + self.t('toolbar.export_video', 'Export Video'))
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        export_btn.clicked.connect(self.export_video)
        toolbar.addWidget(export_btn)

        return toolbar

    def create_preview_area(self):
        """Create the preview area."""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        preview_label = QLabel("Preview Area")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px dashed #666666;
                font-size: 18px;
                min-height: 300px;
            }
        """)

        preview_layout.addWidget(preview_label)
        return preview_widget

    def switch_language(self, language_code):
        """Switch application language."""
        if self.locale:
            self.locale.switch_language(language_code)
        if self.config:
            self.config.set_language(language_code)
        QMessageBox.information(
            self,
            "Language",
            f"Language changed! Please restart LocalEdit to apply."
        )

    def new_project(self):
        """Create a new project."""
        reply = QMessageBox.question(
            self,
            self.t('dialogs.new_project_title', 'New Project'),
            self.t('dialogs.new_project_message', 'Create a new project? Unsaved changes will be lost.'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.project_data = {
                'video_layer': None,
                'image_layer': None,
                'text_layer': None,
                'audio_layer': None
            }
            self.timeline.clear()
            self.statusBar().showMessage(self.t('status.new_project_created', 'New project created'))

    def open_project(self):
        """Open an existing project."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t('dialogs.open_project_title', 'Open Project'),
            "",
            "LocalEdit Projects (*.lep);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(self.t('status.opening_project', 'Opening project') + f": {filename}")

    def save_project(self):
        """Save the current project."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.t('dialogs.save_project_title', 'Save Project'),
            "",
            "LocalEdit Projects (*.lep);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(self.t('status.saving_project', 'Saving project') + f": {filename}")

    def import_video(self):
        """Import video or image for Layer 1."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t('dialogs.import_video_title', 'Import Video/Image'),
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        )
        if filename:
            self.project_data['video_layer'] = filename
            self.timeline.add_to_layer(1, filename)
            self.statusBar().showMessage(self.t('status.added_to_layer', 'Added to Layer') + f" 1: {filename}")

    def import_overlay(self):
        """Import image overlay for Layer 2."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t('dialogs.import_overlay_title', 'Import Image Overlay'),
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        if filename:
            self.project_data['image_layer'] = filename
            self.timeline.add_to_layer(2, filename)
            self.statusBar().showMessage(self.t('status.added_to_layer', 'Added to Layer') + f" 2: {filename}")

    def add_text(self):
        """Add text to Layer 3."""
        self.statusBar().showMessage(self.t('status.text_editor_coming', 'Text editor coming soon!'))

    def import_audio(self):
        """Import audio for Layer 4."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t('dialogs.import_audio_title', 'Import Audio'),
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac);;All Files (*)"
        )
        if filename:
            self.project_data['audio_layer'] = filename
            self.timeline.add_to_layer(4, filename)
            self.statusBar().showMessage(self.t('status.added_to_layer', 'Added to Layer') + f" 4: {filename}")

    def export_video(self):
        """Export the final video."""
        if not any(self.project_data.values()):
            QMessageBox.warning(
                self,
                self.t('dialogs.nothing_to_export', 'Nothing to Export'),
                self.t('dialogs.add_media_first', 'Please add some media to your project first!')
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.t('dialogs.export_title', 'Export Video'),
            "",
            "MP4 Video (*.mp4);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(self.t('status.exporting_to', 'Exporting to') + f": {filename}")
            QMessageBox.information(
                self,
                self.t('dialogs.export_success', 'Export'),
                self.t('dialogs.export_coming_soon', 'Export functionality coming soon!') + "\n\n" + filename
            )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            self.t('about.title', 'About LocalEdit'),
            f"""<h2>LocalEdit</h2>
            <p><b>{self.t('app.tagline', 'Simple. Local. Yours.')}</b></p>
            <p>Version {self.t('app.version', '0.1.0')}</p>
            <p>{self.t('about.description', 'A lightweight video editor for creators who value ownership and privacy.')}</p>
            <p>{self.t('about.features', 'No cloud uploads. No watermarks. No subscriptions.')}</p>
            <br>
            <p><i>{self.t('about.signature', 'Baperebup!')} ✨</i></p>
            <p>{self.t('about.license', 'Licensed under MIT License')}</p>
            """
        )