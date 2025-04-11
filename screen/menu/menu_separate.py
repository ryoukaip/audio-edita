from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt

class IconButton(QPushButton):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Đặt kích thước cố định cho nút
        self.setFixedSize(110, 80)  # Đặt kích thước tối đa cố định

        # Load font Cabin-Bold
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family, 11))  # Áp dụng font cho nút

        self.setStyleSheet("""
            QPushButton {
                background-color: #323754;
                border-radius: 15px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(self)
        pixmap = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        text_label = QLabel(text, self)
        text_label.setFont(QFont(font_family, 11))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: white; background: transparent;")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        self.setLayout(layout)

class MenuSeparatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        #Thêm font cho ứng dụng
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 12)
        layout.setSpacing(15)
        
        # Grid Layout cho các nút
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(15)

        buttons = [
            ("vocal", "./icon/micro.png"), ("video", "./icon/video.png"),
            ("noise", "./icon/noise.png"),
        ]
        
        positions = [(i, j) for i in range(2) for j in range(5)]
        for pos, (text, icon_path) in zip(positions, buttons):
            btn = IconButton(icon_path, text)
            if text == "vocal":
                btn.clicked.connect(self.show_vocal_separation_page)
            elif text == "video":
                btn.clicked.connect(self.show_video_page)
            elif text == "noise":
                btn.clicked.connect(self.show_noise_page)
            grid.addWidget(btn, *pos)
        
        container.setFixedWidth(400)

        layout.addWidget(container, alignment=Qt.AlignCenter)
        layout.addStretch()  # Đẩy lưới nút lên khi mở rộng cửa sổ

    def show_vocal_separation_page(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("Separate")
            if page_widget:
                stack.setCurrentWidget(page_widget)

    def show_video_page(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("Video2Audio")
            if page_widget:
                stack.setCurrentWidget(page_widget)

    def show_noise_page(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("Noise")
            if page_widget:
                stack.setCurrentWidget(page_widget)