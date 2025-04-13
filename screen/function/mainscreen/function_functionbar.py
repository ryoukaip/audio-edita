from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize
from screen.function.system.system_thememanager import ThemeManager

class FunctionBar(QHBoxLayout):
    def __init__(self, title, font_family, parent=None):
        super().__init__()
        self.parent = parent
        self.setSpacing(8)
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_button_colors)
        
        self.setup_ui(title, font_family)

    def setup_ui(self, title, font_family):
        # Back button
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("./icon/arrow.png"))
        self.back_button.setIconSize(QSize(15, 15))
        self.back_button.setFixedSize(32, 32)
        self.back_button.setStyleSheet(self.get_button_stylesheet())
        if self.parent:
            self.back_button.clicked.connect(self.parent.go_back)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont(font_family, 13))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setContentsMargins(4, 0, 0, 0)

        # Info button
        self.infor_button = QPushButton()
        self.infor_button.setIcon(QIcon("./icon/faq.png"))
        self.infor_button.setIconSize(QSize(15, 15))
        self.infor_button.setFixedSize(32, 32)
        self.infor_button.setStyleSheet(self.get_button_stylesheet())

        # Add widgets to layout
        self.addWidget(self.back_button)
        self.addWidget(title_label)
        self.addStretch()
        self.addWidget(self.infor_button)
    
    def get_button_stylesheet(self):
        """Tạo stylesheet cho các nút dựa trên theme hiện tại"""
        return f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 15px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.current_colors['dark']};
            }}
        """
    
    def update_button_colors(self, colors):
        """Cập nhật màu sắc của các nút khi theme thay đổi"""
        self.current_colors = colors
        self.back_button.setStyleSheet(self.get_button_stylesheet())
        self.infor_button.setStyleSheet(self.get_button_stylesheet())