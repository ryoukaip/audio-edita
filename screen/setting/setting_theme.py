from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from screen.function.system.system_thememanager import ThemeManager

class ThemeTab(QWidget):
    def __init__(self, font_family="Arial", parent=None): 
        super().__init__(parent)  
        self.font_family = font_family
        self.theme_manager = ThemeManager()
        self.init_ui() 

    def init_ui(self):
        # Main layout with similar margins as menu_check.py
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 0, 12, 12)
        main_layout.setSpacing(15)
        
        # Container widget
        container = QWidget()
        
        hbox_layout = QHBoxLayout(container)
        hbox_layout.setContentsMargins(20, 20, 20, 20)
        hbox_layout.setSpacing(15)
        hbox_layout.setAlignment(Qt.AlignCenter)
        
        self.theme_buttons = {}

        # Add all buttons in one row
        for name, colors in self.theme_manager.themes.items():
            btn = QPushButton()
            btn.setFixedSize(110, 110)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    border-radius: 15px;
                    border: 3px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary']};
                    border: 3px solid #FBFFE4;
                }}
            """)
            btn.clicked.connect(lambda checked, n=name: self.select_theme(n))
            hbox_layout.addWidget(btn)
            self.theme_buttons[name] = btn

        main_layout.addWidget(container, alignment=Qt.AlignCenter)
        main_layout.addStretch()  

        # Highlight current selected theme
        self.update_button_styles()

    def update_button_styles(self):
        selected_theme = self.theme_manager.get_theme_name()
        
        for name, btn in self.theme_buttons.items():
            colors = self.theme_manager.themes[name]
            if name == selected_theme:
                # Highlight selected theme
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['primary']};
                        border-radius: 15px;
                        border: 3px solid #FBFFE4;
                    }}
                """)
            else:
                # Regular style for non-selected themes
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['primary']};
                        border-radius: 15px;
                        border: 3px solid transparent;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['primary']};
                        border: 3px solid #FBFFE4;
                    }}
                """)

    def select_theme(self, theme_name):
        current_theme = self.theme_manager.get_theme_name()
        if current_theme == theme_name:
            return
            
        self.theme_manager.set_theme(theme_name)
        self.update_button_styles()