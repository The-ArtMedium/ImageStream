"""
Timeline widget for LocalEdit.
Displays and manages the 4-layer editing timeline.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPalette


class TimelineLayer(QFrame):
    """Represents a single layer in the timeline."""
    
    def __init__(self, layer_number, layer_name, color):
        super().__init__()
        self.layer_number = layer_number
        self.layer_name = layer_name
        self.color = color
        self.clips = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the layer UI."""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumHeight(80)
        
        layout = QHBoxLayout(self)
        
        # Layer label
        label_widget = QWidget()
        label_widget.setFixedWidth(150)
        label_layout = QVBoxLayout(label_widget)
        
        name_label = QLabel(f"Layer {self.layer_number}")
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        type_label = QLabel(self.layer_name)
        type_label.setStyleSheet("font-size: 10px; color: #888;")
        
        label_layout.addWidget(name_label)
        label_layout.addWidget(type_label)
        label_layout.addStretch()
        
        layout.addWidget(label_widget)
        
        # Timeline track area
        self.track_area = QWidget()
        self.track_area.setStyleSheet(f"""
            QWidget {{
                background-color: {self.color};
                border: 1px solid #444;
                border-radius: 4px;
            }}
        """)
        self.track_layout = QHBoxLayout(self.track_area)
        self.track_layout.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(self.track_area, stretch=1)
    
    def add_clip(self, filename):
        """Add a clip to this layer."""
        from pathlib import Path
        clip_name = Path(filename).name
        
        clip_widget = QPushButton(clip_name)
        clip_widget.setMinimumWidth(150)
        clip_widget.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        self.track_layout.addWidget(clip_widget)
        self.clips.append({
            'filename': filename,
            'widget': clip_widget
        })
    
    def clear(self):
        """Remove all clips from this layer."""
        for clip in self.clips:
            clip['widget'].deleteLater()
        self.clips = []


class Timeline(QWidget):
    """Main timeline widget containing all 4 layers."""
    
    def __init__(self):
        super().__init__()
        self.layers = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the timeline UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Timeline header
        header = QLabel("Timeline - 4 Layers")
        header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #1e1e1e;
                color: white;
            }
        """)
        layout.addWidget(header)
        
        # Create scroll area for layers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layers_widget = QWidget()
        layers_layout = QVBoxLayout(layers_widget)
        layers_layout.setSpacing(4)
        
        # Create the 4 layers
        layer_configs = [
            (1, "Video/Image Background", "#2c3e50"),
            (2, "Image Overlays", "#16a085"),
            (3, "Text Captions", "#e67e22"),
            (4, "Audio Track", "#8e44ad")
        ]
        
        for layer_num, layer_name, color in layer_configs:
            layer = TimelineLayer(layer_num, layer_name, color)
            self.layers[layer_num] = layer
            layers_layout.addWidget(layer)
        
        layers_layout.addStretch()
        
        scroll.setWidget(layers_widget)
        layout.addWidget(scroll)
        
        # Timeline controls
        controls = self.create_controls()
        layout.addLayout(controls)
    
    def create_controls(self):
        """Create timeline control buttons."""
        controls = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear)
        controls.addWidget(clear_btn)
        
        controls.addStretch()
        
        # Playback controls (placeholder)
        play_btn = QPushButton("▶️ Play")
        play_btn.setEnabled(False)  # Coming soon
        controls.addWidget(play_btn)
        
        pause_btn = QPushButton("⏸️ Pause")
        pause_btn.setEnabled(False)  # Coming soon
        controls.addWidget(pause_btn)
        
        stop_btn = QPushButton("⏹️ Stop")
        stop_btn.setEnabled(False)  # Coming soon
        controls.addWidget(stop_btn)
        
        return controls
    
    def add_to_layer(self, layer_number, filename):
        """Add a file to a specific layer.
        
        Args:
            layer_number: 1-4 (Video, Image, Text, Audio)
            filename: Path to the file
        """
        if layer_number in self.layers:
            self.layers[layer_number].add_clip(filename)
    
    def clear(self):
        """Clear all layers."""
        for layer in self.layers.values():
            layer.clear()
    
    def get_layer_data(self):
        """Get all data from all layers.
        
        Returns:
            dict: Layer data with clips
        """
        data = {}
        for layer_num, layer in self.layers.items():
            data[layer_num] = [clip['filename'] for clip in layer.clips]
        return data
