import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class VolumeWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, volume_factor):
        super().__init__()
        self.input_file = input_file
        self.volume_factor = volume_factor

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "5 seconds"),
                (40, "Adjusting volume...", "4 seconds"),
                (60, "Normalizing audio...", "3 seconds"),
                (80, "Saving file...", "2 seconds"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Điều chỉnh âm lượng
            adjusted_audio = audio * self.volume_factor
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Chuẩn hóa nếu âm lượng vượt quá giới hạn
            if np.max(np.abs(adjusted_audio)) > 1.0:
                adjusted_audio = adjusted_audio / np.max(np.abs(adjusted_audio))
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "volume")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_volume_{int(self.volume_factor * 100)}%.wav")
            sf.write(output_file, adjusted_audio, sr)

            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))