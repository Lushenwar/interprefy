"""
================================================================================
 AppController - Core Application Logic and Interaction Handler for Interprefy
================================================================================

Coordinates interactions between the UI, transcription, and translation systems.

This class is responsible for:
    - Managing application state (e.g., recording status, user preferences).
    - Connecting UI events from the MainFrame to the appropriate logic.
    - Initializing and controlling Transcriber and Translator components.
    - Handling language/theme changes and updating ProfileSettings accordingly.
    - Displaying translated subtitles in the floating SubtitleWindow.

Dependencies:
    - PyQt5 for UI signals and widgets.
    - Model components: ProfileSettings, Language, Theme, Translator, Transcriber.
    - View components: MainFrame and SubtitleWindow.

Note: This is the central controller for orchestrating the application's workflow.
"""


import os
from datetime import datetime

from model.ProfileSettings import ProfileSettings
from model.Language import Language
from model.Theme import Theme
from model.Translator import Translator
from model.Transcriber import Transcriber
from PyQt5.QtWidgets import QPushButton
from view.MainFrame import MainFrame
from view.SubtitleWindow import SubtitleWindow

class AppController:
    def __init__(self, view: MainFrame):
        self.view = view
        self.transcriber = None
        self.translator = None
        self.is_recording = False

        self.profile_settings = ProfileSettings()

        self.connect_signals()

    def connect_signals(self):
        self.view.home_btn.clicked.connect(self.view.set_home_view)
        self.view.settings_btn.clicked.connect(self.view.set_settings_view)
        self.view.play_btn.clicked.connect(self.on_play_clicked)

        for btn in self.view.topic_buttons:
            if isinstance(btn, QPushButton):
                btn.clicked.connect(lambda _, b=btn: self.on_topic_clicked(b.text()))

        self.view.language_changed.connect(self.on_language_changed)
        self.view.theme_changed.connect(self.on_theme_changed)

    def on_language_changed(self, lang_label):
        for lang in Language:
            if lang.label == lang_label:
                self.profile_settings.translated_language = lang
                print(f"[Settings] Translated language set to: {lang.label} ({lang.code})")
                break

    def on_theme_changed(self, theme_label):
        for theme in Theme:
            if theme.value == theme_label:
                self.profile_settings.theme = theme
                print(f"[Settings] Theme set to: {theme.value}")
                break

    def on_play_clicked(self):
        if not self.is_recording:
            print("🔊 Starting system audio transcription & translation...")
            try:
                deepgram_api_key = "7c6607da70f74e271198980712b8de0ac24b58f5"  # Remove for production
                self.translator = Translator(self.profile_settings)

                self.transcriber = Transcriber(
                    api_key=deepgram_api_key,
                    language=self.profile_settings.source_language.code,
                    on_transcript=self.handle_transcription,
                    profile_settings=self.profile_settings
                )
                self.transcriber.start()

                self.subtitle_window = SubtitleWindow()
                self.subtitle_window.show()
                self.view.set_subtitle_window(self.subtitle_window)

                self.is_recording = True
                self.view.play_btn.setText("Stop")
            except RuntimeError as e:
                print(f"❌ Error: {e}")
                self.view.play_btn.setText("Play")
        else:
            print("Stopping audio capture...")
            if self.transcriber:
                self.transcriber.stop()
            self.is_recording = False
            self.view.play_btn.setText("Play")
            self.view.subtitle_window.label.setHidden(True)

    def handle_transcription(self, original, translated):
        print(f"[Original] {original}")
        print(f"[Translated] → {translated}\n")

        if self.subtitle_window:
            self.subtitle_window.append_line(original, translated)


    def on_topic_clicked(self, topic_name):
        print(f"Topic selected: {topic_name}")

    
