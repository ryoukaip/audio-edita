import librosa
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, pyqtProperty, QTimer

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = None
        self.prev_waveform_data = None
        self.animation_progress = 0.0
        self.progress = 0
        self.current_magnitudes = None
        self.target_magnitudes = None
        self.setMinimumHeight(190)
        self.animations = QParallelAnimationGroup()

    @pyqtProperty(float)
    def transition_progress(self):
        return self.animation_progress
        
    @transition_progress.setter
    def transition_progress(self, value):
        self.animation_progress = value
        self.update()
        
    def load_audio(self, file_path):
        try:
            # Store current waveform data as previous
            if self.waveform_data is not None:
                self.prev_waveform_data = self.waveform_data.copy()
            
            # Load audio với sr thấp hơn để giảm dữ liệu
            audio, sr = librosa.load(file_path, sr=1000, mono=True)
            
            # Giảm số lượng mẫu bằng cách lấy trung bình
            target_samples = 500  # Số lượng mẫu mong muốn
            samples_per_pixel = len(audio) // target_samples
            
            if samples_per_pixel > 1:
                self.waveform_data = np.array_split(audio, target_samples)
                self.waveform_data = [np.mean(np.abs(chunk)) for chunk in self.waveform_data]
            else:
                self.waveform_data = audio
                
            # Create transition animation
            self.start_transition_animation()

        except Exception as e:
            print(f"Error loading audio: {e}")
            self.waveform_data = None

    def start_transition_animation(self):
        # Clear any existing animations
        self.animations.clear()
        
        # Create new animation for transition
        animation = QPropertyAnimation(self, b"transition_progress")
        animation.setDuration(300)  # 300ms duration
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations.addAnimation(animation)
        self.animations.start()

    def set_progress(self, progress):
        """Set playback progress (0-100)"""
        self.progress = progress
        self.update()

    def set_playing(self, is_playing):
        """Set the playing state of the waveform."""
        self.is_playing = is_playing
        self.update()

    def set_waveform_data(self, waveform_data):
        if self.waveform_data is not None:
            self.prev_waveform_data = self.waveform_data.copy()
        self.waveform_data = waveform_data
        self.start_transition_animation()

    def paintEvent(self, event):
        if not self.waveform_data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Tính toán các thông số một lần
        center_y = self.height() // 2
        width = self.width()
        samples = len(self.waveform_data)
        gap = 22
        
        # Tính số lượng vạch cần vẽ
        num_bars = width // gap
        
        # Tính khoảng cách giữa các mẫu
        sample_step = samples // num_bars
        
        for i in range(num_bars):
            x = i * gap
            # Lấy giá trị trung bình của một nhóm mẫu
            start_idx = i * sample_step
            end_idx = min((i + 1) * sample_step, samples)
            magnitude = np.mean(self.waveform_data[start_idx:end_idx])
            
            # If we have previous data, interpolate between old and new values
            if self.prev_waveform_data is not None:
                prev_magnitude = np.mean(self.prev_waveform_data[start_idx:end_idx])
                magnitude = prev_magnitude + (magnitude - prev_magnitude) * self.animation_progress
            
            height = int(200 * magnitude)
            if height < 2:
                height = 2
                
            pen = QPen(QColor("#FBFFE4"), 8)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(x, center_y + height, x, center_y - height)