import os
import re
from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL

class URLValidator:
    """Lớp kiểm tra tính hợp lệ của URL từ nhiều nền tảng"""
    def __init__(self):
        self.patterns = {
            'youtube': [
                r'^(https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]{11}',
                r'^(https?://)?youtu\.be/[\w-]{11}',
                r'^(https?://)?(?:www\.)?youtube\.com/shorts/[\w-]{11}',
                r'^(https?://)?m\.youtube\.com/watch\?v=[\w-]{11}',
                r'^(https?://)?(?:www\.)?music\.youtube\.com/watch\?v=[\w-]{11}',
                r'^(https?://)?music\.youtube\.com/playlist\?list=[\w-]+',
                r'^(https?://)?(?:www\.)?music\.youtube\.com/watch\?v=[\w-]{11}(?:&[\w=-]+)+',
            ],
            'tiktok': [
                r'^(https?://)?(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
                r'^(https?://)?vm\.tiktok\.com/[\w-]+/?$',
                r'^(https?://)?m\.tiktok\.com/v/\d+\.html',
            ],
            'facebook': [
                r'^(https?://)?(?:www\.)?facebook\.com/.*/videos/\d+',
                r'^(https?://)?(?:www\.)?fb\.watch/[\w-]+/?$',
                r'^(https?://)?m\.facebook\.com/.*/videos/\d+',
                r'^(https?://)?(?:www\.)?facebook\.com/share/r/[\w-]+/?$',
                r'^(https?://)?(?:www\.)?facebook\.com/watch\?v=\d+(?:&[\w=]+)*',
            ],
            'instagram': [
                r'^(https?://)?(?:www\.)?instagram\.com/(p|reel)/[\w-]+/?$',
                r'^(https?://)?(?:www\.)?instagram\.com/stories/[\w.-]+/\d+/?$',
                r'^(https?://)?(?:www\.)?instagram\.com/(p|reel)/[\w-]+/?\?[\w=&%_-]+',
            ],
            'x': [
                r'^(https?://)?(?:www\.)?(twitter|x)\.com/.*/status/\d+',
            ],
            'soundcloud': [
                r'^(https?://)?(?:www\.)?soundcloud\.com/[\w-]+/[\w-]+',
                r'^(https?://)?soundcloud\.app\.goo\.gl/[\w-]+',
            ],
            'bandcamp': [
                r'^(https?://)?[\w-]+\.bandcamp\.com/track/[\w-]+',
                r'^(https?://)?[\w-]+\.bandcamp\.com/album/[\w-]+',  # Album (chỉ tải track đầu tiên nếu không hỗ trợ đầy đủ)
            ],
            'deezer': [
                r'^(https?://)?(?:www\.)?deezer\.com/.*/track/\d+',
                r'^(https?://)?deezer\.page\.link/[\w-]+',
                r'^(https?://)?(?:www\.)?deezer\.com/album/\d+',
                r'^(https?://)?(?:www\.)?deezer\.com/artist/\d+',
                r'^(https?://)?(?:www\.)?deezer\.com/playlist/\d+',
                r'^(https?://)?(?:www\.)?deezer\.com/track/\d+',
                r'^(https?://)?dzr\.page\.link/[\w-]+',
            ],
            'tidal': [
                r'^(https?://)?(?:www\.)?tidal\.com/(browse/)?track/\d+',
                r'^(https?://)?tidal\.lnk\.to/[\w-]+',
            ],
            'mixcloud': [
                r'^(https?://)?(?:www\.)?mixcloud\.com/[\w-]+/[\w-]+/?$',
                r'^(https?://)?(?:www\.)?mixcloud\.com/[^/]+/[^/]+/?$',
            ],
            'bluesky': [
                r'^(https?://)?(?:www\.)?bsky\.app/profile/[\w.-]+/post/[\w-]+',
            ],
            'tumblr': [
                r'^(https?://)?[\w-]+\.tumblr\.com/post/\d+',
                r'^(https?://)?(?:www\.)?tumblr\.com/[\w-]+/\d+',
            ],
            'reddit': [
                r'^(https?://)?(?:www\.)?reddit\.com/r/[\w-]+/comments/[\w-]+/[\w-]+/?(?:\?.*)?$',  
                r'^(https?://)?redd\.it/[\w-]+(?:\?.*)?$', 
            ],
            'bilibili': [
                r'^(https?://)?(?:www\.)?bilibili\.com/video/[A-Za-z0-9]+',
                r'^(https?://)?b23\.tv/[A-Za-z0-9]+',
            ],
        }

    def is_valid_url(self, url):
        """Kiểm tra URL hợp lệ và thuộc nền tảng nào"""
        if not url:
            return False, "URL is empty", None
        
        normalized_url = self.normalize_url(url.strip())

        for platform, patterns in self.patterns.items():
            for pattern in patterns:
                if re.match(pattern, normalized_url):
                    if platform == 'youtube' and "playlist" in normalized_url:
                        return False, "YouTube playlists are not supported yet", 'youtube'
                    return True, f"Valid {platform.capitalize()} URL", platform
        
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
        self.base_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "download")
        self.output_dir = None

    def run(self):
        """Hàm chạy trong luồng riêng để tải audio"""
        # Kiểm tra URL
        is_valid, message, platform = self.validator.is_valid_url(self.url)
        if not is_valid:
            self.error.emit(message)
            return

        # Xác định thư mục lưu trữ
        self.output_dir = os.path.join(self.base_dir, platform)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        try:
            # Cấu hình cơ bản cho yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.progress_hook],
                'quiet': True,  # Giảm log
            }

            if platform == 'deezer' or platform == 'tidal':
                ydl_opts['format'] = 'bestaudio'  # Đảm bảo chỉ lấy audio tốt nhất
            elif platform == 'bandcamp':
                ydl_opts['outtmpl'] = os.path.join(self.output_dir, '%(album)s - %(title)s.%(ext)s')  # Định dạng tên file đặc biệt

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