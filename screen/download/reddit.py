import os
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices, QIcon
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.mainscreen.function_downloadbar import DownloadUI
from screen.download.worker_download import DownloadWorker, URLValidator
from screen.function.system.system_thememanager import ThemeManager

class RedditDownloadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.validator = URLValidator()

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

        top_bar = FunctionBar("download reddit audio", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Tạo giao diện tải với placeholder tùy chỉnh
        self.download_ui = DownloadUI(placeholder_text="paste reddit url")
        layout.addWidget(self.download_ui)

        # Kết nối nút download với hàm xử lý
        self.download_ui.download_btn.clicked.connect(self.download_reddit_audio)

        # Thanh nút dưới cùng
        button_layout = QHBoxLayout()
        
        # Tạo layout dọc cho hai dòng chữ
        copyright_layout = QVBoxLayout()
        copyright_layout.setSpacing(0)

        copyright_notice1 = QLabel("• respect audio creator")
        copyright_notice1.setFont(QFont(font_family, 8)) 
        copyright_notice1.setStyleSheet("color: #aaaaaa; background-color: transparent;") 
        copyright_layout.addWidget(copyright_notice1)

        copyright_notice2 = QLabel("• do not use copyrighted content without permission")
        copyright_notice2.setFont(QFont(font_family, 8))  
        copyright_notice2.setStyleSheet("color: #aaaaaa; background-color: transparent;")  
        copyright_layout.addWidget(copyright_notice2)

        # Thêm layout dọc vào layout ngang
        button_layout.addLayout(copyright_layout)
        button_layout.addStretch()

        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.open_location_btn.clicked.connect(self.open_file_location)
        button_layout.addWidget(self.open_location_btn)

        layout.addLayout(button_layout)

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

    def download_reddit_audio(self):
        reddit_link = self.download_ui.link_input.text()
        if not reddit_link:
            print("Please enter a reddit link")
            return

        # Kiểm tra URL trước khi tải
        is_valid, message, platform = self.validator.is_valid_url(reddit_link)
        if not is_valid or platform != 'reddit':
            print(f"Error: {message if not is_valid else 'This is not a valid TikTok URL'}")
            return

        # Nếu URL hợp lệ và là Tiktok, tiến hành tải
        name_label, size_label, progress_bar, main_layout = self.download_ui.add_download_item()
        self.worker = DownloadWorker(reddit_link)
        self.worker.progress.connect(lambda value: progress_bar.setValue(value))
        self.worker.finished.connect(
            lambda name, size: self.download_ui.update_download_item(name_label, size_label, progress_bar, main_layout, name, size)
        )
        self.worker.error.connect(
            lambda err: self.on_download_error(err, main_layout.parentWidget())
        )
        self.worker.start()

    def on_download_error(self, error_message, file_widget):
        """Xử lý khi có lỗi tải"""
        print(f"Download error: {error_message}")
        self.download_ui.remove_download_item(file_widget)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "download", "reddit")
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