import os
import logging
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import QThread, pyqtSignal
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.system_renderwindow import RenderWindow
from screen.function.system.system_notiwindow import NotiWindow

class VideoToAudioWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, video_file, output_file):
        super().__init__()
        self.video_file = video_file
        self.output_file = output_file

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading video...", "3 seconds"),
                (40, "Extracting audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            # Bước 1: Chuẩn bị
            self.progress_updated.emit(0, "Preparing video...", "Calculating...")
            # Giả sử sử dụng ffmpeg để trích xuất âm thanh (cần cài đặt ffmpeg)
            import subprocess
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Bước 2: Trích xuất âm thanh
            cmd = [
                "ffmpeg", "-i", self.video_file, "-vn", "-acodec", "mp3",
                "-y", self.output_file  # -y để ghi đè nếu file đã tồn tại
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Bước 3: Giả lập xử lý (có thể bỏ qua nếu không cần thêm bước)
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Bước 4: Lưu file
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(self.output_file)

        except Exception as e:
            self.error.emit(f"Error extracting audio: {str(e)}")