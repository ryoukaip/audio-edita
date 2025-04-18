import os
from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from screen.function.system.system_thememanager import ThemeManager

class Slider(QWidget):
    value_changed = pyqtSignal(float)  
    
    def __init__(self, font_family, mode="volume", min_value=0, max_value=200, default_value=100, 
                 unit="%", icon_path="./icon/volume.png"):

        super().__init__()
        self.font_family = font_family
        self.mode = mode
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.unit = unit
        self.icon_path = icon_path
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu thanh trượt
        self.theme_manager.theme_changed.connect(self.update_slider_colors)
        
        self.initUI()
    
    def initUI(self):
        # Create horizontal layout for slider controls
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add icon
        icon_label = QLabel()
        icon_pixmap = QPixmap(self.icon_path)
        icon_label.setPixmap(icon_pixmap.scaledToHeight(24, Qt.SmoothTransformation))
        icon_label.setFixedSize(30, 30)
        layout.addWidget(icon_label)

        # Add slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self.min_value, self.max_value)
        self.slider.setValue(self.default_value)
        self.apply_slider_style()
        self.slider.valueChanged.connect(self.update_value)
        layout.addWidget(self.slider)

        # Add value label
        self.value_label = QLabel(f"{self.default_value}{self.unit}")
        self.value_label.setFont(QFont(self.font_family, 12))
        self.value_label.setStyleSheet("color: white;")
        self.value_label.setFixedWidth(70)  
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        """Update value label and emit signal when slider changes"""
        # Tùy chỉnh hiển thị dựa trên mode
        if self.mode == "speed":
            display_value = value / 100.0  # Chuyển thành hệ số tốc độ (e.g., 0.5x, 1.5x)
            self.value_label.setText(f"{display_value:.1f}{self.unit}")
        else:  # Mặc định cho volume hoặc các mode khác
            self.value_label.setText(f"{value}{self.unit}")
        
        self.apply_slider_style(value)
        
        # Emit signal with the processed value
        processed_value = self.get_processed_value()
        self.value_changed.emit(processed_value)
    
    def apply_slider_style(self, value=None):
        """Apply style to slider"""
        if value is None:
            value = self.slider.value()
            
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 16px;
                background: {self.current_colors['shadow']};
                border-radius: 8px;
            }}
            QSlider::handle:horizontal {{
                image: url(./icon/dot.png);
                width: 60px;
                height: 60px;
                margin: -12px 0px;
            }}
            QSlider::sub-page:horizontal {{
                background: {self.current_colors['secondary']};
                border-radius: 8px;
                height: 10px;
            }}
        """)
    
    def update_slider_colors(self, colors):
        """Update slider colors when theme changes"""
        self.current_colors = colors
        self.apply_slider_style()
    
    def get_processed_value(self):
        """Return the processed value based on mode"""
        raw_value = self.slider.value()
        if self.mode == "speed":
            return raw_value / 100.0  # Trả về hệ số tốc độ (e.g., 0.5, 1.0, 2.0)
        elif self.mode == "volume":
            return raw_value / 100.0  # Trả về hệ số âm lượng (e.g., 0.0, 1.0, 2.0)
        return raw_value  # Trả về giá trị gốc cho các mode khác
    
    def set_value(self, value):
        """Set the slider to a specific value"""
        self.slider.setValue(int(value))  # Đảm bảo giá trị là số nguyên cho slider
    
    def get_raw_value(self):
        """Return the raw slider value"""
        return self.slider.value()