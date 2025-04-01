import os
import subprocess
import tempfile
import uuid

def get_audio_info(file_path):
    """Lấy thông tin về định dạng file audio hiện tại."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_name,sample_rate,channels', '-of', 
        'default=noprint_wrappers=1', file_path
    ]
    try:
        info = subprocess.check_output(cmd, universal_newlines=True)
        return info
    except Exception as e:
        print(f"Could not get audio info: {e}")
        return None

def should_standardize(file_path):
    """Quyết định xem có cần chuẩn hóa không."""
    audio_info = get_audio_info(file_path)
    
    if not audio_info:
        return True  # Không đọc được info -> cần chuẩn hóa
        
    # Kiểm tra các tiêu chí cần chuẩn hóa
    need_standardize = False
    if "codec_name=mp3" not in audio_info:
        need_standardize = True
    if "sample_rate=44100" not in audio_info:
        need_standardize = True
    if "channels=2" not in audio_info:
        need_standardize = True
    
    # Kiểm tra xem file có metadata hoặc album cover không
    has_metadata = check_for_metadata(file_path)
    if has_metadata:
        return True  # Cần chuẩn hóa nếu có metadata phức tạp
        
    return need_standardize

def check_for_metadata(file_path):
    """Kiểm tra file có chứa metadata phức tạp hoặc album cover không."""
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
        'stream=codec_type', '-of', 'default=noprint_wrappers=1', file_path
    ]
    try:
        # Kiểm tra xem có stream video nào không (album cover thường được lưu dưới dạng stream video)
        result = subprocess.check_output(cmd, universal_newlines=True)
        if "codec_type=video" in result:
            print(f"File {file_path} contains album cover or video stream")
            return True
            
        # Kiểm tra metadata
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format_tags', 
            '-of', 'default=noprint_wrappers=1', file_path
        ]
        metadata = subprocess.check_output(cmd, universal_newlines=True)
        # Kiểm tra kích thước metadata
        if len(metadata) > 500:  # Ngưỡng tùy chỉnh
            print(f"File {file_path} contains complex metadata")
            return True
            
        return False
    except Exception as e:
        print(f"Error checking metadata: {e}")
        return True  # Nếu không kiểm tra được, giả định cần chuẩn hóa

def _try_standardize_default(file_path, temp_file):
    """Phương pháp chuẩn hóa mặc định."""
    standardize_cmd = [
        'ffmpeg', '-i', file_path, '-c:a', 'mp3', '-b:a', '128k', 
        '-ar', '44100', '-ac', '2', '-map', '0:a', temp_file, '-y'
    ]
    try:
        result = subprocess.run(standardize_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_file):
            print("Standard conversion successful")
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Standard conversion failed: {e.stderr.decode()}")
        return False

def _try_standardize_alternative(file_path, temp_file):
    """Phương pháp chuẩn hóa thay thế với tùy chọn loại bỏ metadata."""
    standardize_cmd = [
        'ffmpeg', '-i', file_path, '-c:a', 'libmp3lame', '-q:a', '4', 
        '-ar', '44100', '-ac', '2', '-map_metadata', '-1', '-map', '0:a', temp_file, '-y'
    ]
    try:
        result = subprocess.run(standardize_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_file):
            print("Alternative conversion successful")
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Alternative conversion failed: {e.stderr.decode()}")
        return False

def _try_standardize_aggressive(file_path, temp_file):
    """Phương pháp chuẩn hóa quyết liệt nhất - decode hoàn toàn và encode lại."""
    standardize_cmd = [
        'ffmpeg', '-i', file_path, '-vn', '-acodec', 'pcm_s16le', '-f', 'wav', '-',
        '|', 'ffmpeg', '-i', '-', '-c:a', 'mp3', '-b:a', '128k', 
        '-ar', '44100', '-ac', '2', temp_file, '-y'
    ]
    try:
        # Sử dụng shell=True để chạy pipeline
        result = subprocess.run(' '.join(standardize_cmd), check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_file):
            print("Aggressive conversion successful")
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Aggressive conversion failed: {e.stderr.decode()}")
        try:
            # Thử một cách khác nếu pipeline thất bại
            print("Trying two-step conversion...")
            temp_wav = f"{temp_file}.wav"
            cmd1 = ['ffmpeg', '-i', file_path, '-vn', '-acodec', 'pcm_s16le', temp_wav, '-y']
            cmd2 = ['ffmpeg', '-i', temp_wav, '-c:a', 'mp3', '-b:a', '128k', '-ar', '44100', '-ac', '2', temp_file, '-y']
            
            subprocess.run(cmd1, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(cmd2, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            if os.path.exists(temp_file):
                print("Two-step conversion successful")
                return True
            return False
        except Exception as e2:
            print(f"Two-step conversion failed: {e2}")
            return False

def standardize_audio(file_path):
    """Chuẩn hóa file audio bằng FFmpeg, trả về đường dẫn đến file đã chuẩn hóa."""
    # Kiểm tra thông tin audio
    if not should_standardize(file_path):
        print(f"File already standardized: {file_path}")
        return file_path  # Trả về file gốc nếu đã chuẩn
    
    # Tạo tên file tạm duy nhất
    temp_dir = tempfile.gettempdir()
    unique_id = str(uuid.uuid4())[:8]
    temp_file = os.path.join(temp_dir, f"std_audio_{unique_id}.mp3")
    
    # Thử các phương pháp chuẩn hóa
    if _try_standardize_default(file_path, temp_file):
        return temp_file
        
    if _try_standardize_alternative(file_path, temp_file):
        return temp_file
        
    if _try_standardize_aggressive(file_path, temp_file):
        return temp_file
    
    # Phương pháp cuối cùng: chỉ trích xuất stream audio, loại bỏ hoàn toàn metadata
    try:
        print("Trying last resort method...")
        last_resort_cmd = [
            'ffmpeg', '-i', file_path, '-vn', '-acodec', 'libmp3lame',
            '-q:a', '2', '-ar', '44100', '-ac', '2', '-map_metadata', '-1',
            '-map', '0:a:0', temp_file, '-y'
        ]
        subprocess.run(last_resort_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_file):
            print("Last resort conversion successful")
            return temp_file
    except Exception as e:
        print(f"Last resort conversion failed: {e}")
        
    return None  # Nếu tất cả phương pháp đều thất bại

def get_duration(audio_file):
    """Dùng ffprobe để lấy thời lượng file audio."""
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_file
    ]
    try:
        duration_output = subprocess.check_output(duration_cmd, universal_newlines=True).strip()
        duration_ms = int(float(duration_output) * 1000)
        return duration_ms
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0

def check_ffmpeg():
    """Kiểm tra xem FFmpeg đã được cài đặt chưa."""
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def is_audio_file(file_path):
    """Check if the file has a valid audio extension."""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
    return any(file_path.lower().endswith(ext) for ext in audio_extensions)

def cleanup_temp_files(max_age_hours=24):
    """Xóa các file tạm cũ hơn n giờ."""
    import time
    import glob
    
    temp_dir = tempfile.gettempdir()
    pattern = os.path.join(temp_dir, "std_audio_*.mp3")
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for file_path in glob.glob(pattern):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    print(f"Removed old temp file: {file_path}")
                except Exception as e:
                    print(f"Could not remove temp file {file_path}: {e}")
    except Exception as e:
        print(f"Error during temp file cleanup: {e}")