"""
Video/Image background layer (Layer 1).
Handles video clips and static images as the foundation.
"""

from pathlib import Path
from moviepy.editor import VideoFileClip, ImageClip


class VideoLayer:
    """Manages the video/image background layer."""
    
    def __init__(self):
        self.clip = None
        self.source_file = None
        self.duration = 0
    
    def load_video(self, filepath):
        """Load a video file.
        
        Args:
            filepath: Path to video file
        
        Returns:
            bool: True if successful
        """
        try:
            self.clip = VideoFileClip(filepath)
            self.source_file = filepath
            self.duration = self.clip.duration
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False
    
    def load_image(self, filepath, duration=10):
        """Load an image file as a clip.
        
        Args:
            filepath: Path to image file
            duration: How long to display the image (seconds)
        
        Returns:
            bool: True if successful
        """
        try:
            self.clip = ImageClip(filepath).set_duration(duration)
            self.source_file = filepath
            self.duration = duration
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def load(self, filepath, duration=10):
        """Load either video or image based on file type.
        
        Args:
            filepath: Path to file
            duration: Duration for images (ignored for videos)
        
        Returns:
            bool: True if successful
        """
        path = Path(filepath)
        ext = path.suffix.lower()
        
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        if ext in video_exts:
            return self.load_video(filepath)
        elif ext in image_exts:
            return self.load_image(filepath, duration)
        else:
            print(f"Unsupported file type: {ext}")
            return False
    
    def get_clip(self):
        """Get the moviepy clip object.
        
        Returns:
            VideoClip or ImageClip or None
        """
        return self.clip
    
    def get_duration(self):
        """Get the duration of the clip.
        
        Returns:
            float: Duration in seconds
        """
        return self.duration
    
    def clear(self):
        """Clear the layer."""
        if self.clip:
            self.clip.close()
        self.clip = None
        self.source_file = None
        self.duration = 0
