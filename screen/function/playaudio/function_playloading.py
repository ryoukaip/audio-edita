from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QVariantAnimation
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient

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
        
        # Indeterminate effect - shine animation
        self.shine_position = 0
        self.shine_animation = QVariantAnimation(self)
        self.shine_animation.setStartValue(0)
        self.shine_animation.setEndValue(360)  # Full circle
        self.shine_animation.setDuration(1500)  # 1.5 seconds for one cycle
        self.shine_animation.setLoopCount(-1)  # Loop infinitely
        self.shine_animation.valueChanged.connect(self.update_shine)
        
    def start(self):
        self.timer.start(50)  # Update every 50ms
        self.shine_animation.start()
        self.show()
        
    def stop(self):
        self.timer.stop()
        self.shine_animation.stop()
        self.hide()
        
    def rotate(self):
        target_angle = (self.angle + 15) % 360  # Rotate 15 degrees each step
        self.rotation_animation.setStartValue(self.angle)
        self.rotation_animation.setEndValue(target_angle)
        self.rotation_animation.start()
        self.angle = target_angle
    
    def update_shine(self, value):
        self.shine_position = value
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up the pen for main arc
        pen = QPen(QColor("#FBFFE4"))  # Use the light color from your theme
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Calculate the rect for the arc
        rect = self.rect().adjusted(5, 5, -5, -5)  # Margin of 5px
        
        # Draw the arc
        painter.drawArc(rect, self.angle * 16, self.arc_length * 16)
        
        # Draw the shine effect (indeterminate animation)
        shine_pen = QPen()
        shine_pen.setWidth(6)
        shine_pen.setCapStyle(Qt.RoundCap)
        
        # Create a gradient for the shine
        gradient = QLinearGradient(rect.center().x(), rect.center().y() - 30, 
                                  rect.center().x(), rect.center().y() + 30)
        gradient.setColorAt(0.0, QColor(255, 255, 228, 0))  # Transparent
        gradient.setColorAt(0.5, QColor("#FBFFE4"))  # Bright 
        gradient.setColorAt(1.0, QColor(255, 255, 228, 0))  # Transparent
        
        shine_pen.setBrush(gradient)
        painter.setPen(shine_pen)
        
        # Draw a small arc for the shine effect
        shine_angle = (self.shine_position - 15) % 360
        painter.drawArc(rect, shine_angle * 16, 30 * 16)  # 30 degree shine

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