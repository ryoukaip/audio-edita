import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QPoint
from edit import EditPage
from separate import SeparatePage
from check import CheckPage
from function.output_separate import OutputSeparateWidget

class AudioEditorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_button = None  # Biến lưu trạng thái nút đang chọn
        self.output_widget = None
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

        # Custom Title Bar
        self.title_bar = QWidget()
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(20, 10, 10, 2)

        app_icon = QLabel()
        pixmap = QPixmap("./icon/edita.png").scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_icon.setPixmap(pixmap)

        app_title = QLabel("audio edita")
        app_title.setFont(QFont(font_family, 14, QFont.Bold))

        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon("./icon/minimize.png"))

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(QIcon("./icon/maximize.png"))

        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon("./icon/close.png"))

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(30, 30)
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 5px;
                }
            """)

        self.close_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: #d32f2f;
                border-radius: 5px;
            }
        """)

        self.minimize_btn.clicked.connect(self.showMinimized)
        self.maximize_btn.clicked.connect(self.toggleMaximize)
        self.close_btn.clicked.connect(self.close)

        title_bar_layout.addWidget(app_icon)
        title_bar_layout.addWidget(app_title)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.minimize_btn)
        title_bar_layout.addWidget(self.maximize_btn)
        title_bar_layout.addWidget(self.close_btn)

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

    def resizeEvent(self, event):
        # Kiểm tra nếu cửa sổ đang ở chế độ toàn màn hình
        if self.isMaximized():  
            self.content_layout.setStretch(0, 1)  
            self.content_layout.setStretch(1, 8)  
        else:
            self.content_layout.setStretch(0, 1) 
            self.content_layout.setStretch(1, 4)  
        super().resizeEvent(event)


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
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            if not self.is_maximized:  # Chỉ cho phép kéo khi không full screen
                self.dragging = True
                self.drag_pos = event.globalPos() - self.pos()
                event.accept()
            else:
                self.dragging = False  # Khi đang full screen, không làm gì cả


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and getattr(self, "dragging", False):
            if not self.is_maximized:  # Chỉ di chuyển khi không full screen
                self.move(event.globalPos() - self.drag_pos)
                event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioEditorUI()
    window.show()
    sys.exit(app.exec_())
