from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from screen.function.system.system_thememanager import ThemeManager

class CustomSidebar(QWidget):
    buttonClicked = pyqtSignal(int, QPushButton)

    def __init__(self, parent=None, font_family=None):
        super().__init__(parent)
        self.font_family = font_family
        self.current_button = None
        
        # Sử dụng ThemeManager thay vì quản lý theme trực tiếp
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.setupUI()

    def setupUI(self):
        self.setStyleSheet("background-color: #1c1b1f;")

        sidebar = QVBoxLayout(self)
        sidebar.setSpacing(10)
        sidebar.setContentsMargins(10, 10, 10, 10)

        self.tool_btn = QPushButton(" tool")
        self.tool_btn.setIcon(QIcon("./icon/tool.png"))
        self.community_btn = QPushButton(" community")
        self.community_btn.setIcon(QIcon("./icon/community.png"))
        self.setting_btn = QPushButton(" setting")
        self.setting_btn.setIcon(QIcon("./icon/setting.png"))

        for index, btn in enumerate([self.tool_btn, self.community_btn, self.setting_btn]):
            btn.setFont(QFont(self.font_family, 12))
            btn.setFixedHeight(50)
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(
                lambda checked, i=index, b=btn: self.buttonClicked.emit(i, b))
            sidebar.addWidget(btn)

        sidebar.addStretch()

        # Áp dụng theme hiện tại từ ThemeManager
        self.set_theme(self.theme_manager.get_theme_colors())

    def on_theme_changed(self, colors):
        """Được gọi khi theme thay đổi trong ThemeManager"""
        self.set_theme(colors)

    def set_theme(self, colors):
        default_style = f"""
            QPushButton {{
                background-color: #1c1b1f;
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                text-align: left;
            }}
        """
        for btn in [self.tool_btn, self.community_btn, self.setting_btn]:
            if btn != self.current_button:
                btn.setStyleSheet(default_style)
        if self.current_button:
            self.set_active_button(self.current_button)

    def set_active_button(self, button):
        if self.current_button:
            self.current_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1c1b1f;
                    color: white;
                    font-size: 14px;
                    border: none;
                    border-radius: 14px;
                    padding: 12px 16px;
                    text-align: left;
                }}
            """)
        
        # Lấy theme hiện tại từ ThemeManager
        current_theme = self.theme_manager.get_theme_colors()
        
        active_style = f"""
            QPushButton {{
                background-color: {current_theme['background']};
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                text-align: left;
            }}
        """
        button.setStyleSheet(active_style)
        self.current_button = button