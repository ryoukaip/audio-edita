import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow
from screen.edit.worker_merge import MergeWorker

class MergePage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file1 = None
        self.selected_audio_file2 = None
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("merge", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        player_layout = QHBoxLayout()
        
        self.audio_player1 = DropAreaLabel()
        self.audio_player1.setFixedHeight(220)
        self.audio_player1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player1.file_dropped.connect(self.on_file1_dropped)
        player_layout.addWidget(self.audio_player1)

        player_layout.addSpacing(10)

        self.audio_player2 = DropAreaLabel()
        self.audio_player2.setFixedHeight(220)
        self.audio_player2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player2.file_dropped.connect(self.on_file2_dropped)
        player_layout.addWidget(self.audio_player2)

        layout.addLayout(player_layout)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        self.open_location_btn.clicked.connect(self.open_file_location)
        button_layout.addWidget(self.open_location_btn)

        button_layout.addSpacing(10)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedSize(100, 40)
        self.export_btn.setFont(QFont(font_family, 13))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        self.export_btn.clicked.connect(self.export_audio)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)
        
        self.setStyleSheet("background-color: #282a32;")

    def on_file1_dropped(self, file_path):
        print(f"File 1 dropped: {file_path}")
        self.selected_audio_file1 = file_path

    def on_file2_dropped(self, file_path):
        print(f"File 2 dropped: {file_path}")
        self.selected_audio_file2 = file_path

    def export_audio(self):
        if not self.selected_audio_file1 or not self.selected_audio_file2:
            noti_window = NotiWindow()
            noti_window.update_message("Please drop two audio files to merge")
            return

        print(f"Starting merge for files: {self.selected_audio_file1} and {self.selected_audio_file2}")
        
        self.render_window = RenderWindow(None)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        self.export_btn.setEnabled(False)

        self.worker = MergeWorker(self.selected_audio_file1, self.selected_audio_file2)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Merge complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Merge failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "merge")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuEdit")
            if page_widget:
                stack.setCurrentWidget(page_widget)