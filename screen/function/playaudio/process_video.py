import os
import subprocess
import tempfile
import librosa
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class VideoLoadWorker(QThread):
    finished = pyqtSignal(str, tuple, int)  # Thêm thời lượng (ms) vào tín hiệu
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.temp_audio_path = None
        
    def run(self):
        try:
            fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            self.temp_audio_path = temp_path

            # Lấy thời lượng video gốc bằng FFprobe
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', self.file_path
            ]
            duration_output = subprocess.check_output(duration_cmd, universal_newlines=True).strip()
            duration_sec = float(duration_output)
            duration_ms = int(duration_sec * 1000)
            print(f"Video original duration (FFprobe): {duration_sec} seconds")  # Debug

            # Trích xuất âm thanh với thời lượng chính xác
            command = [
                'ffmpeg', '-i', self.file_path, 
                '-q:a', '0', '-map', 'a', 
                '-t', str(duration_sec),  # Ép thời lượng khớp video gốc
                '-y', self.temp_audio_path
            ]
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
            
            print(f"Temp audio file duration (FFprobe): {duration_sec} seconds")  # Debug
            
            audio, sr = librosa.load(self.temp_audio_path, sr=22050, mono=True)
            target_samples = 500
            samples_per_pixel = len(audio) // target_samples
            
            if samples_per_pixel > 1:
                waveform_data = np.array_split(audio, target_samples)
                waveform_data = [np.mean(np.abs(chunk)) for chunk in waveform_data]
            else:
                waveform_data = audio
            
            self.finished.emit(self.temp_audio_path, (waveform_data, sr), duration_ms)
            
        except Exception as e:
            print(f"Error processing video: {e}")
            self.finished.emit(self.file_path, None, 0)

def format_time(ms):
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"

def is_video_file(file_path):
    video_extensions = {'.mp4', '.mkv', '.mov', '.flv', '.avi'}
    return any(file_path.lower().endswith(ext) for ext in video_extensions)