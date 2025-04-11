import json
import os
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont

class ThemeTab(QWidget):
    theme_changed = pyqtSignal(dict)  # Tín hiệu gửi dict chứa các màu

    def __init__(self, font_family="Arial", parent=None): 
        super().__init__(parent)  
        self.font_family = font_family
        self.settings_file = "flags.json"
        self.load_themes()
        self.init_ui() 

    def load_themes(self):
        with open('themes.json', 'r') as f:
            self.themes = json.load(f)
        
        # Load saved theme selection if it exists
        self.selected_theme = self.load_selected_theme()
        if not self.selected_theme or self.selected_theme not in self.themes:
            self.selected_theme = "Theme 1"  # Default theme

    def load_selected_theme(self):
        if not os.path.exists(self.settings_file):
            return None
            
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get('selected_theme')
        except:
            return None

    def save_selected_theme(self, theme_name):
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
                
        settings['selected_theme'] = theme_name
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def init_ui(self):
        # Main layout with similar margins as menu_check.py
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 0, 12, 12)
        main_layout.setSpacing(15)
        
        # Container widget
        container = QWidget()
        
        # Use HBoxLayout to arrange buttons horizontally
        hbox_layout = QHBoxLayout(container)
        hbox_layout.setContentsMargins(20, 20, 20, 20)
        hbox_layout.setSpacing(15)
        hbox_layout.setAlignment(Qt.AlignCenter)
        
        self.theme_buttons = {}

        # Add all buttons in one row
        for name, colors in self.themes.items():
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
            btn.clicked.connect(lambda checked, c=colors, n=name: self.select_theme(c, n))
            hbox_layout.addWidget(btn)
            self.theme_buttons[name] = btn

        # Add container to main layout with alignment
        main_layout.addWidget(container, alignment=Qt.AlignCenter)
        main_layout.addStretch()  # Push buttons up when window expands

        # Apply the saved theme
        self.select_theme(self.themes[self.selected_theme], self.selected_theme, initial=True)
        QTimer.singleShot(100, lambda: self.theme_changed.emit(self.themes[self.selected_theme]))

    def select_theme(self, colors, theme_name, initial=False):
        if self.selected_theme == theme_name and not initial:
            return

        if self.selected_theme and not initial:
            prev_btn = self.theme_buttons[self.selected_theme]
            prev_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.themes[self.selected_theme]['primary']};
                    border-radius: 15px;
                    border: 3px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {self.themes[self.selected_theme]['primary']};
                    border: 3px solid #FBFFE4;
                }}
            """)

        selected_btn = self.theme_buttons[theme_name]
        selected_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                border-radius: 15px;
                border: 3px solid #FBFFE4;
            }}
        """)

        self.selected_theme = theme_name
        
        # Save the selected theme to persist between application restarts
        self.save_selected_theme(theme_name)
        
        # Phát tín hiệu với các màu mới
        self.theme_changed.emit(colors)
        print(f"Selected theme: {theme_name} - {colors['primary']}")