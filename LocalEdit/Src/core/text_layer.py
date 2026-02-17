"""
Text caption layer (Layer 3).
Handles text overlays with styling and positioning.
"""

from moviepy.editor import TextClip


class TextLayer:
    """Manages the text caption layer."""
    
    def __init__(self):
        self.text_clips = []
    
    def add_text(self, text, position=('center', 'bottom'), 
                 start_time=0, duration=5,
                 fontsize=48, color='white', font='Arial',
                 bg_color=None, stroke_color=None, stroke_width=0):
        """Add a text caption.
        
        Args:
            text: The text to display
            position: Position tuple or string ('center', 'top', etc.)
            start_time: When to start showing (seconds)
            duration: How long to show (seconds)
            fontsize: Font size
            color: Text color
            font: Font name
            bg_color: Background color (None for transparent)
            stroke_color: Outline color
            stroke_width: Outline width
        
        Returns:
            bool: True if successful
        """
        try:
            clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font,
                bg_color=bg_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width
            )
            
            clip = clip.set_duration(duration)
            clip = clip.set_start(start_time)
            clip = clip.set_position(position)
            
            self.text_clips.append({
                'clip': clip,
                'text': text,
                'position': position,
                'start_time': start_time,
                'duration': duration,
                'style': {
                    'fontsize': fontsize,
                    'color': color,
                    'font': font,
                    'bg_color': bg_color,
                    'stroke_color': stroke_color,
                    'stroke_width': stroke_width
                }
            })
            return True
        except Exception as e:
            print(f"Error adding text: {e}")
            return False
    
    def get_text_clips(self):
        """Get all text clips.
        
        Returns:
            list: List of moviepy text clips
        """
        return [text['clip'] for text in self.text_clips]
    
    def clear(self):
        """Clear all text clips."""
        for text in self.text_clips:
            text['clip'].close()
        self.text_clips = []
    
    def remove_text(self, index):
        """Remove a specific text clip.
        
        Args:
            index: Index of text to remove
        """
        if 0 <= index < len(self.text_clips):
            self.text_clips[index]['clip'].close()
            self.text_clips.pop(index)
