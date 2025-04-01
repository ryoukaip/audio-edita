import librosa
import numpy as np
import subprocess
import os
from PyQt5.QtCore import QThread, pyqtSignal

class AudioLoadWorker(QThread):
    finished = pyqtSignal(str, tuple, int)  # Đường dẫn file, waveform data, thời lượng (ms)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.temp_file = None
        
    def standardize_audio(self):
        """Chuẩn hóa tất cả file audio bằng FFmpeg."""
        self.temp_file = "temp_standardized_audio.mp3"
        standardize_cmd = [
            'ffmpeg', '-i', self.file_path, '-c:a', 'mp3', '-b:a', '128k', 
            '-ar', '44100', '-ac', '2', self.temp_file, '-y'
        ]
        try:
            result = subprocess.run(standardize_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not os.path.exists(self.temp_file):
                raise Exception(f"FFmpeg failed to create file: {result.stderr.decode()}")
            return self.temp_file
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.output.decode()}")
            return None

    def run(self):
        try:
            # Chuẩn hóa file audio
            standardized_file = self.standardize_audio()
            if not standardized_file:
                raise Exception("Failed to standardize audio file")
            
            # Dùng ffprobe để lấy thời lượng
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', standardized_file
            ]
            duration_output = subprocess.check_output(duration_cmd, universal_newlines=True).strip()
            duration_ms = int(float(duration_output) * 1000)
            
            # Load audio để tạo waveform
            audio, sr = librosa.load(standardized_file, sr=8000, mono=True)
            
            # Giảm số lượng mẫu
            target_samples = 50
            samples_per_pixel = len(audio) // target_samples
            
            if samples_per_pixel > 1:
                waveform_data = np.array_split(audio, target_samples)
                waveform_data = [np.mean(np.abs(chunk)) for chunk in waveform_data]
            else:
                waveform_data = audio
                
            print(f"Standardized file: {standardized_file}")  # Debug đường dẫn
            self.finished.emit(standardized_file, (waveform_data, sr), duration_ms)
        except Exception as e:
            print(f"Error loading audio: {e}")
            self.finished.emit(self.file_path, None, 0)
        # Không xóa file tạm ở đây nữa

def format_time(ms):
    """Format milliseconds to MM:SS string."""
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"

def is_audio_file(file_path):
    """Check if the file has a valid audio extension."""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
    return any(file_path.lower().endswith(ext) for ext in audio_extensions)