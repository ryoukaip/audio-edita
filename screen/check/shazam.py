import sys
import asyncio
import json
import requests
from io import BytesIO
from shazamio import Shazam
from PyQt5.QtCore import Qt, QUrl, QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QMainWindow, QHBoxLayout, QProgressBar)
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont, QFontDatabase


class WorkerSignals(QObject):
    """Defines the signals available for a worker thread"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)


class ShazamWorker(QRunnable):
    """Worker thread for running Shazam recognition"""
    
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


class ShazamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.result_data = None
        
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(self.font_family))
        
        # Set up the main window
        self.setWindowTitle("Shazam Song Recognizer")
        self.setGeometry(100, 100, 500, 700)
        
        # Define button style with font
        self.button_style = f"""
            QPushButton {{
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
                font-family: {self.font_family};
            }}
            QPushButton:hover {{
                background-color: #474f7a;
            }}
        """
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # File selection area
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("Select an audio file to recognize")
        self.file_path_label.setFont(QFont(self.font_family))
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet(self.button_style)
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)
        
        # Recognition button
        self.recognize_button = QPushButton("Recognize Song")
        self.recognize_button.setStyleSheet(self.button_style)
        self.recognize_button.clicked.connect(self.start_recognition)
        main_layout.addWidget(self.recognize_button)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        # Results area
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        
        # Song title
        self.title_label = QLabel()
        self.title_label.setFont(QFont(self.font_family, 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(self.title_label)
        
        # Artist name
        self.artist_label = QLabel()
        self.artist_label.setFont(QFont(self.font_family, 12))
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(self.artist_label)
        
        # Album label
        self.album_label = QLabel()
        self.album_label.setFont(QFont(self.font_family))
        self.album_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(self.album_label)
        
        # Album art
        self.album_art_label = QLabel()
        self.album_art_label.setAlignment(Qt.AlignCenter)
        self.album_art_label.setMinimumSize(300, 300)
        self.results_layout.addWidget(self.album_art_label)
        
        # Apple Music link
        self.apple_music_label = QLabel()
        self.apple_music_label.setFont(QFont(self.font_family))
        self.apple_music_label.setOpenExternalLinks(True)
        self.apple_music_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.apple_music_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(self.apple_music_label)
        
        # Apple Music button
        self.apple_music_button = QPushButton("Open in Apple Music")
        self.apple_music_button.setStyleSheet(self.button_style)
        self.apple_music_button.clicked.connect(self.open_apple_music)
        self.results_layout.addWidget(self.apple_music_button)
        
        # Add results area to main layout
        main_layout.addWidget(self.results_widget)
        
        # Hide results initially
        self.results_widget.hide()
        
        # Set up thread pool for background tasks
        self.threadpool = QThreadPool()
        
        # Audio file path
        self.audio_file = None
        self.apple_music_url = None
    
    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)"
        )
        if file_name:
            self.audio_file = file_name
            self.file_path_label.setText(f"File: {file_name}")
    
    def start_recognition(self):
        if not self.audio_file:
            self.file_path_label.setText("Please select an audio file first!")
            return
        
        # Show progress
        self.progress_bar.show()
        self.recognize_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        
        # Create worker thread
        worker = ShazamWorker(self.audio_file)
        worker.signals.finished.connect(self.process_results)
        worker.signals.error.connect(self.handle_error)
        
        # Execute worker
        self.threadpool.start(worker)
    
    def process_results(self, result):
        # Hide progress
        self.progress_bar.hide()
        self.recognize_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        
        # Store result data
        self.result_data = result
        
        # Check if we have track info
        if 'track' not in result:
            self.handle_error("No song was recognized")
            return
        
        track = result['track']
        
        # Update UI with song info
        self.title_label.setText(track.get('title', 'Unknown Title'))
        self.artist_label.setText(track.get('subtitle', 'Unknown Artist'))
        
        # Get album info if available
        album_info = "Unknown Album"
        if 'sections' in track:
            for section in track['sections']:
                if section.get('type') == 'SONG':
                    for metadata in section.get('metadata', []):
                        if metadata.get('title') == 'Album':
                            album_info = metadata.get('text', 'Unknown Album')
        self.album_label.setText(album_info)
        
        # Get Apple Music URL
        self.apple_music_url = None
        if 'hub' in track and 'options' in track['hub']:
            for option in track['hub']['options']:
                if option.get('caption') == 'OPEN IN':
                    for action in option.get('actions', []):
                        if action.get('type') == 'uri':
                            self.apple_music_url = action.get('uri')
        
        # Update Apple Music button and link
        if self.apple_music_url:
            self.apple_music_label.setText(f'<a href="{self.apple_music_url}">Listen on Apple Music</a>')
            self.apple_music_button.setEnabled(True)
        else:
            self.apple_music_label.setText("Apple Music link not available")
            self.apple_music_button.setEnabled(False)
        
        # Load album art
        if 'images' in track and 'coverarthq' in track['images']:
            image_url = track['images']['coverarthq']
            try:
                response = requests.get(image_url)
                image = QPixmap()
                image.loadFromData(BytesIO(response.content).read())
                
                # Scale the image to fit the label while maintaining aspect ratio
                scaled_image = image.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.album_art_label.setPixmap(scaled_image)
            except Exception as e:
                self.album_art_label.setText(f"Failed to load album art: {str(e)}")
        else:
            self.album_art_label.setText("No album art available")
        
        # Show results
        self.results_widget.show()
    
    def handle_error(self, error_message):
        self.progress_bar.hide()
        self.recognize_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.file_path_label.setText(f"Error: {error_message}")
        self.results_widget.hide()
    
    def open_apple_music(self):
        if self.apple_music_url:
            QDesktopServices.openUrl(QUrl(self.apple_music_url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShazamApp()
    window.show()
    sys.exit(app.exec_())