import os
import librosa
import soundfile as sf
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QComboBox, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal

class ConvertWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, output_format):
        super().__init__()
        self.input_file = input_file
        self.output_format = output_format.lower()

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (30, "Loading audio...", "3 seconds"),
                (60, "Converting format...", "2 seconds"),
                (90, "Saving file...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Giả lập bước chuyển đổi (thực tế chỉ cần lưu với định dạng mới)
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "convert")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_converted.{self.output_format}")
            sf.write(output_file, audio, sr, format=self.output_format)

            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Conversion complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))