from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QVariantAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._arc_length = 45  # Độ dài ban đầu
        self.setFixedSize(60, 60)
        
        # Tạo group animation cho một chu kỳ hoàn chỉnh
        self.cycle_duration = 3000  # 3 giây cho 3 vòng xoay
        
        # Animation cho góc xoay - xoay đúng 3 vòng (1080 độ)
        self.rotation_animation = QVariantAnimation(self)
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(1080)  # 3 vòng đầy đủ
        self.rotation_animation.setDuration(self.cycle_duration)
        self.rotation_animation.setLoopCount(-1)  # Lặp vô hạn
        self.rotation_animation.valueChanged.connect(self.set_angle)
        
        # Animation cho độ dài cung - đảm bảo kết thúc với giá trị ban đầu
        self.arc_animation = QVariantAnimation(self)
        self.arc_animation.setStartValue(45)
        self.arc_animation.setEndValue(270)
        self.arc_animation.setDuration(self.cycle_duration // 2)  # Nửa đầu chu kỳ - dài ra
        self.arc_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.arc_animation.valueChanged.connect(self.set_arc_length)
        self.arc_animation.finished.connect(self.reverse_arc_animation)
        
        # Animation ngược cho độ dài cung - đảm bảo quay về giá trị ban đầu
        self.reverse_arc = QVariantAnimation(self)
        self.reverse_arc.setStartValue(270)
        self.reverse_arc.setEndValue(45)
        self.reverse_arc.setDuration(self.cycle_duration // 2)  # Nửa sau chu kỳ - ngắn lại
        self.reverse_arc.setEasingCurve(QEasingCurve.InOutQuad)
        self.reverse_arc.valueChanged.connect(self.set_arc_length)
        self.reverse_arc.finished.connect(self.start_arc_animation)
        
    def get_angle(self):
        return self._angle
        
    def set_angle(self, angle):
        # Chuyển đổi góc về phạm vi 0-360
        self._angle = angle % 360
        self.update()
        
    def get_arc_length(self):
        return self._arc_length
        
    def set_arc_length(self, length):
        self._arc_length = length
        self.update()
        
    # Định nghĩa các thuộc tính cho animation
    angle = pyqtProperty(float, get_angle, set_angle)
    arc_length = pyqtProperty(float, get_arc_length, set_arc_length)
    
    def start(self):
        self.rotation_animation.start()
        self.arc_animation.start()
        self.show()
        
    def stop(self):
        self.rotation_animation.stop()
        self.arc_animation.stop()
        self.reverse_arc.stop()
        self.hide()
    
    def reverse_arc_animation(self):
        # Chuyển từ animation dài ra sang animation ngắn lại
        self.reverse_arc.start()
        
    def start_arc_animation(self):
        # Chuyển từ animation ngắn lại sang animation dài ra
        self.arc_animation.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor("#FBFFE4"))
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Vẽ đoạn cung với các giá trị hiện tại
        painter.drawArc(rect, int(self._angle * 16), int(self._arc_length * 16))

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spinner = LoadingSpinner(self)
        self.setup_ui()
        self.hide()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(125, 139, 212, 0.8);
                border-radius: 25px;
            }
        """)
        
    def resizeEvent(self, event):
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