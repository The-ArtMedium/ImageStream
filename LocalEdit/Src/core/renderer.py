
"""
Video renderer for LocalEdit.
Combines all 4 layers and exports the final video.
"""

from moviepy.editor import CompositeVideoClip, concatenate_videoclips
from pathlib import Path
import time


class Renderer:
    """Handles the final video rendering process."""
    
    def __init__(self):
        self.video_layer = None
        self.image_layer = None
        self.text_layer = None
        self.audio_layer = None
        self.progress_callback = None
    
    def set_layers(self, video_layer, image_layer, text_layer, audio_layer):
        """Set all the layers for rendering.
        
        Args:
            video_layer: VideoLayer instance
            image_layer: ImageLayer instance
            text_layer: TextLayer instance
            audio_layer: AudioLayer instance
        """
        self.video_layer = video_layer
        self.image_layer = image_layer
        self.text_layer = text_layer
        self.audio_layer = audio_layer
    
    def set_progress_callback(self, callback):
        """Set a callback function for progress updates.
        
        Args:
            callback: Function that takes (current, total) as arguments
        """
        self.progress_callback = callback
    
    def validate_project(self):
        """Check if the project has valid content to render.
        
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if not self.video_layer or not self.video_layer.get_clip():
            return False, "No video/image background found in Layer 1"
        
        # At least one layer should have content
        has_content = (
            self.video_layer.get_clip() is not None or
            (self.image_layer and len(self.image_layer.get_overlays()) > 0) or
            (self.text_layer and len(self.text_layer.get_text_clips()) > 0) or
            (self.audio_layer and len(self.audio_layer.get_audio_clips()) > 0)
        )
        
        if not has_content:
            return False, "Project has no content to render"
        
        return True, ""
    
    def render(self, output_path, fps=24, codec='libx264', audio_codec='aac',
               bitrate='5000k', preset='medium', threads=None):
        """Render the final video.
        
        Args:
            output_path: Where to save the output video
            fps: Frames per second
            codec: Video codec to use
            audio_codec: Audio codec to use
            bitrate: Video bitrate
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
            threads: Number of threads (None = auto)
        
        Returns:
            tuple: (bool, str) - (success, message)
        """
        # Validate project
        valid, error = self.validate_project()
        if not valid:
            return False, error
        
        try:
            print("\n" + "="*50)
            print("LocalEdit - Starting Render")
            print("="*50)
            start_time = time.time()
            
            # Get base video clip
            base_clip = self.video_layer.get_clip()
            duration = self.video_layer.get_duration()
            
            print(f"Base clip duration: {duration:.2f}s")
            print(f"Output: {output_path}")
            
            # Collect all clips to composite
            clips = [base_clip]
            
            # Add image overlays (Layer 2)
            if self.image_layer:
                overlays = self.image_layer.get_overlays()
                if overlays:
                    print(f"Adding {len(overlays)} image overlay(s)")
                    for overlay in overlays:
                        # Match overlay duration to base clip
                        overlay = overlay.set_duration(duration)
                        clips.append(overlay)
            
            # Add text clips (Layer 3)
            if self.text_layer:
                text_clips = self.text_layer.get_text_clips()
                if text_clips:
                    print(f"Adding {len(text_clips)} text caption(s)")
                    clips.extend(text_clips)
            
            # Composite all video layers
            print("\nCompositing video layers...")
            final_video = CompositeVideoClip(clips, size=base_clip.size)
            final_video = final_video.set_duration(duration)
            
            # Add audio (Layer 4)
            if self.audio_layer:
                mixed_audio = self.audio_layer.mix_audio()
                if mixed_audio:
                    print("Adding audio track")
                    # Trim or extend audio to match video duration
                    if mixed_audio.duration > duration:
                        mixed_audio = mixed_audio.subclip(0, duration)
                    final_video = final_video.set_audio(mixed_audio)
            
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Render the final video
            print("\nRendering video...")
            print(f"Codec: {codec}")
            print(f"FPS: {fps}")
            print(f"Bitrate: {bitrate}")
            print(f"Preset: {preset}")
            print()
            
            final_video.write_videofile(
                str(output_path),
                fps=fps,
                codec=codec,
                audio_codec=audio_codec,
                bitrate=bitrate,
                preset=preset,
                threads=threads,
                verbose=True,
                logger='bar'
            )
            
            # Calculate render time
            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            
            print("\n" + "="*50)
            print("Render Complete!")
            print(f"Time: {minutes}m {seconds}s")
            print(f"Output: {output_path}")
            print("="*50 + "\n")
            
            # Cleanup
            final_video.close()
            
            return True, f"Video exported successfully to {output_path}"
            
        except Exception as e:
            error_msg = f"Render failed: {str(e)}"
            print(f"\nERROR: {error_msg}\n")
            return False, error_msg
    
    def quick_render(self, output_path):
        """Quick render with default settings.
        
        Args:
            output_path: Where to save the output
        
        Returns:
            tuple: (bool, str) - (success, message)
        """
        return self.render(
            output_path,
            fps=24,
            preset='medium',
            bitrate='5000k'
        )
    
    def get_project_info(self):
        """Get information about the current project.
        
        Returns:
            dict: Project information
        """
        info = {
            'has_video': self.video_layer and self.video_layer.get_clip() is not None,
            'duration': self.video_layer.get_duration() if self.video_layer else 0,
            'num_overlays': len(self.image_layer.get_overlays()) if self.image_layer else 0,
            'num_text': len(self.text_layer.get_text_clips()) if self.text_layer else 0,
            'num_audio': len(self.audio_layer.get_audio_clips()) if self.audio_layer else 0
        }
        return info
    
    def estimate_render_time(self):
        """Estimate how long the render will take.
        
        Returns:
            str: Estimated time description
        """
        if not self.video_layer:
            return "Unknown"
        
        duration = self.video_layer.get_duration()
        
        # Rough estimate: 1 second of video takes 2-5 seconds to render
        # depending on complexity and hardware
        min_time = duration * 2
        max_time = duration * 5
        
        if min_time < 60:
            return f"{int(min_time)}-{int(max_time)} seconds"
        else:
            min_minutes = int(min_time / 60)
            max_minutes = int(max_time / 60)
            return f"{min_minutes}-{max_minutes} minutes"
