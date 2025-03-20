import sys
import json
from PyQt5.QtWidgets import QApplication
from main_screen import AudioEditorUI
from welcome import WelcomeWindow
from screen.boot.boot import BootWindow

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.boot_window = None
        self.welcome_window = None
        self.flags = self.read_flags()

    def read_flags(self):
        """ Đọc file flags.json, nếu lỗi sẽ tạo file mặc định """
        try:
            with open("flags.json", "r") as file:
                flags = json.load(file)
                print("[DEBUG] Đọc flags.json:", flags)
                return flags
        except (FileNotFoundError, json.JSONDecodeError):
            default_flags = {
                "welcome_shown": False,
                "dark_mode": True,
                "auto_save": False,
                "last_used_format": "mp3"
            }
            with open("flags.json", "w") as file:
                json.dump(default_flags, file, indent=4)
            print("[DEBUG] flags.json không tồn tại hoặc lỗi, tạo file mới:", default_flags)
            return default_flags

    def update_flag(self, flag_name, value):
        """ Cập nhật giá trị của một flag và ghi vào file """
        self.flags[flag_name] = value
        with open("flags.json", "w") as file:
            json.dump(self.flags, file, indent=4)
        print(f"[DEBUG] Cập nhật flag {flag_name} = {value}")

    def show_boot_screen(self):
        """ Hiển thị BootWindow, khi đóng sẽ hiện main_window """
        print("[DEBUG] Khởi tạo BootWindow")
        self.boot_window = BootWindow()
        self.boot_window.show()
        self.boot_window.closed.connect(self.on_boot_closed)

    def on_boot_closed(self):
        print("[DEBUG] BootWindow đóng, hiển thị main_window")
        self.main_window.setWindowOpacity(1.0)
        self.boot_window = None

    def show_welcome_screen(self):
        print("[DEBUG] WelcomeWindow chưa hiển thị trước đó, tạo cửa sổ WelcomeWindow")
        self.welcome_window = WelcomeWindow(self.main_window)
        self.welcome_window.show()
        self.welcome_window.closed.connect(self.on_welcome_closed)

    def on_welcome_closed(self):
        print("[DEBUG] WelcomeWindow đóng, cập nhật flag welcome_shown")
        self.update_flag("welcome_shown", True)
        
        # Create and show boot window first
        print("[DEBUG] Khởi tạo BootWindow trước khi đóng WelcomeWindow")
        self.show_boot_screen()
        
        # Clean up welcome window reference after boot window is shown
        self.welcome_window = None

    def run(self):
        print("[DEBUG] Khởi động ứng dụng")
        print("[DEBUG] Khởi tạo main_window")
        self.main_window = AudioEditorUI()
        self.main_window.setWindowOpacity(0.0)
        self.main_window.show()

        if not self.flags.get("welcome_shown", False):
            self.show_welcome_screen()
        else:
            print("[DEBUG] WelcomeWindow đã hiển thị trước đó, mở BootWindow ngay lập tức")
            self.show_boot_screen()

        return self.app.exec_()

if __name__ == "__main__":
    app_manager = ApplicationManager()
    sys.exit(app_manager.run())