import librosa
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QSize, QTimer, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtWidgets import (QLabel, QFileDialog, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QSlider, QStackedWidget, QGridLayout, QSizePolicy)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from screen.function.playaudio.function_wavevisual import WaveformWidget
from screen.function.playaudio.function_playloading import LoadingSpinner, LoadingOverlay

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

class DropAreaLabel(QLabel):
    file_dropped = pyqtSignal(str)
    time_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(220)
        
        # Setup font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        
        # Initialize media player
        self.player = QMediaPlayer()
        self.is_playing = False
        self.first_load = True  # Add this line after super().__init__
        
        self.setupUI()
        
    def setupUI(self):
        # Create stacked widget
        self.stacked_widget = QStackedWidget(self)
        
        # Create and setup both UI states
        self.setup_drop_area_ui()
        self.setup_player_ui()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setGeometry(self.rect())
        
    def setup_drop_area_ui(self):
        # Drop area widget
        drop_widget = QWidget()
        drop_widget.setStyleSheet("""
            QWidget {
                background-color: #7d8bd4;
                border: 3px solid #FBFFE4;
                border-radius: 25px;
            }
        """)
        
        # Drop area label
        drop_label = QLabel("click to select file or drop a file here")
        drop_label.setFont(QFont(self.font_family, 12))
        drop_label.setStyleSheet("color: white; border: none;")
        drop_label.setAlignment(Qt.AlignCenter)
        
        # Layout
        drop_layout = QVBoxLayout(drop_widget)
        drop_layout.addWidget(drop_label)
        
        self.stacked_widget.addWidget(drop_widget)
        
    def setup_player_ui(self):
        # Player widget
        player_widget = QWidget()
        player_layout = QVBoxLayout(player_widget)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_layout.setSpacing(0)

        # Upper section (seekbar)
        upper_widget = QWidget()
        upper_widget.setFixedHeight(220)
        upper_widget.setStyleSheet("""
            QWidget {
                background-color: #7d8bd4;
                border-radius: 25px;
            }
        """)
        upper_layout = QVBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setAlignment(Qt.AlignTop)
        upper_layout.setSpacing(0)

        # Tạo container cho seekbar và waveform
        seekbar_container = QWidget()
        seekbar_container.setFixedHeight(190)
        seekbar_layout = QVBoxLayout(seekbar_container)
        seekbar_layout.setContentsMargins(0, 0, 0, 0)
        seekbar_layout.setSpacing(0)

        # Create seekbar as background
        self.seekbar = QSlider(Qt.Horizontal)
        self.seekbar.setFixedHeight(190)
        self.seekbar.setStyleSheet("""
            QSlider {
                background: transparent;
                margin: 0px;
                padding: 0px;
                border-top: none;
            }
            QSlider::groove:horizontal {
                height: 190px;
                background: #474f7a;
                border-radius: 25px;
                margin: 0px;
            }
            QSlider::handle:horizontal {
                width: 0px;
                height: 0px;
            }
            QSlider::sub-page:horizontal {
                height: 190px;
                background: #98a4e6;
                border-radius: 25px;
                margin: 0px;
            }
        """)
        self.seekbar.sliderMoved.connect(self.seek_position)
        self.seekbar.setEnabled(False)

        # Tạo waveform widget
        self.waveform = WaveformWidget(self.seekbar)
        self.waveform.setFixedHeight(190)
        self.waveform.setGeometry(self.seekbar.geometry())

        # Add timer for smooth updates
        self.update_timer = QTimer()
        self.update_timer.setInterval(8)  # ~60fps
        self.update_timer.timeout.connect(self.update_position)
        
        # Add animation
        self.seekbar_animation = QPropertyAnimation(self.seekbar, b"value")
        self.seekbar_animation.setEasingCurve(QEasingCurve.Linear)
        self.seekbar_animation.setDuration(8)
        
        # Thêm vào layout
        seekbar_layout.addWidget(self.seekbar)
        upper_layout.addWidget(seekbar_container)

        # Lower section (controls)
        lower_widget = QWidget()
        lower_widget.setFixedHeight(30)
        lower_widget.setStyleSheet("""
            QWidget {
                background-color: none;
                margin: 0px;
            }
        """)

        lower_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lower_layout = QHBoxLayout(lower_widget)
        lower_layout.setContentsMargins(20, 0, 20, 0)
        lower_layout.setSpacing(0)
        lower_layout.setAlignment(Qt.AlignVCenter)

        # Create play button with icon
        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setIcon(QIcon("./icon/arrow-back.png"))
        self.back_btn.clicked.connect(lambda: self.seek_relative(-5000))  # 5 seconds backward
        
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(20, 20)
        self.play_icon = QIcon("./icon/play.png")
        self.pause_icon = QIcon("./icon/pause.png")
        self.play_btn.setIcon(self.play_icon)
        self.play_btn.clicked.connect(self.toggle_playback)
        
        self.forward_btn = QPushButton()
        self.forward_btn.setFixedSize(30, 30)
        self.forward_btn.setIcon(QIcon("./icon/arrow-forward.png"))
        self.forward_btn.clicked.connect(lambda: self.seek_relative(5000))  # 5 seconds forward

        # Create time labels
        self.current_time = QLabel("00:00")
        self.total_time = QLabel("00:00")
        for label in [self.current_time, self.total_time]:
            label.setStyleSheet("color: white; border: none;")
            label.setFont(QFont(self.font_family, 10))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(50)

        # Add elements to lower section
        lower_layout.addWidget(self.current_time)
        lower_layout.addStretch()
        lower_layout.addWidget(self.back_btn)
        lower_layout.addWidget(self.play_btn)
        lower_layout.addWidget(self.forward_btn)
        lower_layout.addStretch()
        lower_layout.addWidget(self.total_time)

        # Add both sections to main player layout
        player_layout.addWidget(upper_widget)
        player_layout.addWidget(lower_widget)

        self.stacked_widget.addWidget(player_widget)

        # Connect media player signals
        self.player.stateChanged.connect(self.on_state_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

    def set_audio_file(self, file_path):
        # Set media content immediately for player
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.seekbar.setEnabled(False)
        self.stacked_widget.setCurrentIndex(1)  # Switch to player UI
        
        # Only show loading overlay on first load
        if self.first_load:
            self.loading_overlay.show_loading()
        
        # Create and start worker thread for audio loading
        self.loading_worker = AudioLoadWorker(file_path)
        self.loading_worker.finished.connect(self.on_audio_loaded)
        self.loading_worker.start()
    
    def on_audio_loaded(self, file_path, data):
        if data:
            waveform_data, sr = data
            self.waveform.set_waveform_data(waveform_data)
        if self.first_load:
            self.loading_overlay.hide_loading()
            self.first_load = False  # Set to False after first load
        self.seekbar.setEnabled(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._is_audio_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if self._is_audio_file(file_path):
                self.set_audio_file(file_path)
                self.file_dropped.emit(file_path)
                break


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._open_file_dialog()

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.m4a *.flac)"
        )
        if file_path:
            self.set_audio_file(file_path)
            self.file_dropped.emit(file_path)
            
    def toggle_playback(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.update_timer.stop()
        else:
            self.player.play()
            self.update_timer.start()

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.pause_icon)
            self.is_playing = True
            self.waveform.set_playing(True)  # Add this line
        else:
            self.play_btn.setIcon(self.play_icon)
            self.is_playing = False
            self.waveform.set_playing(False)  # Add this line

    def update_position(self):
        if not self.seekbar.isSliderDown():
            position = self.player.position()
            # Use animation for smooth movement
            self.seekbar_animation.setStartValue(self.seekbar.value())
            self.seekbar_animation.setEndValue(position)
            self.seekbar_animation.start()
            
            # Update waveform progress
            duration = self.player.duration()
            if duration > 0:
                progress = (position / duration) * 100
                self.waveform.set_progress(progress)
            time_str = self.format_time(position)
            self.current_time.setText(time_str)
            self.time_updated.emit(time_str)


    def position_changed(self, position):
        # Only update when manually seeking
        if self.seekbar.isSliderDown():
            self.seekbar.setValue(position)
            duration = self.player.duration()
            if duration > 0:
                progress = (position / duration) * 100
                self.waveform.set_progress(progress)
            self.current_time.setText(self.format_time(position))

    def duration_changed(self, duration):
        self.seekbar.setRange(0, duration)
        self.total_time.setText(self.format_time(duration))

    def seek_position(self, position):
        self.player.setPosition(position)

    @staticmethod
    def format_time(ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def _is_audio_file(file_path):
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
        return any(file_path.lower().endswith(ext) for ext in audio_extensions)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setGeometry(self.rect())
        
    def seek_relative(self, ms):
        new_position = self.player.position() + ms
        self.player.setPosition(new_position)