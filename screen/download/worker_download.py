import os
import re
from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL

class URLValidator:
    """Lớp kiểm tra tính hợp lệ của URL YouTube và TikTok"""
    def __init__(self):
        # Các mẫu regex cho URL YouTube và TikTok
        self.patterns = {
            'youtube': [
                r'^(https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]{11}',  # YouTube video
                r'^(https?://)?youtu\.be/[\w-]{11}',  # YouTube short link
                r'^(https?://)?(?:www\.)?youtube\.com/shorts/[\w-]{11}',  # YouTube Shorts
                r'^(https?://)?m\.youtube\.com/watch\?v=[\w-]{11}',  # YouTube mobile
                r'^(https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]{34}',  # YouTube playlist (không hỗ trợ)
            ],
            'tiktok': [
                r'^(https?://)?(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',  # TikTok video (tiktok.com/@username/video/id)
                r'^(https?://)?vm\.tiktok\.com/[\w-]+/?$',  # TikTok short link (vm.tiktok.com/...)
                r'^(https?://)?m\.tiktok\.com/v/\d+\.html',  # TikTok mobile link
            ]
        }

    def is_valid_url(self, url):
        """Kiểm tra xem URL có hợp lệ không và thuộc loại nào"""
        if not url:
            return False, "URL is empty", None
        
        # Chuẩn hóa URL
        normalized_url = self.normalize_url(url.strip())

        # Kiểm tra YouTube
        for pattern in self.patterns['youtube']:
            if re.match(pattern, normalized_url):
                if "playlist" in normalized_url:
                    return False, "YouTube playlists are not supported yet", 'youtube'
                return True, "Valid YouTube URL", 'youtube'

        # Kiểm tra TikTok
        for pattern in self.patterns['tiktok']:
            if re.match(pattern, normalized_url):
                return True, "Valid TikTok URL", 'tiktok'
        
        return False, "Invalid URL or unsupported format", None

    def normalize_url(self, url):
        """Chuẩn hóa URL để đảm bảo có giao thức"""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.validator = URLValidator()
        
        # Xác định thư mục lưu trữ dựa trên loại URL
        self.base_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "download")
        self.output_dir = None  # Sẽ được xác định sau khi kiểm tra URL

    def run(self):
        """Hàm chạy trong luồng riêng để tải audio"""
        # Kiểm tra URL
        is_valid, message, platform = self.validator.is_valid_url(self.url)
        if not is_valid:
            self.error.emit(message)
            return

        # Xác định thư mục lưu trữ dựa trên platform
        self.output_dir = os.path.join(self.base_dir, platform)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        try:
            # Cấu hình tải xuống chung cho cả YouTube và TikTok
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
                info = ydl.extract_info(self.url, download=True)
                file_name = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                file_size = os.path.getsize(file_name) / (1024 * 1024)
                self.finished.emit(os.path.basename(file_name), f"{file_size:.2f} MB")

        except Exception as e:
            self.error.emit(f"Download failed: {str(e)}")

    def progress_hook(self, d):
        """Cập nhật tiến trình tải"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                self.progress.emit(percent)
        elif d['status'] == 'finished':
            self.progress.emit(100)