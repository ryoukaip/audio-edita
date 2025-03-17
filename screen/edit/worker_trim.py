import os
import librosa
import soundfile as sf
from PyQt5.QtCore import QThread, pyqtSignal

class TrimWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, start_time, end_time):
        super().__init__()
        self.input_file = input_file
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "3 seconds"),
                (40, "Trimming audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            total_duration = librosa.get_duration(y=audio, sr=sr)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Xử lý trường hợp start_time > end_time bằng cách hoán đổi
            if self.start_time > self.end_time:
                self.start_time, self.end_time = self.end_time, self.start_time

            # Kiểm tra thời gian cắt có hợp lệ không
            if self.start_time < 0 or self.end_time > total_duration:
                raise ValueError("Trim times are out of bounds!")

            # Chuyển thời gian từ giây sang số mẫu
            start_samples = int(self.start_time * sr)
            end_samples = int(self.end_time * sr)

            # Cắt đoạn âm thanh
            trimmed_audio = audio[start_samples:end_samples]
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Giả lập bước xử lý (nếu cần thêm logic sau này)
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "trim")
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            file_ext = os.path.splitext(self.input_file)[1]

            output_file = os.path.join(output_dir, f"{base_name}_trimmed{file_ext}")
            sf.write(output_file, trimmed_audio, sr, format='WAV')
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))