import os
import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from scipy.signal import butter, filtfilt
from PyQt5.QtCore import QThread, pyqtSignal

class NoiseWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_file, use_denoise=True):
        super().__init__()
        self.input_file = input_file
        self.use_denoise = use_denoise

    def run(self):
        try:
            self.progress_updated.emit(0, "Loading audio...", "3 seconds")

            # 🟢 BƯỚC 1: Chuẩn hóa âm lượng với PyDub
            audio_pydub = AudioSegment.from_file(self.input_file)
            audio_pydub = audio_pydub.normalize()
            temp_wav_path = "temp_processed.wav"
            audio_pydub.export(temp_wav_path, format="wav")

            # 🟢 BƯỚC 2: Đọc file đã chuẩn hóa với librosa
            audio, sr = librosa.load(temp_wav_path, sr=48000)

            self.progress_updated.emit(30, "Applying pre-filtering...", "3 seconds")

            # 🟢 BƯỚC 3: Áp dụng bộ lọc thông cao & thông thấp (High-pass + Low-pass)
            def bandpass_filter(data, lowcut=100, highcut=12000, sr=48000, order=6):
                nyquist = 0.5 * sr
                low = lowcut / nyquist
                high = highcut / nyquist
                b, a = butter(order, [low, high], btype='band')
                return filtfilt(b, a, data)

            audio_filtered = bandpass_filter(audio)

            self.progress_updated.emit(60, "Applying noise reduction...", "3 seconds")

            # 🟢 BƯỚC 4: Áp dụng Noisereduce (giữ nguyên thông số)
            if self.use_denoise:
                audio_denoised = nr.reduce_noise(
                    y=audio_filtered, sr=sr, 
                    prop_decrease=0.5,  
                    time_mask_smooth_ms=100,  
                    stationary=False  
                )
            else:
                audio_denoised = audio_filtered

            self.progress_updated.emit(90, "Saving file...", "2 seconds")

            # 🟢 BƯỚC 5: Lưu file đầu ra
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "noise")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_denoised.wav")
            sf.write(output_file, audio_denoised, sr)

            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
        finally:
            if os.path.exists("temp_processed.wav"): # Cleanup temporary file
                os.remove("temp_processed.wav")
