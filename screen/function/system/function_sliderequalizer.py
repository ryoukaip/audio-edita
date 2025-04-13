import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from screen.function.system.system_thememanager import ThemeManager

class CustomSlider(QWidget):
    value_changed = pyqtSignal(float)
    
    def __init__(self, min_value=-12, max_value=12, default_value=0, icon_path="./icon/dot.png"):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.icon_path = icon_path
        self.handle_pixmap = QPixmap(self.icon_path)
        self.handle_pos = None
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_colors)
        
        self.setFixedHeight(150)
        self.setFixedWidth(60)
        self.setMouseTracking(True)
        
    def value_to_pos(self, value):
        """Chuyển giá trị thành vị trí pixel trên thanh trượt"""
        range_height = self.height() - 20  # Trừ padding
        mid_point = range_height // 2
        value_range = self.max_value - self.min_value
        pos = mid_point - (value / value_range) * range_height
        return int(pos + 10)  # +10 để căn chỉnh với padding
    
    def pos_to_value(self, pos):
        """Chuyển vị trí pixel thành giá trị"""
        range_height = self.height() - 20
        mid_point = range_height // 2
        value_range = self.max_value - self.min_value
        value = ((mid_point - (pos - 10)) / range_height) * value_range
        return max(self.min_value, min(self.max_value, value))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ rãnh (groove)
        groove_rect = QRect(22, 10, 16, self.height() - 20)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.current_colors['shadow']))
        painter.drawRoundedRect(groove_rect, 8, 8)
        
        # Vẽ vùng màu từ trung tâm đến tay cầm (hình chữ nhật)
        mid_point = self.height() // 2
        if self.value > 0:
            color_rect = QRect(22, mid_point, 16, self.handle_pos - mid_point)
            painter.setBrush(QColor(self.current_colors['secondary']))
            painter.drawRect(color_rect)
        elif self.value < 0:
            color_rect = QRect(22, self.handle_pos, 16, mid_point - self.handle_pos)
            painter.setBrush(QColor(self.current_colors['secondary']))
            painter.drawRect(color_rect)
        
        # Vẽ tay cầm (handle) bằng dot.png
        handle_rect = QRect(10, self.handle_pos - 20, 40, 40)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(handle_rect, self.handle_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Recalculate handle position whenever the widget is resized
        if self.handle_pos is None:
            self.handle_pos = self.value_to_pos(self.value)
        self.update()  # Force a repaint
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.update_handle(event.y())
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.update_handle(event.y())
    
    def update_handle(self, y_pos):
        self.handle_pos = max(10, min(self.height() - 10, y_pos))
        self.value = self.pos_to_value(self.handle_pos)
        self.value_changed.emit(self.value)
        self.update()
    
    def update_colors(self, colors):
        """Update colors when theme changes"""
        self.current_colors = colors
        self.update()  # Force a repaint to apply new colors
    
    def set_value(self, value):
        self.value = max(self.min_value, min(self.max_value, value))
        self.handle_pos = self.value_to_pos(self.value)
        self.update()
    
    def get_value(self):
        return self.value

class SliderEqualizer(QWidget):
    value_changed = pyqtSignal(float)
    
    def __init__(self, font_family, freq_label="60 Hz", min_value=-12, max_value=12, default_value=0, 
                 unit="dB", icon_path="./icon/dot.png"):
        super().__init__()
        self.font_family = font_family
        self.freq_label = freq_label
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.unit = unit
        self.icon_path = icon_path
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        freq_label = QLabel(self.freq_label)
        freq_label.setFont(QFont(self.font_family, 11))
        freq_label.setStyleSheet("color: white;")
        freq_label.setAlignment(Qt.AlignCenter)
        freq_label.setFixedHeight(20)
        layout.addWidget(freq_label)

        self.slider = CustomSlider(self.min_value, self.max_value, self.default_value, self.icon_path)
        self.slider.value_changed.connect(self.update_value)
        layout.addWidget(self.slider, alignment=Qt.AlignHCenter)

        self.value_label = QLabel(f"{self.default_value}{self.unit}")
        self.value_label.setFont(QFont(self.font_family, 11))
        self.value_label.setStyleSheet("color: white;")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFixedHeight(20)
        layout.addWidget(self.value_label)

        self.setFixedWidth(80)
    
    def update_value(self, value):
        self.value_label.setText(f"{int(value)}{self.unit}")
        self.value_changed.emit(value)
    
    def get_processed_value(self):
        return self.slider.get_value()
    
    def set_value(self, value):
        self.slider.set_value(value)
    
    def get_raw_value(self):
        return self.slider.get_value()

class EqualizerControls(QWidget):
    value_changed = pyqtSignal(float)
    
    def __init__(self, font_family):
        super().__init__()
        self.font_family = font_family
        self.eq_sliders = {}
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        eq_layout = QHBoxLayout()
        eq_layout.setSpacing(20)
        eq_layout.setAlignment(Qt.AlignHCenter)
        
        freq_bands = [ 
            ("60 Hz", 60), 
            ("250 Hz", 250), 
            ("1 kHz", 1000), 
            ("4 kHz", 4000), 
            ("12 kHz", 12000), 
            ("16 kHz", 16000)
        ]
        for label, freq in freq_bands:
            slider = SliderEqualizer(self.font_family, freq_label=label, min_value=-12, max_value=12, 
                                    default_value=0, unit=" dB", icon_path="./icon/dot.png")
            slider.value_changed.connect(self.handle_slider_change)
            eq_layout.addWidget(slider)
            self.eq_sliders[freq] = slider
        
        layout.addLayout(eq_layout)
    
    def handle_slider_change(self, value):
        self.value_changed.emit(value)
    
    def get_eq_settings(self):
        return {freq: slider.get_processed_value() for freq, slider in self.eq_sliders.items()}