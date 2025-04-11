from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, pyqtSignal
from screen.function.mainscreen.function_settingbar import SettingBar

class MenuSettingPage(QWidget):
    theme_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Thêm font cho ứng dụng
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title_subtitle_layout = QVBoxLayout()
        title_subtitle_layout.setSpacing(2)
        title_subtitle_layout.setAlignment(Qt.AlignCenter)

        # Tạo hệ thống tab từ hàm riêng
        tabs_container = SettingBar(self, font_family)
        tabs_container.theme_changed.connect(self.theme_changed.emit)
        tabs_container.setMaximumWidth(600)

        # Thêm các thành phần vào layout chính
        layout.addLayout(title_subtitle_layout)
        layout.addWidget(tabs_container, alignment=Qt.AlignCenter)
        layout.addStretch()
        

