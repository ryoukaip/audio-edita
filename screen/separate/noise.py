import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout, QApplication, QLabel
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QTimer, QUrl
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow
from screen.separate.worker_noise import NoiseWorker
from screen.function.system.system_thememanager import ThemeManager

class NoisePage(QWidget):
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

        # Top bar
        layout.addLayout(FunctionBar("noise reduction", font_family, self))
        layout.addSpacing(10)

        # Player layout for Before and After
        player_layout = QHBoxLayout()

        # Before player (draggable)
        before_layout = QVBoxLayout()
        self.audio_player_before = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player_before.setFixedHeight(220)
        self.audio_player_before.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player_before.file_dropped.connect(self.on_file_dropped)
        before_label = self._create_label("before", font_family)
        before_layout.addWidget(self.audio_player_before)
        before_layout.addWidget(before_label)

        player_layout.addLayout(before_layout)
        player_layout.addSpacing(10)

        # After player (non-draggable)
        after_layout = QVBoxLayout()
        self.audio_player_after = DropAreaLabel(self.audio_data_manager, allow_drop=False)
        self.audio_player_after.setFixedHeight(220)
        self.audio_player_after.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        after_label = self._create_label("after", font_family)
        after_layout.addWidget(self.audio_player_after)
        after_layout.addWidget(after_label)

        player_layout.addLayout(after_layout)
        layout.addLayout(player_layout)
        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_location_btn = self._create_button("Open file location", font_family, 180, self.open_file_location)
        button_layout.addWidget(self.open_location_btn)
        button_layout.addSpacing(10)

        self.export_btn = self._create_button("Export", font_family, 100, self.export_audio)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)
        self.setStyleSheet("background-color: #282a32;")

    def _create_label(self, text, font_family):
        """Helper method to create a styled label"""
        label = QLabel(text)
        label.setFont(QFont(font_family, 12))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _create_button(self, text, font_family, width, callback):
        """Helper method to create a styled button"""
        btn = QPushButton(text)
        btn.setFixedSize(width, 40)
        btn.setFont(QFont(font_family, 13))
        btn.setStyleSheet(self.get_button_stylesheet())
        btn.clicked.connect(callback)
        return btn

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

    def update_colors(self, colors):
        """Cập nhật màu sắc của các nút khi theme thay đổi"""
        self.current_colors = colors
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.export_btn.setStyleSheet(self.get_button_stylesheet())

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def export_audio(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        print(f"Starting export for file: {self.selected_audio_file}")

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

        self.worker = NoiseWorker(self.selected_audio_file, True)
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
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)

        self.audio_player_after.set_audio_file(output_file)
        self.audio_data_manager.set_audio_file(output_file)
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "noise")
        os.makedirs(output_dir, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)