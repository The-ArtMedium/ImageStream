"""
Locale manager for LocalClip.
Handles loading and switching between different languages.
"""

import json
from pathlib import Path
from typing import Dict


class LocaleManager:
    """Manages application localization."""
    
    LANGUAGES = {
        'en': 'English',
        'es': 'Español',
        'pt': 'Português',
        'hi': 'हिन्दी',
        'ar': 'العربية',
        'fr': 'Français'
    }
    
    RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur']
    
    def __init__(self, default_language='en'):
        """Initialize the locale manager."""
        self.current_language = default_language
        self.translations = {}
        self.locales_dir = self._get_locales_directory()
        self.load_language(default_language)
    
    def _get_locales_directory(self) -> Path:
        """Get the path to the locales directory."""
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        return project_root / 'locales'
    
    def load_language(self, language_code: str) -> bool:
        """Load a language file."""
        locale_file = self.locales_dir / f'{language_code}.json'
        
        if not locale_file.exists():
            print(f"Warning: Locale file not found: {locale_file}")
            if language_code != 'en':
                return self.load_language('en')
            return False
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = language_code
            print(f"Loaded language: {self.get_language_name(language_code)}")
            return True
        except Exception as e:
            print(f"Error loading language file: {e}")
            return False
    
    def get(self, key_path: str, default: str = None) -> str:
        """Get a translated string."""
        keys = key_path.split('.')
        value = self.translations
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            if default:
                return default
            return f"[{key_path}]"
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available language codes and names."""
        available = {}
        for code, name in self.LANGUAGES.items():
            locale_file = self.locales_dir / f'{code}.json'
            if locale_file.exists():
                available[code] = name
        return available
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name of a language."""
        return self.LANGUAGES.get(language_code, language_code)
    
    def is_rtl(self, language_code: str = None) -> bool:
        """Check if a language is right-to-left."""
        code = language_code or self.current_language
        return code in self.RTL_LANGUAGES
    
    def switch_language(self, language_code: str) -> bool:
        """Switch to a different language."""
        return self.load_language(language_code)
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language


_locale_manager = None


def get_locale_manager() -> LocaleManager:
    """Get the global locale manager instance."""
    global _locale_manager
    if _locale_manager is None:
        _locale_manager = LocaleManager()
    return _locale_manager


def translate(key_path: str, default: str = None) -> str:
    """Convenience function for translation."""
    return get_locale_manager().get(key_path, default)


t = translate
