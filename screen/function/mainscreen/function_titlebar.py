from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QPoint

class CustomTitleBar(QWidget):
    def __init__(self, parent=None, font_family=None):
        super().__init__(parent)
        self.parent = parent
        self.font_family = font_family
        self.dragging = False
        self.drag_pos = QPoint()
        self.setupUI()

    def setupUI(self):
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(20, 10, 10, 2)

        # App icon
        app_icon = QLabel()
        pixmap = QPixmap("./icon/edita.png").scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_icon.setPixmap(pixmap)

        # App title
        app_title = QLabel("audio edita")
        app_title.setStyleSheet("color: white;")
        app_title.setFont(QFont(self.font_family, 14, QFont.Bold))

        # Control buttons
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon("./icon/minimize.png"))

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(QIcon("./icon/maximize.png"))

        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon("./icon/close.png"))

        # Style control buttons
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

        # Special style for close button
        self.close_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: #d32f2f;
                border-radius: 5px;
            }
        """)

        # Connect buttons to parent window actions
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.parent.toggleMaximize)
        self.close_btn.clicked.connect(self.parent.close)

        # Add widgets to layout
        title_bar_layout.addWidget(app_icon)
        title_bar_layout.addWidget(app_title)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.minimize_btn)
        title_bar_layout.addWidget(self.maximize_btn)
        title_bar_layout.addWidget(self.close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.parent.is_maximized:
                self.parent.dragging = True
                self.parent.drag_pos = event.globalPos() - self.parent.pos()
                event.accept()
            else:
                self.parent.dragging = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.parent.dragging:
            if not self.parent.is_maximized:
                self.parent.move(event.globalPos() - self.parent.drag_pos)
                event.accept()

    def toggleMaximize(self):
        if self.parent.is_maximized:
            self.parent.showNormal()
            self.parent.is_maximized = False
        else:
            self.parent.showMaximized()
            self.parent.is_maximized = True