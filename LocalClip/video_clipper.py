"""
Video clipper core functionality for LocalClip.
Handles video loading, trimming, and exporting.
"""

from moviepy.editor import VideoFileClip
from pathlib import Path
import time


class VideoClipper:
    """Handles video trimming operations."""

    def __init__(self):
        """Initialize the video clipper."""
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
            if self.clip:
                self.clip.close()

            self.clip = VideoFileClip(filepath)
            self.source_file = filepath
            self.duration = self.clip.duration
            print(f"Loaded video: {Path(filepath).name}")
            print(f"Duration: {self.duration:.2f}s")
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def get_duration(self):
        """Get the duration of the loaded video.

        Returns:
            float: Duration in seconds
        """
        return self.duration

    def export_clip(self, output_path, start_time, end_time, 
                   codec='libx264', audio_codec='aac', 
                   bitrate='5000k', preset='medium'):
        """Export a trimmed clip.

        Args:
            output_path: Where to save the clip
            start_time: Start time in seconds
            end_time: End time in seconds
            codec: Video codec
            audio_codec: Audio codec
            bitrate: Video bitrate
            preset: Encoding preset

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.clip:
            return False, "No video loaded"

        if end_time <= start_time:
            return False, "End time must be after start time"

        if start_time < 0 or end_time > self.duration:
            return False, "Invalid time range"

        try:
            print("\n" + "=" * 50)
            print("LocalClip - Exporting Clip")
            print("=" * 50)
            start_export = time.time()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            trimmed = self.clip.subclip(start_time, end_time)

            clip_duration = end_time - start_time
            print(f"Clip duration: {clip_duration:.2f}s")
            print(f"Output: {output_path}")
            print(f"Codec: {codec}")
            print(f"Bitrate: {bitrate}")
            print(f"Preset: {preset}")
            print()

            trimmed.write_videofile(
                str(output_path),
                codec=codec,
                audio_codec=audio_codec,
                bitrate=bitrate,
                preset=preset,
                verbose=True,
                logger='bar'
            )

            trimmed.close()

            elapsed = time.time() - start_export
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)

            print("\n" + "=" * 50)
            print("Export Complete!")
            print(f"Time: {minutes}m {seconds}s")
            print(f"Saved: {output_path}")
            print("=" * 50 + "\n")

            return True, f"Clip exported successfully to {output_path}"

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            print(f"\nERROR: {error_msg}\n")
            return False, error_msg

    def close(self):
        """Close the video clip and free resources."""
        if self.clip:
            self.clip.close()
            self.clip = None
            self.source_file = None
            self.duration = 0
