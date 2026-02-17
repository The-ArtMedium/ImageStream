LocalEdit UI Module
Contains all user interface components.
"""

from .main_window import MainWindow

__all__ = ['MainWindow']
Src/ui/main_window.py
"""
Main application window for LocalEdit.
Contains the timeline, preview, and controls.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QSplitter, QMenuBar, QMenu, QAction, QStatusBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from .timeline import Timeline


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.project_data = {
            'video_layer': None,
            'image_layer': None,
            'text_layer': None,
            'audio_layer': None
        }
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("LocalEdit - Simple. Local. Yours.")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Create splitter for preview and timeline
        splitter = QSplitter(Qt.Vertical)
        
        # Preview area (placeholder for now)
        preview_widget = self.create_preview_area()
        splitter.addWidget(preview_widget)
        
        # Timeline
        self.timeline = Timeline()
        splitter.addWidget(self.timeline)
        
        # Set splitter proportions
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Connect signals
        self.connect_signals()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # Export menu
        export_menu = menubar.addMenu("Export")
        
        export_action = QAction("Export to MP4", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_video)
        export_menu.addAction(export_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About LocalEdit", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QHBoxLayout()
        
        # Import buttons
        import_video_btn = QPushButton("📹 Add Video/Image")
        import_video_btn.clicked.connect(self.import_video)
        toolbar.addWidget(import_video_btn)
        
        import_overlay_btn = QPushButton("🖼️ Add Overlay")
        import_overlay_btn.clicked.connect(self.import_overlay)
        toolbar.addWidget(import_overlay_btn)
        
        add_text_btn = QPushButton("📝 Add Text")
        add_text_btn.clicked.connect(self.add_text)
        toolbar.addWidget(add_text_btn)
        
        import_audio_btn = QPushButton("🎵 Add Audio")
        import_audio_btn.clicked.connect(self.import_audio)
        toolbar.addWidget(import_audio_btn)
        
        toolbar.addStretch()
        
        # Export button
        export_btn = QPushButton("💾 Export Video")
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
    
    def connect_signals(self):
        """Connect UI signals to slots."""
        pass
    
    # File operations
    def new_project(self):
        """Create a new project."""
        reply = QMessageBox.question(
            self, 
            "New Project",
            "Create a new project? Unsaved changes will be lost.",
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
            self.statusBar().showMessage("New project created")
    
    def open_project(self):
        """Open an existing project."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "LocalEdit Projects (*.lep);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(f"Opening project: {filename}")
            # TODO: Implement project loading
    
    def save_project(self):
        """Save the current project."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            "LocalEdit Projects (*.lep);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(f"Saving project: {filename}")
            # TODO: Implement project saving
    
    # Import operations
    def import_video(self):
        """Import video or image for Layer 1."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Video/Image",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        )
        if filename:
            self.project_data['video_layer'] = filename
            self.timeline.add_to_layer(1, filename)
            self.statusBar().showMessage(f"Added to Layer 1: {filename}")
    
    def import_overlay(self):
        """Import image overlay for Layer 2."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Image Overlay",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        if filename:
            self.project_data['image_layer'] = filename
            self.timeline.add_to_layer(2, filename)
            self.statusBar().showMessage(f"Added to Layer 2: {filename}")
    
    def add_text(self):
        """Add text to Layer 3."""
        # TODO: Open text editor dialog
        self.statusBar().showMessage("Text editor coming soon!")
    
    def import_audio(self):
        """Import audio for Layer 4."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Audio",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac);;All Files (*)"
        )
        if filename:
            self.project_data['audio_layer'] = filename
            self.timeline.add_to_layer(4, filename)
            self.statusBar().showMessage(f"Added to Layer 4: {filename}")
    
    def export_video(self):
        """Export the final video."""
        if not any(self.project_data.values()):
            QMessageBox.warning(
                self,
                "Nothing to Export",
                "Please add some media to your project first!"
            )
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            "",
            "MP4 Video (*.mp4);;All Files (*)"
        )
        if filename:
            self.statusBar().showMessage(f"Exporting to: {filename}")
            # TODO: Implement actual video rendering
            QMessageBox.information(
                self,
                "Export",
                "Export functionality coming soon!\n\nYour video will be rendered to:\n" + filename
            )
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About LocalEdit",
            """<h2>LocalEdit</h2>
            <p><b>Simple. Local. Yours.</b></p>
            <p>Version 0.1.0</p>
            <p>A lightweight video editor for creators who value ownership and privacy.</p>
            <p>No cloud uploads. No watermarks. No subscriptions.</p>
            <br>
            <p><i>Baperebup!</i> ✨</p>
            <p>Licensed under MIT License</p>
            """
        )
Save as Src/ui/main_window.py
Next: Src/ui/timeline.py?
