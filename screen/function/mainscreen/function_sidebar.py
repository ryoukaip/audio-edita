from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class CustomSidebar(QWidget):
    buttonClicked = pyqtSignal(int, QPushButton)  # Signal for button clicks

    def __init__(self, parent=None, font_family=None):
        super().__init__(parent)
        self.font_family = font_family
        self.current_button = None
        self.setupUI()

    def setupUI(self):
        sidebar = QVBoxLayout(self)
        sidebar.setSpacing(10)
        sidebar.setContentsMargins(10, 10, 10, 10)

        # Create buttons
        self.tool_btn = QPushButton(" tool")
        self.tool_btn.setIcon(QIcon("./icon/tool.png"))
        self.community_btn = QPushButton(" community")
        self.community_btn.setIcon(QIcon("./icon/community.png"))
        self.setting_btn = QPushButton(" setting")
        self.setting_btn.setIcon(QIcon("./icon/setting.png"))

        # Style and setup buttons
        for index, btn in enumerate([self.tool_btn,
                                     self.community_btn,
                                     self.setting_btn,]):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1c1b1f;
                    color: white;
                    font-size: 14px;
                    border: none;
                    border-radius: 14px;
                    padding: 12px 16px;
                    text-align: left;
                }
            """)
            btn.setFont(QFont(self.font_family, 12))
            btn.setFixedHeight(50)
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(
                lambda checked, i=index, b=btn: self.buttonClicked.emit(i, b))
            sidebar.addWidget(btn)

        sidebar.addStretch()

    def set_active_button(self, button):
        if self.current_button:
            self.current_button.setStyleSheet("""
                QPushButton {
                    background-color: #1c1b1f;
                    color: white;
                    font-size: 14px;
                    border: none;
                    border-radius: 14px;
                    padding: 12px 16px;
                    text-align: left;
                }
            """)

        button.setStyleSheet("""
            QPushButton {
                background-color: #474f7a;
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                text-align: left;
            }
        """)
        self.current_button = button