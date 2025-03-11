import sys
import json
import os
from PyQt5.QtWidgets import QApplication
from main_screen import AudioEditorUI
from welcome import WelcomeWindow

def read_flags():
    try:
        with open("flags.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Tạo file mới với giá trị mặc định nếu không tồn tại hoặc lỗi
        default_flags = {
            "welcome_shown": False,
            # Thêm các flags khác ở đây nếu cần
            "dark_mode": True,
            "auto_save": False,
            "last_used_format": "mp3"
        }
        with open("flags.json", "w") as file:
            json.dump(default_flags, file, indent=4)
        return default_flags

def update_flag(flag_name, value):
    flags = read_flags()
    flags[flag_name] = value
    with open("flags.json", "w") as file:
        json.dump(flags, file, indent=4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = AudioEditorUI()
    main_window.setWindowOpacity(0.0)
    main_window.show()

    # Đọc flags từ file
    flags = read_flags()
    
    if not flags.get("welcome_shown", False):
        # Nếu chưa hiển thị welcome screen
        welcome = WelcomeWindow(main_window)
        welcome.show()
        
        # Kết nối sự kiện đóng welcome với việc cập nhật flag
        welcome.closed.connect(lambda: update_flag("welcome_shown", True))
    else:
        # Nếu đã hiển thị welcome screen trước đó
        main_window.setWindowOpacity(1.0)
    
    sys.exit(app.exec_())