from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from screen.setting.setting_about import AboutTab
from screen.function.system.system_thememanager import ThemeManager

class CommunityBar(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager
        self.theme_manager.theme_changed.connect(self.update_theme_colors)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        # Button container
        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        self.button_layout.setSpacing(20)
        self.button_layout.addStretch()
        
        # Button configurations
        button_configs = [
            {"text": "store", "index": 0},
            {"text": "installed", "index": 1}
        ]
        
        # Button style templates
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
        
        # Create buttons
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
        
        # Moving indicator
        self.indicator = QWidget(button_container)
        self.indicator.setStyleSheet(f"background-color: {self.current_colors['primary']};")
        self.indicator.setFixedHeight(2)
        self.indicator.setFixedWidth(80)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.setup_pages(font_family)
        self.main_layout.addWidget(self.content_stack)
        
        # Initialize default state
        self.switch_page(0)
        self._initial_update_done = False
        self.buttons[0].installEventFilter(self)
    
    def setup_pages(self, font_family):
        # Store page
        self.store_page = self.create_placeholder_page("Store (Coming Soon)", font_family)
        self.content_stack.addWidget(self.store_page)
        
        # Installed page
        self.installed_page = self.create_placeholder_page("Installed (Coming Soon)", font_family)
        self.content_stack.addWidget(self.installed_page)
    
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
        # Switch content
        self.content_stack.setCurrentIndex(index)
        
        # Update button styles
        for i, button in enumerate(self.buttons):
            button.setStyleSheet(
                self.active_style_template.format(**self.current_colors) if i == index 
                else self.default_style_template.format(**self.current_colors)
            )
        
        # Move indicator
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
        
        # Cập nhật chỉ báo và các nhãn trong trang
        self.indicator.setStyleSheet(f"background-color: {self.current_colors['primary']};")
        self.store_page.layout().itemAt(0).widget().setStyleSheet(f"color: {self.current_colors['primary']};")
        self.installed_page.layout().itemAt(0).widget().setStyleSheet(f"color: {self.current_colors['primary']};")
    
    def eventFilter(self, obj, event):
        if obj in self.buttons and event.type() == event.Show and not self._initial_update_done:
            self.update_indicator_position(self.buttons.index(obj))
            self._initial_update_done = True
            self.buttons[0].removeEventFilter(self)
        return super().eventFilter(obj, event)