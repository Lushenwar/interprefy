"""
================================================================================
 ProfileSettings - User Preferences for Interprefy
================================================================================

Stores and manages user profile settings, including selected source language,
translated language, and UI theme. Used throughout the application to
customize the user experience.
"""

from model.Language import Language
from model.Theme import Theme

class ProfileSettings:
    """
    Stores and manages user profile settings for Interprefy.
    Provides properties and type checking for language and theme preferences.
    """
    def __init__(self, translated_language=Language.ENGLISH, theme=Theme.DEFAULT, source_language=Language.ENGLISH):
        # Initialize with default or provided settings
        self._translated_language = translated_language
        self._theme = theme
        self._source_language = source_language

    @property
    def translated_language(self):
        # The language to translate to (Language enum)
        return self._translated_language

    @translated_language.setter
    def translated_language(self, value):
        if not isinstance(value, Language):
            raise ValueError("translated_language must be a Language enum value")
        self._translated_language = value

    @property
    def theme(self):
        # The selected UI theme (Theme enum)
        return self._theme

    @theme.setter
    def theme(self, value):
        if not isinstance(value, Theme):
            raise ValueError("theme must be a Theme enum value")
        self._theme = value

    @property
    def source_language(self):
        # The language to transcribe from (Language enum)
        return self._source_language

    @source_language.setter
    def source_language(self, value):
        if not isinstance(value, Language):
            raise ValueError("source_language must be a Language enum value")
        self._source_language = value