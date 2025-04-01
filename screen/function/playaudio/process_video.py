import os
import subprocess
import tempfile
import uuid
import librosa
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from screen.function.playaudio.function_standardize import standardize_audio, get_duration

class VideoLoadWorker(QThread):
    finished = pyqtSignal(str, tuple, int, dict)  # Đường dẫn file, waveform data, thời lượng (ms), error_info
    progress = pyqtSignal(int)  # Signal để cập nhật tiến trình
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.temp_audio_path = None
        
    def __del__(self):
        """Dọn dẹp file tạm khi worker bị hủy."""
        self.cleanup_temp_file()
        
    def cleanup_temp_file(self):
        """Xóa file tạm nếu tồn tại."""
        if self.temp_audio_path and os.path.exists(self.temp_audio_path):
            try:
                os.remove(self.temp_audio_path)
                print(f"Cleaned up temp file: {self.temp_audio_path}")
            except Exception as e:
                print(f"Could not remove temp file: {e}")
    
    def extract_audio(self):
        """Trích xuất âm thanh từ video và trả về đường dẫn file tạm."""
        try:
            # Tạo tên file tạm duy nhất
            temp_dir = tempfile.gettempdir()
            unique_id = str(uuid.uuid4())[:8]
            temp_path = os.path.join(temp_dir, f"vid_audio_{unique_id}.mp3")
            self.temp_audio_path = temp_path

            # Trích xuất âm thanh 
            command = ['ffmpeg', '-i', self.file_path, '-vn', '-q:a', '0', '-map', 'a', '-y', temp_path]
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
            
            if os.path.exists(temp_path):
                print(f"Audio extraction successful: {temp_path}")
                return temp_path
            else:
                print("Audio extraction failed: Output file not created")
                return None
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None
            
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
                
            # Kiểm tra file có phải video không
            if not is_video_file(self.file_path):
                error_info = {'error': 'Not a valid video file', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
            
            # Trích xuất audio từ video
            self.progress.emit(10)  # 10% hoàn thành
            extracted_audio = self.extract_audio()
            if not extracted_audio:
                error_info = {'error': 'Failed to extract audio from video', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
            
            self.progress.emit(30)  # 30% hoàn thành
            
            # Chuẩn hóa file audio đã trích xuất
            standardized_audio = standardize_audio(extracted_audio)
            if not standardized_audio:
                error_info = {'error': 'Failed to standardize audio', 'file_path': self.file_path}
                self.finished.emit(self.file_path, None, 0, error_info)
                return
                
            # Xóa file audio đã trích xuất nếu nó khác với file chuẩn hóa
            if standardized_audio != extracted_audio and os.path.exists(extracted_audio):
                try:
                    os.remove(extracted_audio)
                    print(f"Removed original extracted audio: {extracted_audio}")
                except Exception as e:
                    print(f"Could not remove original extracted audio: {e}")
            
            # Cập nhật đường dẫn file tạm
            self.temp_audio_path = standardized_audio
            
            self.progress.emit(50)  # 50% hoàn thành
            
            # Lấy thời lượng
            duration_ms = get_duration(standardized_audio)
            
            # Tạo waveform
            waveform_data = self.create_waveform(standardized_audio)
            if not waveform_data:
                error_info = {'error': 'Failed to create waveform', 'file_path': self.file_path}
                self.finished.emit(standardized_audio, None, duration_ms, error_info)
                return
                
            self.progress.emit(100)  # 100% hoàn thành
            self.finished.emit(standardized_audio, waveform_data, duration_ms, {})
        except Exception as e:
            error_info = {
                'error': str(e),
                'file_path': self.file_path,
                'file_exists': os.path.exists(self.file_path),
                'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
            }
            print(f"Error processing video: {error_info}")
            self.finished.emit(self.file_path, None, 0, error_info)

def format_time(ms):
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"

def is_video_file(file_path):
    video_extensions = {'.mp4', '.mkv', '.mov', '.flv', '.avi', '.wmv', '.webm', '.mpg', '.mpeg', '.m4v'}
    return any(file_path.lower().endswith(ext) for ext in video_extensions)