import os
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices, QIcon
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.download.function_downloadui import DownloadUI
from screen.download.worker_download import DownloadWorker

class XDownloadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("download x audio", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Tạo giao diện tải với placeholder tùy chỉnh
        self.download_ui = DownloadUI(placeholder_text="x.com/sofujinia_mori")
        layout.addWidget(self.download_ui)

        # Kết nối nút download với hàm xử lý
        self.download_ui.download_btn.clicked.connect(self.download_x_audio)

        # Thanh nút dưới cùng
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

        layout.addLayout(button_layout)

    def download_x_audio(self):
        x_link = self.download_ui.link_input.text()
        if x_link:
            # Thêm mục tải vào danh sách
            name_label, size_label, progress_bar, main_layout = self.download_ui.add_download_item()

            # Tạo và chạy worker thread
            self.worker = DownloadWorker(x_link)
            self.worker.progress.connect(lambda value: progress_bar.setValue(value))
            self.worker.finished.connect(
                lambda name, size: self.download_ui.update_download_item(name_label, size_label, progress_bar, main_layout, name, size)
            )
            self.worker.error.connect(
                lambda err: self.on_download_error(err, main_layout.parentWidget())
            )
            self.worker.start()
        else:
            print("Please enter a X link")

    def on_download_error(self, error_message, file_widget):
        """Xử lý khi có lỗi tải"""
        print(f"Download error: {error_message}")
        self.download_ui.remove_download_item(file_widget)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "download", "x")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(3)