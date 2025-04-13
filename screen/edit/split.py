import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow
from screen.edit.worker_split import SplitWorker
from screen.function.system.system_thememanager import ThemeManager

class SplitPage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager
        self.selected_audio_file = None
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_colors)
        
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("split", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Trình phát input (cho phép thả và chia sẻ)
        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        self.audio_player.time_updated.connect(self.update_split_time)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)
        
        split_label = QLabel("split this audio at")
        split_label.setFont(QFont(font_family, 13))
        split_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(split_label, alignment=Qt.AlignCenter)

        self.time_label = QLabel("00:00")
        self.time_label.setFont(QFont(font_family, 13, QFont.Bold))
        self.time_label.setStyleSheet(self.get_time_label_stylesheet())
        layout.addWidget(self.time_label, alignment=Qt.AlignCenter)
        
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
        self.export_btn.clicked.connect(self.show_output_widget)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)
        self.setStyleSheet("background-color: #282a32;")

        # Tải tệp âm thanh từ AudioDataManager khi khởi tạo
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

    def get_time_label_stylesheet(self):
        """Tạo stylesheet cho ô thời gian dựa trên theme hiện tại"""
        return f"""
            QLabel {{
                color: white;
                background-color: {self.current_colors['background']};
                border-radius: 18px;
                padding: 6px 10px;
            }}
        """

    def update_colors(self, colors):
        """Cập nhật màu sắc của các nút và ô thời gian khi theme thay đổi"""
        self.current_colors = colors
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.export_btn.setStyleSheet(self.get_button_stylesheet())
        self.time_label.setStyleSheet(self.get_time_label_stylesheet())

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path
        # Tệp sẽ tự động được lưu vào AudioDataManager trong DropAreaLabel

    def update_split_time(self, time_str):
        self.time_label.setText(time_str)

    def show_output_widget(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        # Dừng phát âm thanh nếu đang phát
        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            print("Audio paused before export")

        # Lấy thời gian hiện tại từ time_label
        time_str = self.time_label.text()
        try:
            minutes, seconds = map(int, time_str.split(":"))
            split_time = minutes * 60 + seconds
        except ValueError:
            noti_window = NotiWindow()
            noti_window.update_message("Invalid time format!")
            return

        # Hiển thị cửa sổ render
        self.render_window = RenderWindow(None)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = self.audio_player.screen().geometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        # Tạo worker thread
        self.worker = SplitWorker(self.selected_audio_file, split_time)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file1, output_file2):
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        print(f"Files exported successfully: {output_file1}, {output_file2}")
        
        # Lấy tệp âm thanh đầu tiên (output_file1) để hiển thị và chia sẻ
        self.audio_player.set_audio_file(output_file1)
        self.audio_data_manager.set_audio_file(output_file1)  # Cập nhật AudioDataManager

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "split")
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