from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtCore import QSize
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.check.shazam import ShazamApp

class CheckOnlinePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Add function bar
        top_bar = FunctionBar("Check Copyright Online", font_family, self)
        layout.addLayout(top_bar)

        # Integrate ShazamApp
        self.shazam_app = ShazamApp()
        layout.addWidget(self.shazam_app.centralWidget())

        self.setStyleSheet("background-color: #282a32;")

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(2)

    def toggle_playback(self):
        # Placeholder for the actual playback toggle functionality
        pass