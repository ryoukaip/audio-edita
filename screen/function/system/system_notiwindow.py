from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer

class NotiWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        if font_id == -1:
            font_family = "Arial"
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setWindowTitle("Notification")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Độc lập với parent
        self.setStyleSheet("""
            QDialog {
                background-color: #1c1b1f;
                border: 1px solid #333333;
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel("Error")
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
            }
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.message_label)

        button_container = QHBoxLayout()
        button_container.setSpacing(10)

        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                color: white;
                border: none;
                font-size: 13px;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        self.ok_button.clicked.connect(self.close)
        
        button_container.addStretch()
        button_container.addWidget(self.ok_button)
        
        main_layout.addStretch()
        main_layout.addLayout(button_container)

        # Căn giữa cửa sổ trên màn hình
        from PyQt5.QtWidgets import QApplication
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.geometry()
        self.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )

    def update_message(self, message):
        self.message_label.setText(message)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()