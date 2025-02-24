from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase
from screen.function.function_functionbar import FunctionBar

class SplitPage(QWidget):
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
        top_bar = FunctionBar("split", font_family, self)
        layout.addLayout(top_bar)
        layout.addStretch()
        
        self.setStyleSheet("background-color: #282a32;")

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(0)