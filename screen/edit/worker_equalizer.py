import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class EqualizerWorker(QThread):
   progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
   finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
   error = pyqtSignal(str)  # Signal khi có lỗi

   def __init__(self, input_file, eq_settings):
       super().__init__()
       self.input_file = input_file
       self.eq_settings = eq_settings  # Dictionary của các dải tần số và giá trị gain

   def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "3 seconds"),
                (40, "Applying equalizer...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Chuyển đổi sang miền tần số
            print("Step 2: Converting to frequency domain...")
            D = librosa.stft(audio)  # Mặc định n_fft=2048
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Áp dụng equalizer
            print("Step 3: Applying EQ settings...")
            # Sửa lại n_fft để khớp với STFT
            n_fft = 2048  # Giá trị mặc định của librosa.stft
            freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)  # Số bin = (n_fft // 2) + 1 = 1025
            
            # Tạo mảng gain cho mỗi bin tần số
            gains = np.ones(len(freqs))
            
            # Áp dụng gain cho mỗi dải tần số
            for freq, gain_db in self.eq_settings.items():
                print(f"Applying gain {gain_db} dB at {freq} Hz")
                # Chuyển đổi từ dB sang hệ số tuyến tính
                gain_linear = 10 ** (gain_db / 20.0)
                
                # Tính bandwidth
                if freq < 1000:
                    bandwidth = freq * 0.7
                else:
                    bandwidth = freq * 0.3
                
                # Tạo mặt nạ Gaussian
                mask = np.exp(-0.5 * ((freqs - freq) / bandwidth) ** 2)
                
                # Áp dụng gain
                gains = gains * (1 + mask * (gain_linear - 1))
            
            # Áp dụng gain vào STFT
            D_eq = D * gains[:, np.newaxis]
            
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Chuyển đổi ngược về miền thời gian
            print("Step 4: Converting back to time domain...")
            audio_eq = librosa.istft(D_eq, length=len(audio))

            # Tạo thư mục đầu ra và lưu file
            print("Step 5: Saving file...")
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "equalizer")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_eq.wav")
            sf.write(output_file, audio_eq, sr)
            print(f"File saved to: {output_file}")
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            self.error.emit(str(e))