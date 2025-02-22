import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QPoint
from edit import EditPage
from separate import SeparatePage
from check import CheckPage
from function.output_separate import OutputSeparateWidget
from function.function_titlebar import CustomTitleBar

class AudioEditorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_button = None
        self.output_widget = None
        self.dragging = False
        self.drag_pos = QPoint()
        self.is_maximized = False
        self.initUI()

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setWindowTitle("audio edita")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1c1b1f; color: white;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Use custom title bar
        self.title_bar = CustomTitleBar(self, font_family)
        main_layout.addWidget(self.title_bar)

        # Nội dung chính
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout = content_layout # Lưu lại layout để sử dụng trong resizeEvent

        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        sidebar.setContentsMargins(10, 10, 10, 10)

        self.stack = QStackedWidget()
        self.stack.addWidget(EditPage())
        self.stack.addWidget(SeparatePage())
        self.stack.addWidget(CheckPage())
        self.stack.addWidget(OutputSeparateWidget())

        self.edit_btn = QPushButton(" Edit")
        self.edit_btn.setIcon(QIcon("./icon/edit.png"))
        self.separate_btn = QPushButton(" Separate")
        self.separate_btn.setIcon(QIcon("./icon/trim.png"))
        self.check_btn = QPushButton(" Check")
        self.check_btn.setIcon(QIcon("./icon/check.png"))

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
            btn.setFont(QFont(font_family, 12))
            btn.setFixedHeight(50)
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(
                lambda checked, i=index, b=btn: (self.stack.setCurrentIndex(i), self.set_active_button(b)))
            sidebar.addWidget(btn)

        sidebar.addStretch()

        content_layout.addLayout(sidebar, 1)
        content_layout.addWidget(self.stack, 4)
        self.stack.setStyleSheet("""
            background-color: #282a32;
            border-top-left-radius: 22px;
        """)

        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(content_layout)

        # Mặc định nút Edit được chọn
        self.set_active_button(self.edit_btn) 
        self.is_maximized = False

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
            """)  # Reset màu nút cũ

        button.setStyleSheet("""
            QPushButton {
                background-color: #474f7a;  /* Màu nút đang chọn */
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                text-align: left;
            }
        """)  
        self.current_button = button  # Cập nhật nút hiện tại
        
    def toggleMaximize(self):
        self.title_bar.toggleMaximize()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioEditorUI()
    window.show()
    sys.exit(app.exec_())
