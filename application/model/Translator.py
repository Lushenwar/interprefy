"""
================================================================================
 Translator - Text Translation Handler for Interprefy
================================================================================

Responsible for translating text from one language to another using the Google Translator API.
Translating input text into the target language specified in profile settings.
Automatically detecting the source language using GoogleTranslator.
Handling translation failures gracefully with a fallback to original text.
Encapsulating translation logic to maintain separation from UI and audio logic.

Dependencies:
    - deep_translator.GoogleTranslator
    - ProfileSettings for accessing user language preferences.

"""


from deep_translator import GoogleTranslator
from model.ProfileSettings import ProfileSettings
from model.Language import Language
from view.SubtitleWindow import SubtitleWindow

class Translator:
    def __init__(self, profile_settings):
        self.profile_settings = profile_settings

    def translate(self, text):
        target_lang = self.profile_settings.translated_language.code
        try:
            return GoogleTranslator(target=target_lang, source="auto").translate(text)
        except Exception as e:
            print(f"[Translator Error] {e}")
            return text  # fallback to original if translation fails
