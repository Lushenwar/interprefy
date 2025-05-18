"""
================================================================================
 MainFrame - The main window of the Interprefy application
================================================================================

Allows users to select a source language, translated language, and UI theme.
Provides a sidebar for chat history and a content area for chat display and
settings. The sidebar displays chat logs, allowing users to load, rename,
delete, and view chat history. The content area includes a chat display with
bubbles for sent and received messages, as well as a settings area for
language and theme selection. The audio player is located at the bottom of
the window. The MainFrame class is responsible for managing the layout and
interactions of the main window, including the sidebar and content area.


"""


from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QSplitter, QComboBox, QScrollArea, QFrame, QLineEdit, QMessageBox, QInputDialog, QSizePolicy
)
import sys
import os
from datetime import datetime

from model.Language import Language
from model.Theme import Theme
from model.ProfileSettings import ProfileSettings


class MainFrame(QMainWindow):
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, profile_settings=None):
        super().__init__()
        self.profile_settings = profile_settings or ProfileSettings()
        self.setWindowTitle("Interprefy")
        self.setGeometry(100, 100, 1280, 800)
        self.current_log_file = None
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.splitter.setSizes([320, 960])

        # Set theme and language from profile settings
        self.current_theme = self.profile_settings.theme.value
        self.setup_left_sidebar()
        self.setup_right_content()
        self.apply_theme(self.current_theme)
        self.language_combo.setCurrentText(self.profile_settings.translated_language.label)

    def setup_left_sidebar(self):
        self.left_sidebar = QWidget()
        self.left_sidebar.setObjectName("leftSidebar")
        self.left_sidebar.setStyleSheet("""
            #leftSidebar {
                background-color: white;
                border-right: 1px solid #ddd;
            }
        """)
        self.left_layout = QVBoxLayout(self.left_sidebar)
        self.left_layout.setContentsMargins(10, 10, 10, 10)
        self.left_layout.setSpacing(5)

        logo = QLabel("🎧 Interprefy")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.left_layout.addWidget(logo)

        # History header
        history_label = QLabel("History")
        history_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 15px;")
        self.left_layout.addWidget(history_label)

        self.topic_buttons = []

        # Today header
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
        self.left_layout.addWidget(today_label)

        logs_path = "history"
        if os.path.exists(logs_path):
            txt_files = sorted(
                [f for f in os.listdir(logs_path) if f.endswith(".txt")],
                key=lambda f: os.path.getmtime(os.path.join(logs_path, f)),
                reverse=True
            )
            
            # Organize files by date categories
            today_files = []
            yesterday_files = []
            older_files = []
            
            # In a real app, you would categorize the files properly
            # For demonstration, we'll just split the list
            if txt_files:
                third = len(txt_files) // 3
                today_files = txt_files[:third]
                yesterday_files = txt_files[third:third*2]
                older_files = txt_files[third*2:]
            
            # Add today's files
            self.add_file_section(today_files)
            
            # Yesterday header
            yesterday_label = QLabel("Yesterday")
            yesterday_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
            self.left_layout.addWidget(yesterday_label)
            
            # Add yesterday's files
            self.add_file_section(yesterday_files)
            
            # Previous 14 days header
            previous_label = QLabel("Previous 14 days")
            previous_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
            self.left_layout.addWidget(previous_label)
            
            # Add older files
            self.add_file_section(older_files)
            
        else:
            label = QLabel("No logs found.")
            label.setStyleSheet("color: #777; font-size: 14px;")
            self.left_layout.addWidget(label)

        self.left_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.left_sidebar)
        scroll_area.setObjectName("leftScrollArea")
        self.splitter.addWidget(scroll_area)

    def add_file_section(self, files):
        for filename in files:
            base_name = os.path.splitext(filename)[0]
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)

            title_btn = QPushButton(base_name)
            title_btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            title_btn.clicked.connect(lambda checked, f=filename: self.load_log_content(f))

            rename_btn = QPushButton("✏️")
            rename_btn.setFixedWidth(30)
            rename_btn.setStyleSheet("border: none;")
            rename_btn.clicked.connect(lambda checked, f=filename: self.rename_log(f))

            delete_btn = QPushButton("❌")
            delete_btn.setFixedWidth(30)
            delete_btn.setStyleSheet("border: none;")
            delete_btn.clicked.connect(lambda checked, f=filename: self.delete_log(f))

            row_layout.addWidget(title_btn, 1)
            row_layout.addWidget(rename_btn)
            row_layout.addWidget(delete_btn)
            self.left_layout.addWidget(row)
            self.topic_buttons.append(row)

    def setup_right_content(self):
        self.right_content = QWidget()
        self.right_content.setObjectName("rightContent")
        self.right_content.setStyleSheet("""
            #rightContent {
                background-color: #e0e0e0;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_content)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        nav_bar = QWidget()
        nav_bar.setFixedHeight(60)
        nav_bar.setStyleSheet("background-color: #ccc;")
        nav_bar.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav_bar)

        self.home_btn = QPushButton("Home")
        self.settings_btn = QPushButton("Settings")
        for btn in [self.home_btn, self.settings_btn]:
            btn.setCheckable(True)
            btn.setMinimumWidth(120)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 20px;
                    border: none;
                    border-bottom: 3px solid transparent;
                    background-color: transparent;
                    font-size: 16px;
                }
                QPushButton:checked {
                    border-bottom: 3px solid black;
                    font-weight: bold;
                }
            """)
            nav_layout.addWidget(btn)
        self.home_btn.setChecked(True)
        self.home_btn.clicked.connect(self.set_home_view)
        self.settings_btn.clicked.connect(self.set_settings_view)
        
        nav_layout.addStretch()
        self.right_layout.addWidget(nav_bar)

        # Create stack for content
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Home content - Chat display with bubbles
        self.home_content = QWidget()
        self.home_layout = QVBoxLayout(self.home_content)
        self.home_layout.setContentsMargins(10, 10, 10, 10)
        self.home_layout.setSpacing(15)
        self.home_layout.addStretch()  # Push content to the top

        # Settings content
        self.settings_content = QWidget()
        settings_layout = QVBoxLayout(self.settings_content)
        settings_layout.setSpacing(20)
        settings_layout.setAlignment(Qt.AlignCenter)

        # Language selection with larger dropdown
        language_container = QWidget()
        language_layout = QVBoxLayout(language_container)
        language_layout.setAlignment(Qt.AlignCenter)
        
        language_label = QLabel("Dropdown ↓")
        language_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        language_label.setAlignment(Qt.AlignCenter)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([lang.label for lang in Language])
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 1px solid #aaa;
                border-radius: 6px;
                min-width: 300px;
                background: white;
                font-size: 16px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        settings_layout.addWidget(language_container)
        
        # Spacer between dropdowns
        spacer = QWidget()
        spacer.setFixedHeight(40)
        settings_layout.addWidget(spacer)

        # Theme selection with larger dropdown
        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setAlignment(Qt.AlignCenter)
        
        theme_label = QLabel("Themes ↓")
        theme_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        theme_label.setAlignment(Qt.AlignCenter)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([theme.value for theme in Theme])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 1px solid #aaa;
                border-radius: 6px;
                min-width: 300px;
                background: white;
                font-size: 16px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        settings_layout.addWidget(theme_container)

        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        # Add both content widgets to the stack
        self.content_layout.addWidget(self.home_content)
        self.content_layout.addWidget(self.settings_content)
        
        # Set up scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.content_stack)
        scroll_area.setObjectName("contentScrollArea")
        self.right_layout.addWidget(scroll_area)

        # Audio player at the bottom
        self.player = QWidget()
        self.player.setFixedHeight(80)
        self.player.setStyleSheet("background-color: #ccc;")
        self.player.setObjectName("audioPlayer")
        self.player_layout = QHBoxLayout(self.player)

        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 20px;
                font-size: 18px;
            }
        """)
        self.waveform = QLabel("Audio Waveform")
        self.waveform.setStyleSheet("""
            background-color: #333;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)

        self.player_layout.addWidget(self.play_btn)
        self.player_layout.addWidget(self.waveform, 1)
        self.right_layout.addWidget(self.player)

        self.splitter.addWidget(self.right_content)
        self.set_home_view()

    def set_home_view(self):
        self.home_btn.setChecked(True)
        self.settings_btn.setChecked(False)
        self.home_content.show()
        self.settings_content.hide()

    def set_settings_view(self):
        self.settings_btn.setChecked(True)
        self.home_btn.setChecked(False)
        self.settings_content.show()
        self.home_content.hide()

    def _on_language_changed(self, idx):
        lang_label = self.language_combo.currentText()
        self.language_changed.emit(lang_label)

    def _on_theme_changed(self, idx):
        theme_label = self.theme_combo.currentText()
        self.current_theme = theme_label
        self.apply_theme(theme_label)
        self.theme_changed.emit(theme_label)

    def apply_theme(self, theme_name):
        if theme_name == "Dark":
            # Dark theme with deep blues and purples
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #080B38;
                    color: #e0e0ff;
                }
                #leftSidebar {
                    background-color: #36195B;
                    border-right: 1px solid #4A3B65;
                }
                #rightContent {
                    background-color: #133155;
                    border-radius: 24px;
                    margin: 8px;
                }
                #navBar {
                    background-color: #192642;
                    border-top-left-radius: 24px;
                    border-top-right-radius: 24px;
                }
                QPushButton {
                    color: #e0e0ff;
                }
                QPushButton:hover {
                    background-color: #2A3A62;
                }
                QPushButton:checked {
                    border-bottom: 3px solid #6F74DD;
                    color: #8C90E8;
                }
                QLabel {
                    color: #e0e0ff;
                }
                .ChatBubble {
                    background-color: #2A3A62;
                    color: #e0e0ff;
                    border-radius: 22px;
                }
                .ReceivedBubble {
                    background-color: #36195B;
                }
                .SentBubble {
                    background-color: #154680;
                }
                #audioPlayer {
                    background-color: #192642;
                    border-bottom-left-radius: 24px;
                    border-bottom-right-radius: 24px;
                }
                QComboBox {
                    background-color: #36195B;
                    color: #e0e0ff;
                    border: 1px solid #4A3B65;
                }
                QComboBox QAbstractItemView {
                    background-color: #36195B;
                    color: #e0e0ff;
                    selection-background-color: #4A3B65;
                }
                QComboBox::drop-down {
                    background-color: #36195B;
                }
                QScrollBar:vertical {
                    background-color: #133155;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background-color: #36195B;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                }
            """)
            # Update the play button and waveform for dark theme
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6F74DD;
                    color: #e0e0ff;
                    border-radius: 20px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #8C90E8;
                }
            """)
            self.waveform.setStyleSheet("""
                background-color: #2A3A62;
                color: #e0e0ff;
                padding: 10px;
                border-radius: 5px;
            """)
            
        elif theme_name == "Light":
            # Light theme with beige and tan
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #F5F1E6;
                    color: #5D4037;
                }
                #leftSidebar {
                    background-color: #EAE0CC;
                    border-right: 1px solid #D1C5A9;
                }
                #rightContent {
                    background-color: #F0E6D2;
                    border-radius: 24px;
                    margin: 8px;
                }
                #navBar {
                    background-color: #D1C5A9;
                    border-top-left-radius: 24px;
                    border-top-right-radius: 24px;
                }
                QPushButton {
                    color: #5D4037;
                }
                QPushButton:hover {
                    background-color: #E0D4BA;
                }
                QPushButton:checked {
                    border-bottom: 3px solid #A67C52;
                    color: #8C6D5D;
                }
                QLabel {
                    color: #5D4037;
                }
                .ChatBubble {
                    background-color: #E0D4BA;
                    color: #5D4037;
                    border-radius: 22px;
                }
                .ReceivedBubble {
                    background-color: #D1C5A9;
                }
                .SentBubble {
                    background-color: #CBBFAD;
                }
                #audioPlayer {
                    background-color: #D1C5A9;
                    border-bottom-left-radius: 24px;
                    border-bottom-right-radius: 24px;
                }
                QComboBox {
                    background-color: #EAE0CC;
                    color: #5D4037;
                    border: 1px solid #D1C5A9;
                }
                QComboBox QAbstractItemView {
                    background-color: #EAE0CC;
                    color: #5D4037;
                    selection-background-color: #D1C5A9;
                }
                QComboBox::drop-down {
                    background-color: #EAE0CC;
                }
                QScrollBar:vertical {
                    background-color: #F0E6D2;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background-color: #D1C5A9;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                }
            """)
            # Update the play button and waveform for light theme
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #A67C52;
                    color: #F5F1E6;
                    border-radius: 20px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #8C6D5D;
                }
            """)
            self.waveform.setStyleSheet("""
                background-color: #D1C5A9;
                color: #5D4037;
                padding: 10px;
                border-radius: 5px;
            """)
            
        else:  # Default - shades of grey
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f0f0f0;
                    color: #333;
                }
                #leftSidebar {
                    background-color: #e0e0e0;
                    border-right: 1px solid #ccc;
                }
                #rightContent {
                    background-color: #d0d0d0;
                    border-radius: 24px;
                    margin: 8px;
                }
                #navBar {
                    background-color: #c0c0c0;
                    border-top-left-radius: 24px;
                    border-top-right-radius: 24px;
                }
                QPushButton {
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #ccc;
                }
                QPushButton:checked {
                    border-bottom: 3px solid #555;
                    color: #000;
                }
                QLabel {
                    color: #333;
                }
                .ChatBubble {
                    background-color: #bbb;
                    color: #333;
                    border-radius: 22px;
                }
                .ReceivedBubble {
                    background-color: #aaa;
                }
                .SentBubble {
                    background-color: #999;
                }
                #audioPlayer {
                    background-color: #c0c0c0;
                    border-bottom-left-radius: 24px;
                    border-bottom-right-radius: 24px;
                }
                QComboBox {
                    background-color: #e0e0e0;
                    color: #333;
                    border: 1px solid #ccc;
                }
                QComboBox QAbstractItemView {
                    background-color: #e0e0e0;
                    color: #333;
                    selection-background-color: #ccc;
                }
                QComboBox::drop-down {
                    background-color: #e0e0e0;
                }
                QScrollBar:vertical {
                    background-color: #d0d0d0;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background-color: #aaa;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                }
            """)
            # Update the play button and waveform for default theme
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    color: white;
                    border-radius: 20px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #777;
                }
            """)
            self.waveform.setStyleSheet("""
                background-color: #aaa;
                color: #333;
                padding: 10px;
                border-radius: 5px;
            """)

    def set_subtitle_window(self, subtitle_window):
        self.subtitle_window = subtitle_window

    def load_log_content(self, filename):
        try:
            self.current_log_file = filename
            path = os.path.join("history", filename)
            
            # Clear existing chat bubbles
            for i in reversed(range(self.home_layout.count())):
                widget = self.home_layout.itemAt(i).widget()
                if widget is not None and widget != self.home_layout.itemAt(self.home_layout.count()-1).widget():
                    widget.setParent(None)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

                # Remove all widgets except the stretch at the end
                for i in reversed(range(self.home_layout.count())):
                    item = self.home_layout.itemAt(i)
                    widget = item.widget()
                    # Only remove if it's not the stretch (which has no widget)
                    if widget is not None:
                        widget.setParent(None)

                if not content.strip():
                    empty_label = QLabel("(Empty log file)")
                    empty_label.setAlignment(Qt.AlignCenter)
                    self.home_layout.addWidget(empty_label)
                else:
                    lines = content.split('\n')
                    is_sent = True
                    for line in lines:
                        if line.strip():
                            self.add_chat_bubble(line, is_sent)
                            is_sent = not is_sent

                self.set_home_view()
                
            if hasattr(self, "subtitle_window"):
                self.subtitle_window.set_subtitle_file(path)
                
        except Exception as e:
            error_label = QLabel(f"Error loading file: {e}")
            self.home_layout.addWidget(error_label)
            self.set_home_view()

    def add_chat_bubble(self, text, is_sent=False):
        bubble = QWidget()
        bubble_layout = QHBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(0)

        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_label.setMinimumWidth(120)
        
        # Dynamically set max width based on home_content width
        max_width = int(self.home_content.width() * 0.95) if self.home_content.width() > 0 else 900
        text_label.setMaximumWidth(max_width)
        text_label.setStyleSheet("""
            padding: 18px;
            border-radius: 22px;
            font-size: 20px;
            line-height: 1.4;
        """)

        if is_sent:
            bubble_layout.setAlignment(Qt.AlignRight)
            if self.current_theme == "Dark":
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #154680;
                    color: #e0e0ff;
                    border-top-right-radius: 8px;
                """)
            elif self.current_theme == "Light":
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #CBBFAD;
                    color: #5D4037;
                    border-top-right-radius: 8px;
                """)
            else:  # Default
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #999;
                    color: #fff;
                    border-top-right-radius: 8px;
                """)
            text_label.setProperty("class", "ChatBubble SentBubble")
        else:
            bubble_layout.setAlignment(Qt.AlignLeft)
            if self.current_theme == "Dark":
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #36195B;
                    color: #e0e0ff;
                    border-top-left-radius: 8px;
                """)
            elif self.current_theme == "Light":
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #D1C5A9;
                    color: #5D4037;
                    border-top-left-radius: 8px;
                """)
            else:  # Default
                text_label.setStyleSheet(text_label.styleSheet() + """
                    background-color: #aaa;
                    color: #333;
                    border-top-left-radius: 8px;
                """)
            text_label.setProperty("class", "ChatBubble ReceivedBubble")

        bubble_layout.addWidget(text_label)
        self.home_layout.insertWidget(0, bubble)

    def append_to_current_log(self, text):
        if self.current_log_file:
            path = os.path.join("history", self.current_log_file)
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n{text}")
            self.load_log_content(self.current_log_file)
            
            # Add new bubble directly (optimization)
            self.add_chat_bubble(text, True)

    def rename_log(self, filename):
        old_path = os.path.join("history", filename)
        base_name = os.path.splitext(filename)[0]
        new_name, ok = QInputDialog.getText(self, "Rename Chat", "Enter new name:", text=base_name)
        if ok and new_name:
            new_filename = f"{new_name}.txt"
            new_path = os.path.join("history", new_filename)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                QMessageBox.information(self, "Renamed", f"Renamed to {new_name}.")
                self.refresh_sidebar()
                if hasattr(self, "subtitle_window") and self.subtitle_window.subtitle_file == old_path:
                    self.subtitle_window.set_subtitle_file(new_path)
            else:
                QMessageBox.warning(self, "File Exists", f"A log with name '{new_name}' already exists.")

    def delete_log(self, filename):
        reply = QMessageBox.question(
            self,
            "Delete Chat",
            f"Are you sure you want to delete '{filename}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                os.remove(os.path.join("history", filename))
                QMessageBox.information(self, "Deleted", f"'{filename}' has been deleted.")
                self.refresh_sidebar()
                if hasattr(self, "subtitle_window") and os.path.basename(self.subtitle_window.subtitle_file) == filename:
                    self.subtitle_window.set_subtitle_file("")
                remaining = sorted(
                    [f for f in os.listdir("history") if f.endswith(".txt")],
                    key=lambda f: os.path.getmtime(os.path.join("history", f)),
                    reverse=True
                )
                if remaining:
                    self.load_log_content(remaining[0])
                else:
                    new_file = datetime.now().strftime("%b %d, %Y") + ".txt"
                    path = os.path.join("history", new_file)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("")
                    self.load_log_content(new_file)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    def refresh_sidebar(self):
        for btn in self.topic_buttons:
            self.left_layout.removeWidget(btn)
            btn.deleteLater()
        self.topic_buttons.clear()

        # Clear the left sidebar
        while self.left_layout.count() > 1:
            item = self.left_layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        # Add history header
        history_label = QLabel("History")
        history_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 15px;")
        self.left_layout.addWidget(history_label)
        
        # Today header
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
        self.left_layout.addWidget(today_label)

        logs_path = "history"
        if os.path.exists(logs_path):
            txt_files = sorted(
                [f for f in os.listdir(logs_path) if f.endswith(".txt")],
                key=lambda f: os.path.getmtime(os.path.join(logs_path, f)),
                reverse=True
            )
            
            # Organize files by date categories (simplified)
            today_files = []
            yesterday_files = []
            older_files = []
            
            if txt_files:
                third = len(txt_files) // 3
                today_files = txt_files[:third]
                yesterday_files = txt_files[third:third*2]
                older_files = txt_files[third*2:]
            
            # Add today's files
            self.add_file_section(today_files)
            
            # Yesterday header
            yesterday_label = QLabel("Yesterday")
            yesterday_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
            self.left_layout.addWidget(yesterday_label)
            
            # Add yesterday's files
            self.add_file_section(yesterday_files)
            
            # Previous 14 days header
            previous_label = QLabel("Previous 14 days")
            previous_label.setStyleSheet("font-size: 14px; color: #777; margin-top: 10px;")
            self.left_layout.addWidget(previous_label)
            
            # Add older files
            self.add_file_section(older_files)
            
        else:
            label = QLabel("No logs found.")
            label.setStyleSheet("color: #777; font-size: 14px;")
            self.left_layout.addWidget(label)

        self.left_layout.addStretch()
        
        # Reapply current theme after refreshing
        self.apply_theme(self.current_theme)

    def resizeEvent(self, event):
        # Dynamically update bubble widths on resize
        for i in range(self.home_layout.count()):
            widget = self.home_layout.itemAt(i).widget()
            if widget:
                label = widget.findChild(QLabel)
                if label:
                    max_width = int(self.home_content.width() * 0.95)
                    label.setMaximumWidth(max_width)
        super().resizeEvent(event)