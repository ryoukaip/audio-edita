from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class CheckPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        title = QLabel("Audio Checking")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        
        subtitle = QLabel("This section is under development.")
        subtitle.setFont(QFont("Arial", 12))
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        self.setLayout(layout)
