from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SeparatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        title = QLabel("Separate Audio")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title)
        self.setLayout(layout)
