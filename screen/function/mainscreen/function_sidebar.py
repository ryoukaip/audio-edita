from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class CustomSidebar(QWidget):
    buttonClicked = pyqtSignal(int, QPushButton)

    def __init__(self, parent=None, font_family=None):
        super().__init__(parent)
        self.font_family = font_family
        self.current_button = None
        self.current_theme = None
        self.setupUI()

    def setupUI(self):
        # Set solid background for the sidebar widget
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

        self.set_theme({
            "primary": "#98a4e6",
            "secondary": "#7d8bd4",
            "background": "#474f7a",
            "highlight": "#6574c6",
            "shadow": "#3a4062",
            "dark": "#292d47"
        })

    def set_theme(self, colors):
        self.current_theme = colors
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
        active_style = f"""
            QPushButton {{
                background-color: {self.current_theme['background']};
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