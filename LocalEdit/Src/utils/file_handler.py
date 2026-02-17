"""
File handling utilities for LocalEdit.
Manages file operations, validation, and project files.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class FileHandler:
    """Handles file operations for LocalEdit."""
    
    # Supported file types
    VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg']
    PROJECT_EXTENSION = '.lep'  # LocalEdit Project
    
    @staticmethod
    def validate_file_exists(filepath: str) -> bool:
        """Check if a file exists.
        
        Args:
            filepath: Path to file
        
        Returns:
            bool: True if file exists
        """
        return Path(filepath).exists()
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        """Get file extension in lowercase.
        
        Args:
            filepath: Path to file
        
        Returns:
            str: Extension with dot (e.g., '.mp4')
        """
        return Path(filepath).suffix.lower()
    
    @staticmethod
    def is_video_file(filepath: str) -> bool:
        """Check if file is a supported video format.
        
        Args:
            filepath: Path to file
        
        Returns:
            bool: True if video file
        """
        ext = FileHandler.get_file_extension(filepath)
        return ext in FileHandler.VIDEO_EXTENSIONS
    
    @staticmethod
    def is_image_file(filepath: str) -> bool:
        """Check if file is a supported image format.
        
        Args:
            filepath: Path to file
        
        Returns:
            bool: True if image file
        """
        ext = FileHandler.get_file_extension(filepath)
        return ext in FileHandler.IMAGE_EXTENSIONS
    
    @staticmethod
    def is_audio_file(filepath: str) -> bool:
        """Check if file is a supported audio format.
        
        Args:
            filepath: Path to file
        
        Returns:
            bool: True if audio file
        """
        ext = FileHandler.get_file_extension(filepath)
        return ext in FileHandler.AUDIO_EXTENSIONS
    
    @staticmethod
    def get_file_type(filepath: str) -> Optional[str]:
        """Determine the type of media file.
        
        Args:
            filepath: Path to file
        
        Returns:
            str: 'video', 'image', 'audio', or None
        """
        if FileHandler.is_video_file(filepath):
            return 'video'
        elif FileHandler.is_image_file(filepath):
            return 'image'
        elif FileHandler.is_audio_file(filepath):
            return 'audio'
        return None
    
    @staticmethod
    def get_file_size_mb(filepath: str) -> float:
        """Get file size in megabytes.
        
        Args:
            filepath: Path to file
        
        Returns:
            float: Size in MB
        """
        try:
            size_bytes = Path(filepath).stat().st_size
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    @staticmethod
    def save_project(filepath: str, project_data: Dict) -> bool:
        """Save project data to a .lep file.
        
        Args:
            filepath: Where to save the project
            project_data: Dictionary containing project information
        
        Returns:
            bool: True if successful
        """
        try:
            # Ensure .lep extension
            path = Path(filepath)
            if path.suffix != FileHandler.PROJECT_EXTENSION:
                path = path.with_suffix(FileHandler.PROJECT_EXTENSION)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    @staticmethod
    def load_project(filepath: str) -> Optional[Dict]:
        """Load project data from a .lep file.
        
        Args:
            filepath: Path to project file
        
        Returns:
            dict: Project data, or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    @staticmethod
    def create_project_data(video_layer=None, image_layer=None, 
                          text_layer=None, audio_layer=None) -> Dict:
        """Create a project data dictionary.
        
        Args:
            video_layer: Video layer data
            image_layer: Image layer data
            text_layer: Text layer data
            audio_layer: Audio layer data
        
        Returns:
            dict: Structured project data
        """
        return {
            'version': '0.1.0',
            'layers': {
                'video': video_layer or {},
                'image': image_layer or {},
                'text': text_layer or {},
                'audio': audio_layer or {}
            },
            'settings': {
                'fps': 24,
                'resolution': [1920, 1080]
            }
        }
    
    @staticmethod
    def get_supported_formats_filter() -> str:
        """Get file dialog filter string for all supported formats.
        
        Returns:
            str: Filter string for QFileDialog
        """
        video_exts = ' '.join(f'*{ext}' for ext in FileHandler.VIDEO_EXTENSIONS)
        image_exts = ' '.join(f'*{ext}' for ext in FileHandler.IMAGE_EXTENSIONS)
        audio_exts = ' '.join(f'*{ext}' for ext in FileHandler.AUDIO_EXTENSIONS)
        
        return (
            f"All Media ({video_exts} {image_exts} {audio_exts});;"
            f"Video Files ({video_exts});;"
            f"Image Files ({image_exts});;"
            f"Audio Files ({audio_exts});;"
            f"All Files (*)"
        )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename.
        
        Args:
            filename: Original filename
        
        Returns:
            str: Sanitized filename
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def ensure_output_directory(filepath: str) -> bool:
        """Ensure the output directory exists.
        
        Args:
            filepath: Path to output file
        
        Returns:
            bool: True if directory exists or was created
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
