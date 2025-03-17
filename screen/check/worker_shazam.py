import sys
import asyncio
import json
import requests
from io import BytesIO
from shazamio import Shazam
from PyQt5.QtCore import Qt, QUrl, QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QDesktopServices

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class ShazamWorker(QRunnable):
    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        self.signals = WorkerSignals()
        
    async def recognize_song(self):
        shazam = Shazam()
        result = await shazam.recognize(self.audio_file)
        return result
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.recognize_song())
            loop.close()
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class ShazamApp:
    def __init__(self):
        # Initialize variables
        self.result_data = None
        self.audio_file = None
        self.apple_music_url = None
        self.threadpool = QThreadPool()

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.audio_file = file_path
        return f"File: {file_path.split('/')[-1]}"
    
    def start_recognition(self):
        if not self.audio_file:
            return "Please drop an audio file first!", None
        
        worker = ShazamWorker(self.audio_file)
        return None, worker
    
    def process_results(self, result):
        self.result_data = result
        
        if 'track' not in result:
            return "No song was recognized", None, None, None, None, None
        
        track = result['track']
        
        title = track.get('title', 'Unknown Title')
        artist = track.get('subtitle', 'Unknown Artist')
        
        album_info = "Unknown Album"
        year_info = "Unknown Year"
        if 'sections' in track:
            for section in track['sections']:
                if section.get('type') == 'SONG':
                    for metadata in section.get('metadata', []):
                        if metadata.get('title') == 'Album':
                            album_info = metadata.get('text', 'Unknown Album')
                        if metadata.get('title') == 'Released':  # Lấy năm phát hành
                            year_info = metadata.get('text', 'Unknown Year')
        
        self.apple_music_url = None
        if 'hub' in track and 'options' in track['hub']:
            for option in track['hub']['options']:
                if option.get('caption') == 'OPEN IN':
                    for action in option.get('actions', []):
                        if action.get('type') == 'uri':
                            self.apple_music_url = action.get('uri')
        
        album_art = None
        if 'images' in track and 'coverarthq' in track['images']:
            image_url = track['images']['coverarthq']
            try:
                response = requests.get(image_url)
                image = QPixmap()
                image.loadFromData(BytesIO(response.content).read())
                album_art = image.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            except Exception as e:
                return f"Failed to load album art: {str(e)}", None, None, None, None, None
        else:
            return "No album art available", None, None, None, None, None
        
        return None, title, artist, album_info, album_art, year_info
    
    def handle_error(self, error_message):
        return error_message
    
    def open_apple_music(self):
        if self.apple_music_url:
            QDesktopServices.openUrl(QUrl(self.apple_music_url))