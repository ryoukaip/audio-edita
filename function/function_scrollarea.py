from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtWidgets import QScrollArea

class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_alpha = 0
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
                background: rgba(40, 42, 50, {alpha/255});
                width: 12px;
                margin: 15px 5px 15px 5px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(71, 79, 122, {alpha/255});
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

    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.show_scrollbar()
        
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