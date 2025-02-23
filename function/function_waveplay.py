import numpy as np
from PyQt5.QtCore import QTimer, QObject

class WavePlay(QObject):
    def __init__(self):
        super().__init__()
        # Animation parameters
        self.animation_step = 0
        self.base_multiplier = 1.0
        self.wave_intensity = 0.3  # Cường độ dao động
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.setInterval(8)  
        self.is_enabled = True # Cho phép hoặc tắt animation

    def set_enabled(self, enabled):
        """Enable or disable wave animation"""
        self.is_enabled = enabled
        if not enabled:
            self.stop_animation()
        elif self.parent() and getattr(self.parent(), 'is_playing', False):
            self.start_animation()

    def start_animation(self):
        self.timer.start()
        
    def stop_animation(self):
        self.timer.stop()
        
    def update_animation(self):
        self.animation_step += 1
        if self.animation_step >= 360:
            self.animation_step = 0
            
    def get_height_multiplier(self, bar_index):
        """Return height multiplier for a specific bar"""
        if not self.is_enabled:
            return 1.0
        
        phase = (bar_index * 10 + self.animation_step) % 360
        wave = np.sin(np.radians(phase))
        # Tạo hiệu ứng dao động quanh giá trị 1.0
        return 1.0 + (wave * self.wave_intensity)