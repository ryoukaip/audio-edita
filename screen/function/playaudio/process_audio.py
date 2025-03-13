import librosa
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class AudioLoadWorker(QThread):
    finished = pyqtSignal(str, tuple)  # Signal to emit when loading is complete
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            # Load audio với sr thấp hơn để giảm dữ liệu
            audio, sr = librosa.load(self.file_path, sr=22050, mono=True)
            
            # Giảm số lượng mẫu bằng cách lấy trung bình
            target_samples = 500
            samples_per_pixel = len(audio) // target_samples
            
            if samples_per_pixel > 1:
                waveform_data = np.array_split(audio, target_samples)
                waveform_data = [np.mean(np.abs(chunk)) for chunk in waveform_data]
            else:
                waveform_data = audio
                
            self.finished.emit(self.file_path, (waveform_data, sr))
        except Exception as e:
            print(f"Error loading audio: {e}")
            self.finished.emit(self.file_path, None)

def format_time(ms):
    """Format milliseconds to MM:SS string."""
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"

def is_audio_file(file_path):
    """Check if the file has a valid audio extension."""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
    return any(file_path.lower().endswith(ext) for ext in audio_extensions)