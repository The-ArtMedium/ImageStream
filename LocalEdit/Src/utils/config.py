"""
Configuration management for LocalEdit.
Handles application settings and preferences.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Application configuration manager."""
    
    DEFAULT_SETTINGS = {
        'language': 'en',
        'theme': 'dark',
        'default_fps': 24,
        'default_resolution': [1920, 1080],
        'default_bitrate': '5000k',
        'export_preset': 'medium',
        'auto_save': True,
        'auto_save_interval': 300,
        'recent_projects': [],
        'max_recent_projects': 10,
        'default_export_path': str(Path.home() / 'Videos' / 'LocalEdit'),
        'show_welcome': True,
        'check_updates': False,
        'telemetry': False,
        'window_geometry': None,
        'timeline_zoom': 1.0
    }
    
    def __init__(self):
        """Initialize configuration."""
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / 'config.json'
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()
    
    def _get_config_directory(self) -> Path:
        """Get the configuration directory path.
        
        Returns:
            Path: Configuration directory
        """
        if Path.home().exists():
            config_dir = Path.home() / '.localedit'
        else:
            config_dir = Path('.localedit')
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load(self) -> bool:
        """Load configuration from file.
        
        Returns:
            bool: True if successful
        """
        if not self.config_file.exists():
            self.save()
            return True
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
            
            self.settings.update(loaded_settings)
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save(self) -> bool:
        """Save configuration to file.
        
        Returns:
            bool: True if successful
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Setting key
            default: Default value if key not found
        
        Returns:
            Any: Setting value
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value.
        
        Args:
            key: Setting key
            value: Setting value
            save: Whether to save immediately
        """
        self.settings[key] = value
        if save:
            self.save()
    
    def reset(self, save: bool = True) -> None:
        """Reset configuration to defaults.
        
        Args:
            save: Whether to save after reset
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        if save:
            self.save()
    
    def add_recent_project(self, filepath: str) -> None:
        """Add a project to recent projects list.
        
        Args:
            filepath: Path to project file
        """
        recent = self.get('recent_projects', [])
        
        if filepath in recent:
            recent.remove(filepath)
        
        recent.insert(0, filepath)
        
        max_recent = self.get('max_recent_projects', 10)
        recent = recent[:max_recent]
        
        self.set('recent_projects', recent)
    
    def get_recent_projects(self) -> list:
        """Get list of recent projects.
        
        Returns:
            list: Recent project file paths
        """
        recent = self.get('recent_projects', [])
        existing = [p for p in recent if Path(p).exists()]
        
        if len(existing) != len(recent):
            self.set('recent_projects', existing)
        
        return existing
    
    def clear_recent_projects(self) -> None:
        """Clear the recent projects list."""
        self.set('recent_projects', [])
    
    def get_language(self) -> str:
        """Get current language setting.
        
        Returns:
            str: Language code
        """
        return self.get('language', 'en')
    
    def set_language(self, language_code: str) -> None:
        """Set the language.
        
        Args:
            language_code: Language code (e.g., 'en', 'es')
        """
        self.set('language', language_code)
    
    def get_export_settings(self) -> Dict:
        """Get export settings.
        
        Returns:
            dict: Export configuration
        """
        return {
            'fps': self.get('default_fps', 24),
            'resolution': self.get('default_resolution', [1920, 1080]),
            'bitrate': self.get('default_bitrate', '5000k'),
            'preset': self.get('export_preset', 'medium')
        }
    
    def set_export_settings(self, fps: int = None, resolution: list = None,
                           bitrate: str = None, preset: str = None) -> None:
        """Set export settings.
        
        Args:
            fps: Frames per second
            resolution: [width, height]
            bitrate: Video bitrate
            preset: Encoding preset
        """
        if fps is not None:
            self.set('default_fps', fps, save=False)
        if resolution is not None:
            self.set('default_resolution', resolution, save=False)
        if bitrate is not None:
            self.set('default_bitrate', bitrate, save=False)
        if preset is not None:
            self.set('export_preset', preset, save=False)
        self.save()


_config_instance = None


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Config: Global configuration
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
