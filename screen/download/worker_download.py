import os
import re
from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL

class YouTubeValidator:
    """Lớp kiểm tra tính hợp lệ của URL YouTube"""
    def __init__(self):
        # Các mẫu regex cho các định dạng URL YouTube phổ biến
        self.patterns = [
            r'^(https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]{11}',  # PC: (https://)(www.)youtube.com/watch?v=...
            r'^(https?://)?youtu\.be/[\w-]{11}',  # Short link: (https://)youtu.be/...
            r'^(https?://)?(?:www\.)?youtube\.com/shorts/[\w-]{11}',  # YouTube Shorts
            r'^(https?://)?m\.youtube\.com/watch\?v=[\w-]{11}',  # Mobile: (https://)m.youtube.com/watch?v=...
            r'^(https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]{34}',  # Playlist (tạm thời không hỗ trợ)
        ]

    def is_valid_youtube_url(self, url):
        """Kiểm tra xem URL có phải là URL YouTube hợp lệ không"""
        if not url:
            return False, "URL is empty"
        
        # Chuẩn hóa URL bằng cách thêm https:// nếu thiếu giao thức
        normalized_url = url.strip()
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = 'https://' + normalized_url
        
        for pattern in self.patterns:
            if re.match(pattern, normalized_url):
                # Kiểm tra thêm xem có phải playlist không (chưa hỗ trợ)
                if "playlist" in normalized_url:
                    return False, "Playlists are not supported yet"
                return True, "Valid YouTube URL"
        
        return False, "Invalid YouTube URL or unsupported format"

    def normalize_url(self, url):
        """Chuẩn hóa URL để đảm bảo có giao thức"""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, youtube_url):
        super().__init__()
        self.youtube_url = youtube_url
        self.output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "download", "youtube")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.validator = YouTubeValidator()

    def run(self):
        """Hàm chạy trong luồng riêng để tải audio"""
        # Kiểm tra URL trước khi tải
        is_valid, message = self.validator.is_valid_youtube_url(self.youtube_url)
        if not is_valid:
            self.error.emit(message)
            return

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.progress_hook],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=True)
                file_name = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                file_size = os.path.getsize(file_name) / (1024 * 1024)
                self.finished.emit(os.path.basename(file_name), f"{file_size:.2f} MB")

        except Exception as e:
            self.error.emit(str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                self.progress.emit(percent)
        elif d['status'] == 'finished':
            self.progress.emit(100)