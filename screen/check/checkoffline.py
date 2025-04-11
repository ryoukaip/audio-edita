import os
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout, QApplication, QLabel
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow
from screen.check.worker_checkoffline import CheckOfflineWorker  # Đảm bảo import đúng worker

class CheckOfflinePage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file1 = None
        self.selected_audio_file2 = None
        self.initUI()

    def initUI(self):
        # Tải font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        # Thanh chức năng
        top_bar = FunctionBar("check similarity", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Khu vực kéo thả file âm thanh
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
        layout.addSpacing(10)

        # Label hiển thị kết quả
        self.result_label = QLabel("result: n/a")
        self.result_label.setFont(QFont(font_family, 13))
        self.result_label.setStyleSheet("color: white;")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        layout.addStretch()

        # Nút và kết quả
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.compare_btn = QPushButton("Analyze")
        self.compare_btn.setFixedSize(100, 40)
        self.compare_btn.setFont(QFont(font_family, 13))
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        self.compare_btn.clicked.connect(self.compare_audio)
        button_layout.addWidget(self.compare_btn)

        layout.addLayout(button_layout)
        self.setStyleSheet("background-color: #282a32;")

    def on_file1_dropped(self, file_path):
        print(f"File 1 dropped: {file_path}")
        self.selected_audio_file1 = file_path
        self.result_label.setText("result: n/a")  # Reset kết quả

    def on_file2_dropped(self, file_path):
        print(f"File 2 dropped: {file_path}")
        self.selected_audio_file2 = file_path
        self.result_label.setText("result - n/a")  # Reset kết quả

    def compare_audio(self):
        if not self.selected_audio_file1 or not self.selected_audio_file2:
            noti_window = NotiWindow()
            noti_window.update_message("Please drop two audio files to compare")
            return

        print(f"Starting comparison for files: {self.selected_audio_file1} and {self.selected_audio_file2}")

        # Hiển thị cửa sổ tiến trình
        self.render_window = RenderWindow(None)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        self.compare_btn.setEnabled(False)

        # Khởi chạy worker
        self.worker = CheckOfflineWorker(self.selected_audio_file1, self.selected_audio_file2)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_comparison_finished)
        self.worker.error.connect(self.on_comparison_error)
        self.worker.start()  # Bắt đầu luồng worker

    def update_progress(self, progress, status, time_remaining):
        print(f"Progress: {progress}%, Status: {status}, Time remaining: {time_remaining}")
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_comparison_finished(self, similarity):
        print(f"Comparison finished with result: {similarity}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Comparison complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.result_label.setText(f"result - {similarity}")
        QTimer.singleShot(1000, self.render_window.close)
        self.compare_btn.setEnabled(True)

    def on_comparison_error(self, error_message):
        print(f"Comparison error: {error_message}")
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Comparison failed: {error_message}")
        self.compare_btn.setEnabled(True)

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)