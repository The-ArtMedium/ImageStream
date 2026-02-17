"""
Audio track layer (Layer 4).
Handles audio files and mixing.
"""

from pathlib import Path
from moviepy.editor import AudioFileClip


class AudioLayer:
    """Manages the audio track layer."""
    
    def __init__(self):
        self.audio_clips = []
    
    def add_audio(self, filepath, start_time=0, volume=1.0):
        """Add an audio file.
        
        Args:
            filepath: Path to audio file
            start_time: When to start the audio (seconds)
            volume: Volume level (0.0 to 1.0+)
        
        Returns:
            bool: True if successful
        """
        try:
            clip = AudioFileClip(filepath)
            clip = clip.set_start(start_time)
            clip = clip.volumex(volume)
            
            self.audio_clips.append({
                'clip': clip,
                'filepath': filepath,
                'start_time': start_time,
                'volume': volume,
                'duration': clip.duration
            })
            return True
        except Exception as e:
            print(f"Error adding audio: {e}")
            return False
    
    def get_audio_clips(self):
        """Get all audio clips.
        
        Returns:
            list: List of moviepy audio clips
        """
        return [audio['clip'] for audio in self.audio_clips]
    
    def mix_audio(self):
        """Mix all audio clips together.
        
        Returns:
            CompositeAudioClip or None
        """
        if not self.audio_clips:
            return None
        
        from moviepy.editor import CompositeAudioClip
        clips = self.get_audio_clips()
        return CompositeAudioClip(clips)
    
    def clear(self):
        """Clear all audio clips."""
        for audio in self.audio_clips:
            audio['clip'].close()
        self.audio_clips = []
    
    def remove_audio(self, index):
        """Remove a specific audio clip.
        
        Args:
            index: Index of audio to remove
        """
        if 0 <= index < len(self.audio_clips):
            self.audio_clips[index]['clip'].close()
            self.audio_clips.pop(index)
