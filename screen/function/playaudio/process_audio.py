import librosa
import numpy as np
import os
from PyQt5.QtCore import QThread, pyqtSignal
from screen.function.playaudio.function_standardize import standardize_audio, get_duration, is_audio_file

class AudioLoadWorker(QThread):
    finished = pyqtSignal(str, tuple, int, dict)  # Đường dẫn file, waveform data, thời lượng (ms), error_info
    progress = pyqtSignal(int)  # Signal để cập nhật tiến trình
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.temp_file = None
        
    def __del__(self):
        """Dọn dẹp file tạm khi worker bị hủy."""
        self.cleanup_temp_file()
        
    def cleanup_temp_file(self):
        """Xóa file tạm nếu tồn tại và khác với file gốc."""
        if self.temp_file and os.path.exists(self.temp_file) and self.temp_file != self.file_path:
            try:
                os.remove(self.temp_file)
                print(f"Cleaned up temp file: {self.temp_file}")
            except Exception as e:
                print(f"Could not remove temp file: {e}")
    
    def create_waveform(self, audio_file, target_samples=50):
        """Tạo waveform từ file audio."""
        try:
            # Load audio để tạo waveform
            audio, sr = librosa.load(audio_file, sr=8000, mono=True)
            
            # Báo tiến trình
            self.progress.emit(75)  # 75% hoàn thành
            
            # Giảm số lượng mẫu
            samples_per_pixel = len(audio) // target_samples
            
            if samples_per_pixel > 1:
                waveform_data = np.array_split(audio, target_samples)
                waveform_data = [np.mean(np.abs(chunk)) for chunk in waveform_data]
            else:
                waveform_data = audio
            
            self.progress.emit(90)  # 90% hoàn thành
            return (waveform_data, sr)
        except Exception as e:
            print(f"Error creating waveform: {e}")
            return None

    def run(self):
        error_info = {}
        try:
            self.progress.emit(0)  # Báo tiến trình bắt đầu
            
            # Kiểm tra file có tồn tại không
            if not os.path.exists(self.file_path):
                error_info = {'error': 'File does not exist', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
                
            # Kiểm tra file có phải audio không
            if not is_audio_file(self.file_path):
                error_info = {'error': 'Not a valid audio file', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
            
            # Chuẩn hóa file audio
            self.progress.emit(10)  # 10% hoàn thành
            standardized_file = standardize_audio(self.file_path)
            if not standardized_file:
                error_info = {'error': 'Failed to standardize audio file', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
            
            # Lưu lại đường dẫn file tạm để có thể xóa sau này
            self.temp_file = standardized_file
            
            self.progress.emit(50)  # 50% hoàn thành
            
            # Lấy thời lượng
            duration_ms = get_duration(standardized_file)
            
            # Tạo waveform
            waveform_data = self.create_waveform(standardized_file)
            if not waveform_data:
                error_info = {'error': 'Failed to create waveform', 'file_path': self.file_path}
                self.finished.emit(standardized_file, None, duration_ms, error_info)
                return
                
            self.progress.emit(100)  # 100% hoàn thành
            self.finished.emit(standardized_file, waveform_data, duration_ms, {})
        except Exception as e:
            error_info = {
                'error': str(e),
                'file_path': self.file_path,
                'file_exists': os.path.exists(self.file_path),
                'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
            }
            print(f"Error loading audio: {error_info}")
            self.finished.emit(self.file_path, None, 0, error_info)

def format_time(ms):
    """Format milliseconds to MM:SS string."""
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"