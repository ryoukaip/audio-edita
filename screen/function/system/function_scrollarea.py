from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtWidgets import QScrollArea
from screen.function.system.system_thememanager import ThemeManager

class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_alpha = 0
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_scrollbar_colors)
        
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.hide_scrollbar)
        self.fade_timer.setSingleShot(True)
        
        # Set base style
        self.base_style = """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        self.setStyleSheet(self.base_style)
        
        self.fade_animation = QPropertyAnimation(self, b"scroll_alpha")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Add smooth scroll animation
        self.scroll_animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.scroll_animation.setDuration(250)
        self.scroll_animation.setEasingCurve(QEasingCurve.OutExpo)
        self.scroll_step = 120
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Initialize scrollbar as hidden
        self.updateScrollBarStyle(0)

    @pyqtProperty(int)
    def scroll_alpha(self):
        return self._scroll_alpha

    @scroll_alpha.setter
    def scroll_alpha(self, value):
        self._scroll_alpha = value
        self.updateScrollBarStyle(value)

    def updateScrollBarStyle(self, alpha):
        style = f"""
            QScrollBar:vertical {{
                border: none;
                background: {self.current_colors['shadow'] + f', {alpha/255})'};
                width: 12px;
                margin: 15px 5px 15px 5px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.current_colors['secondary'] + f', {alpha/255})'};
                min-height: 30px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
        self.verticalScrollBar().setStyleSheet(style)

    def update_scrollbar_colors(self, colors):
        """Update scrollbar colors when theme changes"""
        self.current_colors = colors
        self.updateScrollBarStyle(self._scroll_alpha)

    def wheelEvent(self, event):
        # Cancel any ongoing scroll animation
        self.scroll_animation.stop()
        
        # Calculate target scroll position
        delta = event.angleDelta().y()
        delta = self.scroll_step if delta > 0 else -self.scroll_step
        
        current_value = self.verticalScrollBar().value()
        target_value = current_value - delta
        
        # Clamp target value within scrollbar range
        maximum = self.verticalScrollBar().maximum()
        minimum = self.verticalScrollBar().minimum()
        target_value = max(minimum, min(maximum, target_value))
        
        if target_value != current_value:
            self.scroll_animation.setStartValue(current_value)
            self.scroll_animation.setEndValue(target_value)
            self.scroll_animation.start()
            self.show_scrollbar()
        
        event.accept()
        
    def show_scrollbar(self):
        self.fade_timer.stop()
        self.fade_animation.stop()
        self.fade_animation.setStartValue(self._scroll_alpha)
        self.fade_animation.setEndValue(255)
        self.fade_animation.start()
        self.fade_timer.start(1000)
        
    def hide_scrollbar(self):
        self.fade_animation.setStartValue(self._scroll_alpha)
        self.fade_animation.setEndValue(0)
        self.fade_animation.start()

    def scroll_to_bottom(self):
        """Cuộn mượt mà xuống dưới cùng của scroll area"""
        scrollbar = self.verticalScrollBar()
        current_pos = scrollbar.value()
        target_pos = scrollbar.maximum()

        # Tạo animation mới để không xung đột với scroll_animation hiện có
        bottom_animation = QPropertyAnimation(scrollbar, b"value")
        bottom_animation.setDuration(500)
        bottom_animation.setStartValue(current_pos)
        bottom_animation.setEndValue(target_pos)
        bottom_animation.setEasingCurve(QEasingCurve.InOutQuad)

        def update_target():
            bottom_animation.setEndValue(scrollbar.maximum())
            bottom_animation.start()

        QTimer.singleShot(0, update_target)