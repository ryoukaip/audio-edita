import os
from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class Slider(QWidget):
    # Signal to notify when volume changes
    volume_changed = pyqtSignal(int)
    
    def __init__(self, font_family):
        super().__init__()
        self.font_family = font_family
        self.initUI()
    
    def initUI(self):
        # Create horizontal layout for volume controls
        volume_layout = QHBoxLayout(self)
        volume_layout.setContentsMargins(0, 0, 0, 0)

        # Add volume icon
        volume_icon_label = QLabel()
        volume_icon_pixmap = QPixmap("./icon/volume.png")
        volume_icon_label.setPixmap(volume_icon_pixmap.scaledToHeight(24, Qt.SmoothTransformation))
        volume_icon_label.setFixedSize(30, 30)
        volume_layout.addWidget(volume_icon_label)

        # Add volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)  # Default value is 100%
        self.apply_slider_style()
        self.volume_slider.valueChanged.connect(self.update_volume)
        volume_layout.addWidget(self.volume_slider)

        # Add percentage label
        self.volume_percentage_label = QLabel("100%")
        self.volume_percentage_label.setFont(QFont(self.font_family, 12))
        self.volume_percentage_label.setStyleSheet("color: white;")
        self.volume_percentage_label.setFixedWidth(50)
        self.volume_percentage_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        volume_layout.addWidget(self.volume_percentage_label)
    
    def update_volume(self, value):
        """Update volume percentage label when slider changes"""
        self.volume_percentage_label.setText(f"{value}%")
        
        # Change style based on current value
        self.apply_slider_style(value)
        
        # Emit the signal with the new value
        self.volume_changed.emit(value)
    
    def apply_slider_style(self, value=None):
        """Apply appropriate style to slider based on value"""
        if value is None:
            value = self.volume_slider.value()
            
        # Style the slider with custom handle that appears on top
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 16px;
                background: #3a4062;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal {
                image: url(./icon/dot.png);
                width: 60px;
                height: 60px;
                margin: -12px 0px; /* negative margin to raise the image above the groove */
            }
            
            QSlider::sub-page:horizontal {
                background: #7d8bd4;
                border-radius: 8px;
                height: 10px;
            }
        """)
    
    def get_volume_factor(self):
        """Return the volume factor (0.0 to 2.0)"""
        return self.volume_slider.value() / 100.0
    
    def set_volume(self, value):
        """Set the volume slider to a specific value"""
        self.volume_slider.setValue(value)