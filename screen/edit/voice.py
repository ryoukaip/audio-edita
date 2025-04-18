import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.edit.worker_voice import VoiceWorker
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow
from screen.function.system.system_thememanager import ThemeManager

class VoicePage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager 
        self.selected_audio_file = None
        self.output_file = None
        self.is_exporting = False
        self.last_exported_config = None
        
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

        top_bar = FunctionBar("voice changer", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # File drop area (input, cho phép thả và chia sẻ)
        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(20)

        # Thay ComboBox bằng 5 nút độc lập
        self.selected_voice_type = None 
        voice_buttons_layout = QHBoxLayout()
        voice_buttons_layout.setAlignment(Qt.AlignCenter)

        voice_types = ["Male", "Female", "Child", "Elderly", "Robot"]
        self.voice_buttons = {}

        for voice_type in voice_types:
            btn = QPushButton(voice_type)
            btn.setFixedSize(100, 40)
            btn.setFont(QFont(font_family, 13))
            btn.setStyleSheet(self.get_voice_button_stylesheet(selected=False))
            btn.clicked.connect(lambda checked, vt=voice_type: self.select_voice_type(vt))
            voice_buttons_layout.addWidget(btn)
            voice_buttons_layout.addSpacing(10)
            self.voice_buttons[voice_type] = btn

        layout.addLayout(voice_buttons_layout)
        layout.addSpacing(15)

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
        self.export_btn.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_btn)
        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #282a32;")
        self.audio_player.load_shared_audio()

    def get_button_stylesheet(self):
        """Tạo stylesheet cho các nút chính dựa trên theme hiện tại"""
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

    def get_voice_button_stylesheet(self, selected=False):
        """Tạo stylesheet cho các nút chọn giọng nói dựa trên trạng thái selected"""
        if selected:
            return f"""
                QPushButton {{
                    background-color: {self.current_colors['dark']};
                    border-radius: 12px;
                    color: white;
                    font-weight: bold;
                    border: 2px solid #FBFFE4;
                }}
            """
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
        for vtype, btn in self.voice_buttons.items():
            selected = (vtype == self.selected_voice_type)
            btn.setStyleSheet(self.get_voice_button_stylesheet(selected=selected))

    def on_file_dropped(self, file_path):
        if file_path.lower().endswith(('.wav', '.mp3', '.flac')):
            print(f"File dropped: {file_path}")
            self.selected_audio_file = file_path
            self.last_exported_config = None

    def export_audio(self, voice_type):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        # Hiển thị cửa sổ render
        self.render_window = RenderWindow(None)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        # Đánh dấu đang trong quá trình xuất
        self.is_exporting = True
        self.export_btn.setEnabled(False)

        # Tạo worker thread
        self.worker = VoiceWorker(self.selected_audio_file, voice_type, pitch_shift=0, formant_shift=0)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def select_voice_type(self, voice_type):
        self.selected_voice_type = voice_type
        for vtype, btn in self.voice_buttons.items():
            btn.setStyleSheet(self.get_voice_button_stylesheet(selected=(vtype == voice_type)))
        
        print(f"Selected voice type: {voice_type}")
        # Reset cấu hình đã xuất cuối cùng khi chọn loại giọng khác
        if self.last_exported_config and self.last_exported_config[1] != voice_type:
            self.last_exported_config = None

    def start_export(self):
        # Kiểm tra nếu đang xuất thì không làm gì
        if self.is_exporting:
            noti_window = NotiWindow()
            noti_window.update_message("Export in progress. Please wait.")
            return
            
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return
        
        if not self.selected_voice_type:
            noti_window = NotiWindow()
            noti_window.update_message("Please select a voice type first")
            return
            
        # Kiểm tra nếu cấu hình hiện tại đã được xuất trước đó
        current_config = (self.selected_audio_file, self.selected_voice_type)
        if current_config == self.last_exported_config:
            noti_window = NotiWindow()
            noti_window.update_message("This configuration has already been exported")
            # Tự động mở thư mục chứa file đã xuất
            if self.output_file and os.path.exists(self.output_file):
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self.output_file)))
            return
        
        # Gọi hàm export_audio với loại giọng đã chọn
        self.export_audio(self.selected_voice_type)

    def on_export_finished(self, output_file):
        self.output_file = output_file
        print(f"Export completed: {output_file}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        self.last_exported_config = (self.selected_audio_file, self.selected_voice_type)
        QTimer.singleShot(1000, self.render_window.close)
        
        self.audio_player.set_audio_file(output_file)
        self.audio_data_manager.set_audio_file(output_file) 
        
        self.is_exporting = False
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        
        # Đánh dấu không còn đang xuất khi có lỗi
        self.is_exporting = False
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "voice-changer")
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