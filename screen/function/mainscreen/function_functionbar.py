from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

class FunctionBar(QHBoxLayout):
    def __init__(self, title, font_family, parent=None):
        super().__init__()
        self.parent = parent
        self.setSpacing(8)
        self.setup_ui(title, font_family)

    def setup_ui(self, title, font_family):
        # Back button
        back_button = QPushButton()
        back_button.setIcon(QIcon("./icon/arrow.png"))
        back_button.setIconSize(QSize(15, 15))
        back_button.setFixedSize(32, 32)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #282a32;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        if self.parent:
            back_button.clicked.connect(self.parent.go_back)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont(font_family, 13))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setContentsMargins(4, 0, 0, 0)

        infor_button = QPushButton()
        infor_button.setIcon(QIcon("./icon/faq.png"))
        infor_button.setIconSize(QSize(15, 15))
        infor_button.setFixedSize(32, 32)

        action_buttons_style = """
            QPushButton {
                background-color: #3a4062;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """
        infor_button.setStyleSheet(action_buttons_style)
        

        # Add widgets to layout
        self.addWidget(back_button)
        self.addWidget(title_label)
        self.addStretch()
        self.addWidget(infor_button)