from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QWidget)
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer

class RenderWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.smooth_progress)
        self.target_progress = 0
        self.current_progress = 0
        
    def initUI(self):
        # Load custom font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Window setup
        self.setWindowTitle("Rendering")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #1c1b1f;
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Rendering Audio")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title_label)

        # Status label
        self.status_label = QLabel("Processing...")
        self.status_label.setStyleSheet("color: #a0a0a0;")
        main_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #282a32;
                height: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #98a4e6;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Time remaining
        self.time_label = QLabel("Time remaining: calculating...")
        self.time_label.setStyleSheet("color: #a0a0a0;")
        main_layout.addWidget(self.time_label)

        # Buttons container
        button_container = QHBoxLayout()
        button_container.setSpacing(10)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                color: white;
                border: none;
                font-size: 13px;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        self.cancel_button.clicked.connect(self.close)
        
        button_container.addStretch()
        button_container.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_container)

    def updateProgress(self, value):
        """Update the progress bar value with smooth animation"""
        self.target_progress = value
        if not self.progress_timer.isActive():
            self.progress_timer.start(16)
        
    def updateStatus(self, status_text):
        """Update the status label text"""
        self.status_label.setText(status_text)
        
    def updateTimeRemaining(self, time_text):
        """Update the time remaining label"""
        self.time_label.setText(f"Time remaining: {time_text}")

    def smooth_progress(self):
        """Create smooth animation for progress bar"""
        if abs(self.current_progress - self.target_progress) < 0.5:
            self.current_progress = self.target_progress
            self.progress_bar.setValue(int(self.current_progress))
            self.progress_timer.stop()
        else:
            # Move current progress 10% closer to target each step
            self.current_progress += (self.target_progress - self.current_progress) * 0.1
            self.progress_bar.setValue(int(self.current_progress))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()
            