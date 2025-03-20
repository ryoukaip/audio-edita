import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer

from main_screen import AudioEditorUI

class WelcomeWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.current_page = 0
        self.main_window = main_window
        self.initUI()
        self.center()

        # Setup auto-page switching timer
        self.page_timer = QTimer(self)
        self.page_timer.timeout.connect(self.auto_next_page)
        self.page_timer.start(3500)

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        if font_id == -1:
            font_family = "Arial"
            print("Warning: Could not load Cabin-Bold.ttf, using Arial instead")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1c1b1f; color: white;")
        self.oldPos = None
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        
        page_contents = [
            {"icon": "./icon/edita.png", "icon_size": 60, "title": "Welcome to", "subtitle": "audio edita", "description": ""},
            {"icon": "./icon/edit.png", "icon_size": 50, "title": "Audio Editing", "subtitle": "", "description": "Edit audio professionally with tools for cutting, splicing,\nadjusting volume, removing noise, and easily adding effects."},
            {"icon": "./icon/trim.png", "icon_size": 50, "title": "Audio Separation", "subtitle": "", "description": "Separate tracks into individual components such as vocals and\ninstruments, supporting remixing, karaoke, or advanced audio processing."},
            {"icon": "./icon/check.png", "icon_size": 50, "title": "Copyright Check", "subtitle": "", "description": "Quickly determine the ownership of audio files, ensuring content usage\ncomplies with the law and avoids copyright infringement."},
            {"icon": "./icon/heart.png", "icon_size": 50, "title": "and you", "subtitle": "", "description": "The amazing contributions from the community\n and open-source projects make Edita better and free."}
        ]

        for i, content in enumerate(page_contents):
            page = self.create_page(font_family, content, i == 0)
            self.stack.addWidget(page)

        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setAlignment(Qt.AlignCenter)
        nav_layout.setContentsMargins(0, 0, 0, 40)
        
        dots_container = QWidget()
        dots_container_layout = QHBoxLayout(dots_container)
        dots_container_layout.setAlignment(Qt.AlignCenter)
        dots_container_layout.setSpacing(10)

        self.dots_layout = QHBoxLayout()
        self.dots_layout.setAlignment(Qt.AlignCenter)
        self.dots_layout.setSpacing(10)
        self.dots = []
        
        for i in range(5):
            dot = QPushButton("•")
            dot.setFont(QFont(font_family, 45))
            dot.setFixedSize(30, 30)
            dot.setStyleSheet("""
                QPushButton { color: #555555; background: transparent; border: none; }
                QPushButton:hover { color: #7d8bd4; }
            """)
            if i == 0:
                dot.setStyleSheet("""
                    QPushButton { color: #7d8bd4; background: transparent; border: none; }
                    QPushButton:hover { color: #7d8bd4; }
                """)
            dot.clicked.connect(lambda checked, idx=i: self.go_to_page(idx))
            self.dots.append(dot)
            self.dots_layout.addWidget(dot)
        
        dots_container_layout.addStretch(1)
        dots_container_layout.addLayout(self.dots_layout)
        dots_container_layout.addStretch(1)
        
        terms_label = QLabel("by using the service, you agree to the Terms of Service and Privacy Policy")
        terms_label.setFont(QFont(font_family, 8))
        terms_label.setAlignment(Qt.AlignCenter)
        terms_label.setStyleSheet("color: #888888")
        
        nav_layout.addWidget(dots_container)
        nav_layout.addWidget(terms_label)

        self.start_button = QPushButton("Get Started")
        self.start_button.setFont(QFont(font_family, 14))
        self.start_button.setFixedSize(200, 50)
        self.start_button.setStyleSheet("""
            QPushButton { background-color: #474f7a; border-radius: 10px; color: white; }
            QPushButton:hover { background-color: #7d8bd4; }
        """)
        self.start_button.clicked.connect(self.start_transition)
        self.start_button.setVisible(False)

        main_layout.addWidget(self.stack, 1)
        main_layout.addWidget(self.start_button, 0, Qt.AlignCenter)
        main_layout.addWidget(nav_widget, 0)

    def create_page(self, font_family, content, is_welcome_page=False):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.addStretch(1)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)

        if is_welcome_page:
            title = QLabel(content["title"])
            title.setFont(QFont(font_family, 20))
            title.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(title)
            
        group_widget = QWidget()
        group_layout = QHBoxLayout(group_widget)
        group_layout.setAlignment(Qt.AlignCenter)
        group_layout.setSpacing(10)

        image_label = QLabel()
        image_label.setPixmap(QIcon(content["icon"]).pixmap(content["icon_size"], content["icon_size"]))
        image_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(image_label)

        text = content["subtitle"] if is_welcome_page else content["title"]
        if text:
            text_label = QLabel(text)
            text_label.setFont(QFont(font_family, 18 if is_welcome_page else 20, QFont.Bold))
            text_label.setAlignment(Qt.AlignCenter)
            group_layout.addWidget(text_label)

        content_layout.addWidget(group_widget)

        if content["description"]:
            desc = QLabel(content["description"])
            desc.setFont(QFont(font_family, 14))
            desc.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(desc)

        page_layout.addWidget(content_widget)
        page_layout.addStretch(1)
        
        return page

    def update_dots(self):
        active_dot_style = """
            QPushButton { color: #7d8bd4; background: transparent; border: none; }
            QPushButton:hover { color: #7d8bd4; }
        """
        inactive_dot_style = """
            QPushButton { color: #555555; background: transparent; border: none; }
            QPushButton:hover { color: #7d8bd4; }
        """
        for i, dot in enumerate(self.dots):
            dot.setStyleSheet(active_dot_style if i == self.current_page else inactive_dot_style)
        self.start_button.setVisible(self.current_page == 4)

    def go_to_page(self, page_index):
        self.current_page = page_index
        self.stack.setCurrentIndex(self.current_page)
        self.update_dots()

        if page_index < 4: 
            self.page_timer.start(3500)
        else:
            self.page_timer.stop()

    def start_transition(self):
        # Emit closed signal first to trigger boot screen preparation
        self.closed.emit()
        
        # Create fade out animation for welcome window
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(700)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.hide)  

        # Start fade out
        self.fade_out_animation.start()

    def auto_next_page(self):
        if self.current_page < 4:  # We have 5 pages (0-4)
            self.go_to_page(self.current_page + 1)
        else:
            self.page_timer.stop()

    def close_welcome(self):
        self.closed.emit()
        self.hide()

    def closeEvent(self, event):
        # Chỉ đơn giản chấp nhận sự kiện đóng
        event.accept()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None