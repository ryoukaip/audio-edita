from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class IconButton(QWidget):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 120)  # Đảm bảo kích thước phù hợp

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)

        # QLabel để hiển thị icon
        icon_label = QLabel(self)
        pixmap = QPixmap(icon_path).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        # QLabel để hiển thị chữ
        text_label = QLabel(text, self)
        text_label.setFont(QFont("Arial", 11))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: white;")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        self.setLayout(layout)
        self.setStyleSheet("""
            background-color: #323754;
            border-radius: 10px;
        """)

class EditPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("audio editing")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("choose a function to start")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        
        title_subtitle_layout = QVBoxLayout()
        title_subtitle_layout.addWidget(title)
        title_subtitle_layout.addWidget(subtitle)
        title_subtitle_layout.setSpacing(10)
        title_subtitle_layout.setAlignment(Qt.AlignCenter)
        
        # Grid Layout cho các nút
        grid = QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(5)

        buttons = [
            ("mixing", "./icon/mix.png"), ("trim", "./icon/trim.png"), 
            ("merge", "./icon/merge.png"), ("split", "./icon/split.png"),
            ("volume", "./icon/volume.png"), ("reverse", "./icon/reverse.png"), 
            ("speed", "./icon/speed.png"), ("compress", "./icon/compress.png"),
            ("convert", "./icon/convert.png"), ("voice changer", "./icon/voice.png")
        ]
        
        positions = [(i, j) for i in range(2) for j in range(5)]
        for pos, (text, icon_path) in zip(positions, buttons):
            btn = IconButton(icon_path, text)  # Sử dụng widget nút tùy chỉnh
            grid.addWidget(btn, *pos)
        
        layout.addLayout(title_subtitle_layout)
        layout.addLayout(grid)
