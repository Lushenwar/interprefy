"""
================================================================================
 Language Enum - Supported Languages for Interprefy
================================================================================

Defines the supported languages for transcription and translation in the Interprefy
application. Each language has a display label and a language code compatible with
the translation API (GoogleTranslator).

Usage:
    Language.ENGLISH.label  # "English"
    Language.ENGLISH.code   # "en"
"""

from enum import Enum

class Language(Enum):
    ENGLISH = ("English", "en")
    SPANISH = ("Spanish", "es")
    FRENCH = ("French", "fr")
    GERMAN = ("German", "de")
    CHINESE = ("Chinese", "zh-cn")
    JAPANESE = ("Japanese", "ja")

    @property
    def label(self):
        """Returns the display label for the language."""
        return self.value[0]

    @property
    def code(self):
        """Returns the language code for translation APIs."""
        return self.value[1]