import os
import librosa
import soundfile as sf
from PyQt5.QtCore import QThread, pyqtSignal

class SplitWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str, str)  # Signal khi hoàn thành (đường dẫn file đầu ra 1 và 2)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, split_time):
        super().__init__()
        self.input_file = input_file
        self.split_time = split_time

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "3 seconds"),
                (40, "Splitting audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving files...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            total_duration = librosa.get_duration(y=audio, sr=sr)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Kiểm tra thời gian cắt
            if self.split_time >= total_duration or self.split_time <= 0:
                raise ValueError("Split time is out of bounds!")

            # Chuyển thời gian từ giây sang số mẫu
            split_samples = int(self.split_time * sr)

            # Cắt file âm thanh thành 2 phần
            part1 = audio[:split_samples]
            part2 = audio[split_samples:]
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Giả lập bước xử lý (nếu cần thêm logic sau này)
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "split")
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            file_ext = os.path.splitext(self.input_file)[1]

            output_file1 = os.path.join(output_dir, f"{base_name}_split_1{file_ext}")
            output_file2 = os.path.join(output_dir, f"{base_name}_split_2{file_ext}")

            sf.write(output_file1, part1, sr, format='WAV')
            sf.write(output_file2, part2, sr, format='WAV')
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file1, output_file2)

        except Exception as e:
            self.error.emit(str(e))