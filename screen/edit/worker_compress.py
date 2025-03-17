import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

# Worker thread để xử lý nén âm thanh
class CompressWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, quality_factor):
        super().__init__()
        self.input_file = input_file
        self.quality_factor = quality_factor

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "3 seconds"),
                (40, "Compressing audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Ánh xạ chất lượng sang sample rate mới
            min_sr = 2000
            mid_sr = 11025
            max_sr = sr
            if self.quality_factor <= 1.0:
                new_sr = int(max_sr - (max_sr - mid_sr) * self.quality_factor)
            else:
                new_sr = int(mid_sr - (mid_sr - min_sr) * (self.quality_factor - 1.0))
            new_sr = max(min_sr, min(new_sr, max_sr))

            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Thay đổi sample rate nếu cần
            if new_sr != sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=new_sr)

            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "compress")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_compress_{int(self.quality_factor * 1)}%.wav")
            sf.write(output_file, audio, new_sr)

            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))