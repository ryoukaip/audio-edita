# ./screen/function/system/function_datamanager.py
import os

class AudioDataManager:
    def __init__(self):
        # Đường dẫn thư mục tạm
        self.temp_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "temp")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)  # Tạo thư mục nếu chưa tồn tại
        self.current_audio_file = None  # Lưu trữ tệp âm thanh hiện tại

    def set_audio_file(self, file_path):
        """Lưu tệp âm thanh được chọn."""
        self.current_audio_file = file_path

    def get_audio_file(self):
        """Lấy tệp âm thanh hiện tại."""
        return self.current_audio_file

    def get_temp_dir(self):
        """Lấy đường dẫn thư mục tạm."""
        return self.temp_dir

    def clear_audio_file(self):
        """Xóa tệp âm thanh hiện tại."""
        self.current_audio_file = None