"""
Image overlay layer (Layer 2).
Handles transparent images, logos, graphics with blend modes.
"""

from pathlib import Path
from moviepy.editor import ImageClip


class ImageLayer:
    """Manages the image overlay layer."""
    
    def __init__(self):
        self.overlays = []
    
    def add_overlay(self, filepath, position=(0, 0), duration=None, opacity=1.0):
        """Add an image overlay.
        
        Args:
            filepath: Path to image file
            position: (x, y) tuple for position
            duration: How long to show (None = full duration)
            opacity: 0.0 to 1.0
        
        Returns:
            bool: True if successful
        """
        try:
            clip = ImageClip(filepath)
            
            if duration:
                clip = clip.set_duration(duration)
            
            clip = clip.set_position(position)
            clip = clip.set_opacity(opacity)
            
            self.overlays.append({
                'clip': clip,
                'filepath': filepath,
                'position': position,
                'duration': duration,
                'opacity': opacity
            })
            return True
        except Exception as e:
            print(f"Error adding overlay: {e}")
            return False
    
    def get_overlays(self):
        """Get all overlay clips.
        
        Returns:
            list: List of moviepy clips
        """
        return [overlay['clip'] for overlay in self.overlays]
    
    def clear(self):
        """Clear all overlays."""
        for overlay in self.overlays:
            overlay['clip'].close()
        self.overlays = []
    
    def remove_overlay(self, index):
        """Remove a specific overlay.
        
        Args:
            index: Index of overlay to remove
        """
        if 0 <= index < len(self.overlays):
            self.overlays[index]['clip'].close()
            self.overlays.pop(index)
