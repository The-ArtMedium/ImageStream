"""
Video clipper core functionality for LocalClip.
Handles video loading, trimming, and exporting.
"""

from moviepy.editor import VideoFileClip
from pathlib import Path
import time
import subprocess

try:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BINARY = "ffmpeg"  # fall back to a system install on PATH


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

    def export_clip(self, output_path, start_time, end_time, lossless=True,
                   codec='libx264', audio_codec='aac',
                   bitrate='5000k', preset='medium'):
        """Export a trimmed clip.

        By default this does a lossless stream copy — no re-encoding,
        no quality loss, near-instant regardless of clip length. The
        cut points snap to the nearest keyframe, so start/end may shift
        by up to a second or two depending on the source. Pass
        lossless=False for frame-exact cuts, which re-encodes instead.

        Args:
            output_path: Where to save the clip
            start_time: Start time in seconds
            end_time: End time in seconds
            lossless: If True (default), stream-copy without re-encoding.
                      If False, re-encode for frame-exact cuts.
            codec: Video codec (only used when lossless=False)
            audio_codec: Audio codec (only used when lossless=False)
            bitrate: Video bitrate (only used when lossless=False)
            preset: Encoding preset (only used when lossless=False)

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.clip or not self.source_file:
            return False, "No video loaded"

        if end_time <= start_time:
            return False, "End time must be after start time"

        if start_time < 0 or end_time > self.duration:
            return False, "Invalid time range"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        clip_duration = end_time - start_time

        print("\n" + "=" * 50)
        print("LocalClip - Exporting Clip")
        print("=" * 50)
        start_export = time.time()

        if lossless:
            print(f"Clip duration: {clip_duration:.2f}s")
            print(f"Output: {output_path}")
            print("Mode: lossless (stream copy, no re-encoding)")
            print()

            cmd = [
                FFMPEG_BINARY, "-y",
                "-ss", str(start_time),
                "-i", str(self.source_file),
                "-t", str(clip_duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                str(output_path),
            ]

            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=120
                )
                if result.returncode != 0 or not output_path.exists():
                    print("Lossless copy failed, falling back to re-encode.")
                    print(result.stderr[-800:] if result.stderr else "")
                    return self._export_reencode(
                        output_path, start_time, end_time,
                        codec, audio_codec, bitrate, preset, start_export
                    )
            except Exception as e:
                print(f"Lossless copy error: {e}. Falling back to re-encode.")
                return self._export_reencode(
                    output_path, start_time, end_time,
                    codec, audio_codec, bitrate, preset, start_export
                )

            elapsed = time.time() - start_export
            print(f"\nExport Complete! ({elapsed:.1f}s, lossless)")
            print(f"Saved: {output_path}")
            print("=" * 50 + "\n")
            return True, f"Clip exported successfully to {output_path}"

        return self._export_reencode(
            output_path, start_time, end_time,
            codec, audio_codec, bitrate, preset, start_export
        )

    def _export_reencode(self, output_path, start_time, end_time,
                          codec, audio_codec, bitrate, preset, start_export):
        """Frame-exact export via re-encoding (the old default behavior)."""
        try:
            trimmed = self.clip.subclip(start_time, end_time)
            print(f"Clip duration: {end_time - start_time:.2f}s")
            print(f"Output: {output_path}")
            print(f"Mode: frame-exact (re-encode, {codec} @ {bitrate})")
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
            minutes, seconds = int(elapsed // 60), int(elapsed % 60)
            print(f"\nExport Complete! Time: {minutes}m {seconds}s")
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
                       
