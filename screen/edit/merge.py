# screen/edit/merge.py
import os
import soundfile as sf
import numpy as np
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow
from screen.edit.worker_merge import MergeWorker
from screen.function.system.system_thememanager import ThemeManager

class MergePage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager  # Thêm AudioDataManager
        self.selected_audio_file_1 = None  # Sửa tên biến cho đồng bộ
        self.selected_audio_file_2 = None  # Sửa tên biến cho đồng bộ
        
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

        top_bar = FunctionBar("merge", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        player_layout = QHBoxLayout()
        
        # Trình phát input 1 (cho phép thả và chia sẻ)
        self.audio_player_1 = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player_1.setFixedHeight(220)
        self.audio_player_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player_1.file_dropped.connect(self.on_file_1_dropped)
        player_layout.addWidget(self.audio_player_1)

        player_layout.addSpacing(10)

        # Trình phát input 2 (cho phép thả)
        self.audio_player_2 = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player_2.setFixedHeight(220)
        self.audio_player_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player_2.file_dropped.connect(self.on_file_2_dropped)
        player_layout.addWidget(self.audio_player_2)

        layout.addLayout(player_layout)
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

        # Tải tệp âm thanh từ AudioDataManager cho trình phát 1 khi khởi tạo
        self.audio_player_1.load_shared_audio()
    
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

    def on_file_1_dropped(self, file_path):
        print(f"File 1 dropped: {file_path}")
        self.selected_audio_file_1 = file_path

    def on_file_2_dropped(self, file_path):
        print(f"File 2 dropped: {file_path}")
        self.selected_audio_file_2 = file_path

    def export_audio(self):
        if not self.selected_audio_file_1 or not self.selected_audio_file_2:
            noti_window = NotiWindow()
            noti_window.update_message("Please drop two audio files to merge")
            return

        print(f"Starting merge for files: {self.selected_audio_file_1} and {self.selected_audio_file_2}")
        
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

        self.worker = MergeWorker(self.selected_audio_file_1, self.selected_audio_file_2)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        print(f"Export finished, output file: {output_file}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Merge complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        # Ghi đè tệp đầu ra vào AudioDataManager và hiển thị trên audio_player_1
        self.audio_player_1.set_audio_file(output_file)
        self.audio_data_manager.set_audio_file(output_file)  # Ghi đè AudioDataManager
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
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)