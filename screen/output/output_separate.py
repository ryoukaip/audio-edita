import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QVBoxLayout, QScrollArea)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from screen.function.function_openlocation import open_file_location
from screen.function.function_playaudio import DropAreaLabel
from screen.function.function_scrollarea import CustomScrollArea

class OutputSeparateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Create custom scroll area
        scroll_area = CustomScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create scroll content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        # Create multiple rows of separated tracks
        for _ in range(5):  # Example: 5 tracks
            track_layout = QHBoxLayout()
            track_layout.setContentsMargins(10, 5, 10, 5)
            track_layout.setSpacing(20)

            # Icon
            icon_label = QLabel()
            icon_label.setFixedSize(30, 30)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
            icon = QIcon("./icon/micro.png")
            icon_label.setPixmap(icon.pixmap(30, 30))
            
            # Replace rounded rectangle with audio player
            audio_player = DropAreaLabel()
            audio_player.setFixedHeight(150)  
            audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            track_layout.addWidget(icon_label)
            track_layout.addWidget(audio_player)
            scroll_layout.addLayout(track_layout)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

        # Add buttons
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Open file location button
        open_location_btn = QPushButton("Open file location")
        open_location_btn.setFixedSize(180, 40)
        open_location_btn.setFont(QFont(font_family, 13))
        open_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #474f7a;
                border-radius: 12px;
                color: white;
            }
            QPushButton:pressed {
                background-color: #7d8bd4;
            }
        """)
        open_location_btn.clicked.connect(open_file_location)

        # Add Back button
        done_btn = QPushButton("Back")
        done_btn.setFixedSize(100, 40)
        done_btn.setFont(QFont(font_family, 13))
        done_btn.setStyleSheet("""
            QPushButton {
                background-color: #474f7a;
                border-radius: 12px;
                color: white;
            }
            QPushButton:pressed {
                background-color: #7d8bd4;
            }
        """)
        done_btn.clicked.connect(self.return_to_separate)

        # Add buttons to layout in correct order
        button_layout.addWidget(open_location_btn)
        button_layout.addSpacing(10)  
        button_layout.addWidget(done_btn)
        main_layout.addLayout(button_layout)

    def return_to_separate(self):
        # Get main window and switch back to separate page (index 1)
        main_window = self.window()
        main_window.stack.setCurrentIndex(1)