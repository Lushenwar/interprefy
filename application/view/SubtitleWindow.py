"""
================================================================================
 SubtitleWindow - Floating Overlay for Displaying Translated Subtitles
================================================================================

This class is responsible for:
    - Creating a transparent, always-on-top subtitle display window using PyQt5.
    - Periodically reading a text history file for updated translated lines.
    - Displaying new subtitle lines on the screen as they become available.
    - Automatically adjusting the size and position of the overlay window.

Features:
    - Frameless, translucent UI with styled text for readability.
    - Monitors the latest file in the 'history' folder for real-time updates.
    - Only displays every second line (assuming translated lines follow source).
    - Designed to integrate with systems producing translation output to file.

Dependencies:
    - PyQt5 for UI components and timers.
    - Standard Python libraries for file handling and datetime.

Note: This window is presentation-only and does not handle audio capture or translation.
"""


import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QDesktopWidget, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class SubtitleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)

        self.label = QLabel("Waiting for subtitles...")
        self._setup_label(self.label)
        self.layout.addWidget(self.label)

        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 10px;")
        self.adjust_size_and_position()

        # History setup
        self.history_folder = "history"
        os.makedirs(self.history_folder, exist_ok=True)

        self.history_path = self.get_latest_history_file()
        self.translated_lines = []
        self.current_index = 0
        self.line_count = 0  # Total lines tracked so far

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.check_for_updates)
        self.poll_timer.start(1000)  # Check every 1 second

    def _setup_label(self, label: QLabel):
        label.setFont(QFont("Arial", 20))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 28px; padding: 10px;")

    def get_latest_history_file(self):
        files = [f for f in os.listdir(self.history_folder) if f.endswith(".txt")]
        if not files:
            # Create a dummy file to track
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            path = os.path.join(self.history_folder, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            return path

        latest = max(files, key=lambda f: os.path.getmtime(os.path.join(self.history_folder, f)))
        return os.path.join(self.history_folder, latest)

    def check_for_updates(self):
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print("Error reading file:", e)
            return

        # Check if new lines were added
        if len(lines) > self.line_count:
            new_lines = lines[self.line_count:]
            self.line_count = len(lines)

            # Translated lines are every other one starting at index 1
            for i in range(1, len(new_lines), 2):
                self.translated_lines.append(new_lines[i])

            self.display_next()

    def display_next(self):
        if self.current_index < len(self.translated_lines):
            text = self.translated_lines[self.current_index]
            self.layout.removeWidget(self.label)
            self.label.deleteLater()

            self.label = QLabel(text)
            self._setup_label(self.label)
            self.layout.addWidget(self.label)

            self.adjust_size_and_position()
            self.repaint()
            QApplication.processEvents()

            self.current_index += 1

    def adjust_size_and_position(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width(), 80)
        self.move(0, screen.height() - 145)

