"""
================================================================================
 Interprefy: Real-Time Audio Transcription and Translation Desktop Application

Contributors:
    - Tony Tan
    - Ryan Qi

Project Description:
    Interprefy is a desktop application that captures system audio, transcribes 
    spoken language in real time, translates it into a user-selected language, 
    and displays the translated subtitles in an always-on-top overlay window. 
    The application also logs both the original and translated text for later review.

Notable Features:
    - Real-time system audio capture using VB-CABLE and PyAudio
    - Speech-to-text transcription powered by OpenAI Whisper (via faster-whisper)
    - Automatic language detection and translation using deep-translator (GoogleTranslator)
    - Always-on-top, transparent subtitle overlay window for translated text
    - User profile settings for language and theme preferences
    - History logging of all transcribed and translated text in timestamped files
    - Modular MVC-inspired code structure for maintainability

APIs and Frameworks Used:
    - PyQt5: For the graphical user interface (main window, subtitle overlay, etc.)
    - deepgram: For real-time audio transcription
    - faster-whisper: For fast, accurate speech-to-text transcription
    - deep-translator: For translation (GoogleTranslator or LibreTranslator backend)
    - PyAudio: For capturing system audio via VB-CABLE virtual device

How to Run:
    1. Install all dependencies (see README.txt).
    2. Ensure VB-CABLE is installed and set as the system audio output.
    3. Run Main.py to start the application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from view.MainFrame import MainFrame
from controller.AppController import AppController
from model.ProfileSettings import ProfileSettings

def main():
    # Create the Qt application instance
    app = QApplication(sys.argv)

    # Load or initialize user profile settings
    profile_settings = ProfileSettings()

    # Create the main application window with profile settings
    window = MainFrame(profile_settings=profile_settings)

    # Create the application controller, passing the main window
    controller = AppController(window)

    # Show the main window
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec_())

# Entry point for the application
if __name__ == "__main__":
    main()