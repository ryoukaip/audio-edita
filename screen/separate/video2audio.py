# screen/separate/video2audio.py
import os
import shutil
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow
from screen.separate.worker_video2audio import VideoToAudioWorker
from screen.function.system.system_thememanager import ThemeManager

class Video2AudioPage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager  # Gán audio_data_manager trước
        self.selected_video_file = None
        self.temp_audio_file = None

        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_button_colors)
        
        self.initUI() 

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("video to audio", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Trình phát input (cho phép thả và chia sẻ)
        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.open_location_btn.clicked.connect(self.open_file_location)
        button_layout.addWidget(self.open_location_btn)

        button_layout.addSpacing(10)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedSize(100, 40)
        self.export_btn.setFont(QFont(font_family, 13))
        self.export_btn.setStyleSheet(self.get_button_stylesheet())
        self.export_btn.clicked.connect(self.export_audio)
        button_layout.addWidget(self.export_btn)
        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #282a32;")
        self.audio_player.load_shared_audio()

    def get_button_stylesheet(self):
        """Tạo stylesheet cho các nút dựa trên theme hiện tại"""
        return f"""
            QPushButton {{
                background-color: {self.current_colors['shadow']};
                border-radius: 12px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.current_colors['dark']};
            }}
        """

    def update_button_colors(self, colors):
        """Cập nhật màu sắc của các nút khi theme thay đổi"""
        self.current_colors = colors
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.export_btn.setStyleSheet(self.get_button_stylesheet())

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_video_file = file_path  # Sửa tên biến cho đúng với video

    def export_audio(self):
        if not self.selected_video_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select a video file first")
            return

        # Dừng phát âm thanh nếu đang phát
        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            logging.debug("Audio paused before export")

        # Tạo đường dẫn đầu ra
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "separate", "video-to-audio")
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.selected_video_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}_audio.mp3")

        # Hiển thị cửa sổ render
        self.render_window = RenderWindow(self)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = self.audio_player.screen().geometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        # Tạo worker thread
        self.worker = VideoToAudioWorker(self.selected_video_file, output_file)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.export_btn.setEnabled(False)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        print(f"Export finished, output file: {output_file}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)

        # Hiển thị tệp âm thanh đầu ra trên audio_player và ghi đè vào AudioDataManager
        self.audio_player.set_audio_file(output_file)
        self.audio_data_manager.set_audio_file(output_file)  # Ghi đè AudioDataManager
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "separate", "video-to-audio")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)