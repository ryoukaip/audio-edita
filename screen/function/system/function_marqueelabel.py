from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter

class MarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.text_width = 0
        self.label_width = 0
        self.animation_offset = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(30)  # 30ms timer interval
        self.animation_active = False
        self.pause_time = 2000  # 2 seconds pause at start and end
        self.pause_counter = 0
        self.direction = 1  # 1 = move left, -1 = move right
        self.margin = 10  # Pixel margin
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(100)
        
    def setText(self, text):
        super().setText(text)
        self.check_text_width()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.label_width = self.width()
        self.check_text_width()
        
    def check_text_width(self):
        self.text_width = self.fontMetrics().horizontalAdvance(self.text())
        
        # Only animate if text is wider than the label
        if self.text_width > self.width() - self.margin * 2:
            if not self.animation_active:
                self.animation_active = True
                self.animation_offset = 0
                self.pause_counter = self.pause_time
                self.direction = 1
                self.animation_timer.start()
        else:
            if self.animation_active:
                self.animation_active = False
                self.animation_timer.stop()
                self.animation_offset = 0
                self.update()
    
    def update_animation(self):
        if self.pause_counter > 0:
            self.pause_counter -= self.animation_timer.interval()
            return
            
        self.animation_offset += self.direction
        
        # If text is fully moved to the left
        if self.direction == 1 and self.animation_offset >= self.text_width - self.width() + self.margin * 2:
            self.direction = -1
            self.pause_counter = self.pause_time
        
        # If text is back to the start position
        elif self.direction == -1 and self.animation_offset <= 0:
            self.direction = 1
            self.pause_counter = self.pause_time
            self.animation_offset = 0
            
        self.update()
        
    def paintEvent(self, event):
        if not self.animation_active:
            super().paintEvent(event)
            return
            
        painter = QPainter(self)
        
        # Set clipping to the widget's rectangle
        painter.setClipRect(self.rect())
        
        # Move the text position based on the current animation offset
        text_position = QPoint(self.margin - self.animation_offset, self.height() // 2 + self.fontMetrics().ascent() // 2)
        
        # Draw the text
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(text_position, self.text())