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
        self.edit_btn = QPushButton(" Edit")
        self.edit_btn.setIcon(QIcon("./icon/edit.png"))
        self.separate_btn = QPushButton(" Separate")
        self.separate_btn.setIcon(QIcon("./icon/trim.png"))
        self.check_btn = QPushButton(" Check")
        self.check_btn.setIcon(QIcon("./icon/check.png"))

        # Style and setup buttons
        for index, btn in enumerate([self.edit_btn, self.separate_btn, self.check_btn]):
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