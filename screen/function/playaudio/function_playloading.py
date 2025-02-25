from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.arc_length = 90  # Length of the arc in degrees
        self.setFixedSize(60, 60)  # Fixed size for the spinner
        
        # Animation for smooth rotation
        self.rotation_animation = QPropertyAnimation(self, b"angle")
        self.rotation_animation.setDuration(50)  # Duration for each step
        self.rotation_animation.valueChanged.connect(self.update)
        
    def start(self):
        self.timer.start(50)  # Update every 100ms
        self.show()
        
    def stop(self):
        self.timer.stop()
        self.hide()
        
    def rotate(self):
        target_angle = (self.angle + 15) % 360  # Rotate 30 degrees each step
        self.rotation_animation.setStartValue(self.angle)
        self.rotation_animation.setEndValue(target_angle)
        self.rotation_animation.start()
        self.angle = target_angle
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up the pen
        pen = QPen(QColor("#FBFFE4"))  # Use the light color from your theme
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Calculate the rect for the arc
        rect = self.rect().adjusted(5, 5, -5, -5)  # Margin of 5px
        
        # Draw the arc
        painter.drawArc(rect, self.angle * 16, self.arc_length * 16)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spinner = LoadingSpinner(self)
        self.setup_ui()
        self.hide()  # Initially hidden
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(125, 139, 212, 0.8);  /* Semi-transparent background */
                border-radius: 25px;
            }
        """)
        
    def resizeEvent(self, event):
        # Center the spinner in the overlay
        spinner_pos = QPoint(
            (self.width() - self.spinner.width()) // 2,
            (self.height() - self.spinner.height()) // 2
        )
        self.spinner.move(spinner_pos)
        
    def show_loading(self):
        self.show()
        self.spinner.start()
        
    def hide_loading(self):
        self.spinner.stop()
        self.hide()