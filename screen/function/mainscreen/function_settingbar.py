from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from screen.setting.setting_about import AboutTab
from screen.setting.setting_theme import ThemeTab
from screen.function.system.system_thememanager import ThemeManager

class SettingBar(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        
        # Sử dụng ThemeManager thay vì tự quản lý colors
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager
        self.theme_manager.theme_changed.connect(self.update_theme_colors)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        self.button_layout.setSpacing(20)
        self.button_layout.addStretch()
        
        button_configs = [
            {"text": "general", "index": 0},
            {"text": "theme", "index": 1},
            {"text": "about", "index": 2}
        ]
        
        self.default_style_template = """
            QPushButton {{
                background: transparent; 
                color: white;
                padding: 10px 15px;
                border: none;
            }}
            QPushButton:hover {{
                color: {primary};
            }}
        """
        
        self.active_style_template = """
            QPushButton {{
                background: transparent; 
                color: {primary};
                padding: 10px 15px;
                border: none;
            }}
        """
        
        self.buttons = []
        for config in button_configs:
            button = QPushButton(config["text"])
            button.setFont(QFont(font_family, 12))
            button.setStyleSheet(self.default_style_template.format(**self.current_colors))
            button.clicked.connect(lambda checked, idx=config["index"]: self.switch_page(idx))
            self.buttons.append(button)
            self.button_layout.addWidget(button)
        
        self.button_layout.addStretch()
        self.main_layout.addWidget(button_container)
        
        self.indicator = QWidget(button_container)
        self.indicator.setStyleSheet(f"background-color: {self.current_colors['primary']};")
        self.indicator.setFixedHeight(2)
        self.indicator.setFixedWidth(80)
        
        self.content_stack = QStackedWidget()
        self.setup_pages(font_family)
        self.main_layout.addWidget(self.content_stack)
        
        self.switch_page(0)
        self._initial_update_done = False
        self.buttons[0].installEventFilter(self)
    
    def setup_pages(self, font_family):
        self.general_page = self.create_placeholder_page("General Settings (Coming Soon)", font_family)
        self.content_stack.addWidget(self.general_page)
        
        # Chỉ truyền font_family cho ThemeTab, không cần kết nối tín hiệu
        self.theme_page = ThemeTab(font_family)
        self.content_stack.addWidget(self.theme_page)
        
        self.about_page = AboutTab(font_family)
        self.content_stack.addWidget(self.about_page)
    
    def create_placeholder_page(self, text, font_family):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(text)
        label.setFont(QFont(font_family, 12))
        label.setStyleSheet(f"color: {self.current_colors['primary']};")
        layout.addWidget(label)
        return page
    
    def update_indicator_position(self, index):
        button = self.buttons[index]
        button_rect = button.geometry()
        indicator_x = button_rect.center().x() - self.indicator.width() // 2
        pos_y = button_rect.bottom()
        self.indicator.setGeometry(indicator_x, pos_y, self.indicator.width(), 2)
        self.indicator.raise_()
    
    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, button in enumerate(self.buttons):
            button.setStyleSheet(
                self.active_style_template.format(**self.current_colors) if i == index 
                else self.default_style_template.format(**self.current_colors)
            )
        self.update_indicator_position(index)
    
    def update_theme_colors(self, colors):
        # Cập nhật màu sắc khi nhận tín hiệu từ ThemeManager
        self.current_colors = colors
        current_index = self.content_stack.currentIndex()
        
        # Cập nhật giao diện cho các nút
        for i, button in enumerate(self.buttons):
            button.setStyleSheet(
                self.active_style_template.format(**self.current_colors) if i == current_index 
                else self.default_style_template.format(**self.current_colors)
            )
        
        # Cập nhật chỉ báo và các phần tử khác
        self.indicator.setStyleSheet(f"background-color: {self.current_colors['primary']};")
        self.general_page.layout().itemAt(0).widget().setStyleSheet(f"color: {self.current_colors['primary']};")
    
    def eventFilter(self, obj, event):
        if obj in self.buttons and event.type() == event.Show and not self._initial_update_done:
            self.update_indicator_position(self.buttons.index(obj))
            self._initial_update_done = True
            self.buttons[0].removeEventFilter(self)
        return super().eventFilter(obj, event)