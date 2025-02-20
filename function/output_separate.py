import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QVBoxLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase


class OutputSeparateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Create tracks container widget
        tracks_widget = QWidget()
        tracks_layout = QVBoxLayout(tracks_widget)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(10)

        # Create multiple rows of separated tracks
        for _ in range(5):  # Example: 5 tracks
            track_layout = QHBoxLayout()
            track_layout.setContentsMargins(10, 5, 10, 5)
            track_layout.setSpacing(10)

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
            
            # Rounded rectangle
            rect_widget = QWidget()
            rect_widget.setFixedHeight(30)
            rect_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
            rect_widget.setStyleSheet("""
                QWidget {
                    background-color: #7d8bd4;
                    border-radius: 25px;
                }
            """)

            # Play button
            play_button = QPushButton()
            play_button.setFixedSize(30, 30)
            play_button.setIcon(QIcon("./icon/play.png"))
            play_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                }
            """)

            # Add widgets to track layout
            track_layout.addWidget(icon_label)
            track_layout.addWidget(rect_widget)
            track_layout.addWidget(play_button)
            
            # Add track layout to tracks layout
            tracks_layout.addLayout(track_layout)

        tracks_layout.addStretch()
        main_layout.addWidget(tracks_widget)

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
        open_location_btn.clicked.connect(self.open_file_location)

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

    def open_file_location(self):
        # Get documents folder path
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita")
        
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Open the directory
        os.startfile(output_dir)

    def return_to_separate(self):
        # Get main window and switch back to separate page (index 1)
        main_window = self.window()
        main_window.stack.setCurrentIndex(1)