import json
import os
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal(dict)
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._initialized = True
        self.theme_name = "Theme 1"  # default
        self.settings_file = "flags.json"
        
        # Màu mặc định
        self.current_theme = {
            "primary": "#98a4e6",
            "secondary": "#7d8bd4",
            "background": "#474f7a",
            "highlight": "#6574c6",
            "shadow": "#3a4062",
            "dark": "#292d47"
        }
        
        # Load themes và theme đã chọn
        self.themes = self.load_themes()
        self.load_selected_theme()

    def load_themes(self):
        try:
            with open("themes.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Trả về theme mặc định nếu file không tồn tại hoặc không hợp lệ
            return {
                "Theme 1": self.current_theme,
                "Theme 2": {
                    "primary": "#5fbaa4",
                    "secondary": "#50a893",
                    "background": "#439b86",
                    "highlight": "#377f6e",
                    "shadow": "#317262",
                    "dark": "#193b33"
                },
                "Theme 3": {
                    "primary": "#11d7f9",
                    "secondary": "#059eb8",
                    "background": "#04899f",
                    "highlight": "#088395",
                    "shadow": "#047386",
                    "dark": "#035e6e"
                },
                "Theme 4": {
                    "primary": "#f15a3a",
                    "secondary": "#f14c28",
                    "background": "#cf310f",
                    "highlight": "#b72b0d",
                    "shadow": "#9f260c",
                    "dark": "#88200a"
                }
            }

    def load_selected_theme(self):
        if not os.path.exists(self.settings_file):
            self.set_theme(self.theme_name)
            return
            
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                saved_theme = settings.get('selected_theme')
                if saved_theme and saved_theme in self.themes:
                    self.set_theme(saved_theme, emit_signal=False)
                else:
                    self.set_theme(self.theme_name, emit_signal=False)
        except:
            self.set_theme(self.theme_name, emit_signal=False)

    def save_selected_theme(self):
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
                
        settings['selected_theme'] = self.theme_name
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def set_theme(self, theme_name, emit_signal=True):
        if theme_name in self.themes:
            self.theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            self.save_selected_theme()
            
            if emit_signal:
                self.theme_changed.emit(self.current_theme)
                
            print(f"Theme set to {self.theme_name}")
            return True
        else:
            print(f"Theme '{theme_name}' not found")
            return False

    def get_theme_name(self):
        return self.theme_name
    
    def get_theme_colors(self):
        return self.current_theme

    def reset_theme(self):
        return self.set_theme("Theme 1")
    
    def get_available_themes(self):
        return list(self.themes.keys())
    
    def update_theme_colors(self, colors):
        """Cập nhật màu theme hiện tại mà không thay đổi tên"""
        self.current_theme = colors
        self.theme_changed.emit(self.current_theme)