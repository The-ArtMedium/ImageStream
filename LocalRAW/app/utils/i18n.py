"""
Simple translation loader for LocalRAW.
Loads a language JSON file and provides lookup with English fallback.
"""
import json
from pathlib import Path

_TRANSLATIONS_DIR = Path(__file__).parent.parent / "resources" / "translations"
_SUPPORTED = ["en", "es", "fr", "pt", "ar", "hi"]

_cache = {}


def _load(lang_code):
    if lang_code in _cache:
        return _cache[lang_code]
    path = _TRANSLATIONS_DIR / f"{lang_code}.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    _cache[lang_code] = data
    return data


class Translator:
    def __init__(self, lang_code="en"):
        self.lang_code = lang_code if lang_code in _SUPPORTED else "en"
        self.strings = _load(self.lang_code)
        self.fallback = _load("en") if self.lang_code != "en" else self.strings

    def set_language(self, lang_code):
        self.lang_code = lang_code if lang_code in _SUPPORTED else "en"
        self.strings = _load(self.lang_code)
        self.fallback = _load("en") if self.lang_code != "en" else self.strings

    def t(self, key, **kwargs):
        text = self.strings.get(key, self.fallback.get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text
