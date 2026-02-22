"""
Main clipper window for LocalClip.
Simple video trimming interface with multilingual support.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QSlider, QMenuBar, QAction, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys
sys.path.append('..')
from core.video_clipper import VideoClipper


class ClipperWindow(QMainWindow):
    """Main application window for LocalClip."""

    def __init__(self, locale=None):
        super().__init__()
        self.locale = locale
        self.clipper = VideoClipper()
        self.video_loaded = False
        self.playing = False
        self.current_position = 0
        self.in_point = 0
        self.out_point = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_playback)
        self.init_ui()

    def t(self, key, default=''):
        """Translate a key using locale manager."""
        if self.locale:
            return self.locale.get(key, default)
        return default

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("LocalClip - Simple. Local. Yours.")
        self.setMinimumSize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.create_menu_bar()

        info_label = QLabel(self.t('app.name', 'LocalClip'))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(info_label)

        tagline = QLabel(self.t('labels.tagline_subtitle', 'Trim videos. No cloud. No watermarks.'))
        tagline.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(tagline)

        self.video_info = QLabel(self.t('labels.no_video', 'No video loaded'))
        self.video_info.setAlignment(Qt.AlignCenter)
        self.video_info.setStyleSheet("padding: 20px; font-size: 14px;")
        main_layout.addWidget(self.video_info)

        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setEnabled(False)
        self.timeline_slider.valueChanged.connect(self.slider_moved)
        main_layout.addWidget(self.timeline_slider)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.time_label)

        markers_layout = QHBoxLayout()
        self.in_label = QLabel(f"{self.t('labels.in_point', 'In')}: --:--")
        self.out_label = QLabel(f"{self.t('labels.out_point', 'Out')}: --:--")
        markers_layout.addWidget(self.in_label)
        markers_layout.addStretch()
        markers_layout.addWidget(self.out_label)
        main_layout.addLayout(markers_layout)

        controls_layout = self.create_controls()
        main_layout.addLayout(controls_layout)

        main_layout.addStretch()

        self.statusBar().showMessage(self.t('status.ready', 'Ready - Import a video to begin'))

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.t('menu.file', 'File'))

        import_action = QAction(self.t('menu.import_video', 'Import Video'), self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self.import_video)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction(self.t('menu.exit', 'Exit'), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu(self.t('menu.help', 'Help'))

        about_action = QAction(self.t('menu.about', 'About LocalClip'), self)
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

    def create_controls(self):
        """Create control buttons."""
        controls = QVBoxLayout()

        import_layout = QHBoxLayout()
        import_btn = QPushButton(f"📹 {self.t('buttons.import_video', 'Import Video')}")
        import_btn.setStyleSheet("font-size: 14px; padding: 12px;")
        import_btn.clicked.connect(self.import_video)
        import_layout.addWidget(import_btn)
        controls.addLayout(import_layout)

        playback_layout = QHBoxLayout()
        
        self.play_btn = QPushButton(f"▶️ {self.t('buttons.play', 'Play')}")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_play)
        playback_layout.addWidget(self.play_btn)

        controls.addLayout(playback_layout)

        markers_layout = QHBoxLayout()

        self.mark_in_btn = QPushButton(f"📍 {self.t('buttons.mark_start', 'Mark Start (I)')}")
        self.mark_in_btn.setEnabled(False)
        self.mark_in_btn.clicked.connect(self.mark_in)
        markers_layout.addWidget(self.mark_in_btn)

        self.mark_out_btn = QPushButton(f"📍 {self.t('buttons.mark_end', 'Mark End (O)')}")
        self.mark_out_btn.setEnabled(False)
        self.mark_out_btn.clicked.connect(self.mark_out)
        markers_layout.addWidget(self.mark_out_btn)

        self.reset_btn = QPushButton(f"🔄 {self.t('buttons.reset_markers', 'Reset Markers')}")
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self.reset_markers)
        markers_layout.addWidget(self.reset_btn)

        controls.addLayout(markers_layout)

        export_layout = QHBoxLayout()
        self.export_btn = QPushButton(f"💾 {self.t('buttons.export_clip', 'Export Clip')}")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px; font-size: 14px;")
        self.export_btn.clicked.connect(self.export_clip)
        export_layout.addWidget(self.export_btn)
        controls.addLayout(export_layout)

        return controls

    def switch_language(self, language_code):
        """Switch application language."""
        if self.locale:
            self.locale.switch_language(language_code)
        QMessageBox.information(
            self,
            "Language",
            f"Language changed to {self.locale.get_language_name(language_code)}!\nPlease restart LocalClip."
        )

    def import_video(self):
        """Import a video file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t('dialogs.import_title', 'Import Video'),
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*)"
        )
        if filename:
            success = self.clipper.load_video(filename)
            if success:
                self.video_loaded = True
                duration = self.clipper.get_duration()
                self.out_point = duration

                self.timeline_slider.setEnabled(True)
                self.timeline_slider.setMaximum(int(duration * 100))
                self.timeline_slider.setValue(0)

                self.play_btn.setEnabled(True)
                self.mark_in_btn.setEnabled(True)
                self.mark_out_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.export_btn.setEnabled(True)

                from pathlib import Path
                video_name = Path(filename).name
                self.video_info.setText(f"{self.t('labels.loaded', 'Loaded')}: {video_name}\n{self.t('labels.duration', 'Duration')}: {self.format_time(duration)}")
                self.time_label.setText(f"00:00 / {self.format_time(duration)}")
                self.out_label.setText(f"{self.t('labels.out_point', 'Out')}: {self.format_time(duration)}")

                self.statusBar().showMessage(f"{self.t('status.video_loaded', 'Video loaded')}: {video_name}")
            else:
                QMessageBox.warning(
                    self, 
                    self.t('dialogs.load_error', 'Error'),
                    self.t('dialogs.load_error_msg', 'Failed to load video file!')
                )

    def toggle_play(self):
        """Toggle play/pause."""
        if not self.video_loaded:
            return

        self.playing = not self.playing
        if self.playing:
            self.play_btn.setText(f"⏸️ {self.t('buttons.pause', 'Pause')}")
            self.timer.start(100)
        else:
            self.play_btn.setText(f"▶️ {self.t('buttons.play', 'Play')}")
            self.timer.stop()

    def update_playback(self):
        """Update playback position."""
        if not self.playing:
            return

        self.current_position += 0.1
        duration = self.clipper.get_duration()

        if self.current_position >= duration:
            self.current_position = 0

        self.timeline_slider.setValue(int(self.current_position * 100))

    def slider_moved(self, value):
        """Handle slider movement."""
        if self.video_loaded:
            self.current_position = value / 100.0
            duration = self.clipper.get_duration()
            self.time_label.setText(f"{self.format_time(self.current_position)} / {self.format_time(duration)}")

    def mark_in(self):
        """Mark in point."""
        if self.video_loaded:
            self.in_point = self.current_position
            self.in_label.setText(f"{self.t('labels.in_point', 'In')}: {self.format_time(self.in_point)}")
            self.statusBar().showMessage(f"{self.t('status.start_marked', 'Start marked at')} {self.format_time(self.in_point)}")

    def mark_out(self):
        """Mark out point."""
        if self.video_loaded:
            self.out_point = self.current_position
            self.out_label.setText(f"{self.t('labels.out_point', 'Out')}: {self.format_time(self.out_point)}")
            self.statusBar().showMessage(f"{self.t('status.end_marked', 'End marked at')} {self.format_time(self.out_point)}")

    def reset_markers(self):
        """Reset in/out markers."""
        if self.video_loaded:
            self.in_point = 0
            duration = self.clipper.get_duration()
            self.out_point = duration
            self.in_label.setText(f"{self.t('labels.in_point', 'In')}: 00:00")
            self.out_label.setText(f"{self.t('labels.out_point', 'Out')}: {self.format_time(duration)}")
            self.statusBar().showMessage(self.t('status.markers_reset', 'Markers reset'))

    def export_clip(self):
        """Export the trimmed clip."""
        if not self.video_loaded:
            return

        if self.out_point <= self.in_point:
            QMessageBox.warning(
                self,
                self.t('dialogs.invalid_range', 'Invalid Range'),
                self.t('dialogs.invalid_range_msg', 'End point must be after start point!')
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.t('dialogs.export_title', 'Export Clip'),
            "",
            "MP4 Video (*.mp4);;All Files (*)"
        )

        if filename:
            self.statusBar().showMessage(self.t('status.exporting', 'Exporting clip...'))
            self.export_btn.setEnabled(False)

            success, message = self.clipper.export_clip(
                filename,
                self.in_point,
                self.out_point
            )

            self.export_btn.setEnabled(True)

            if success:
                QMessageBox.information(
                    self,
                    self.t('dialogs.export_complete', 'Export Complete'),
                    f"{self.t('dialogs.export_success', 'Clip exported successfully!')}\n\n{filename}"
                )
                self.statusBar().showMessage(self.t('status.export_complete', 'Export complete!'))
            else:
                QMessageBox.warning(
                    self,
                    self.t('dialogs.export_failed', 'Export Failed'),
                    f"{self.t('dialogs.failed_msg', 'Failed to export clip:')}\n{message}"
                )
                self.statusBar().showMessage(self.t('status.export_failed', 'Export failed'))

    def format_time(self, seconds):
        """Format seconds as MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            self.t('about.title', 'About LocalClip'),
            f"""<h2>{self.t('app.name', 'LocalClip')}</h2>
            <p><b>{self.t('app.tagline', 'Simple. Local. Yours.')}</b></p>
            <p>Version {self.t('app.version', '0.1.0')}</p>
            <p>{self.t('about.description', 'A lightweight video trimming tool for creators.')}</p>
            <p>{self.t('about.features', 'No cloud uploads. No watermarks. No limits.')}</p>
            <br>
            <p><i>{self.t('about.signature', 'Baperebup!')} ✨</i></p>
            <p>{self.t('about.license', 'Licensed under MIT License')}</p>
            """
        )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key_I:
            self.mark_in()
        elif event.key() == Qt.Key_O:
            self.mark_out()
