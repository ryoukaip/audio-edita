import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices, QPixmap
from PyQt5.QtCore import Qt, QUrl, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_slider import Slider
from screen.function.system.function_notiwindow import NotiWindow

class CompressPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("compress", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        # Slider mở rộng tới 500%
        self.quality_slider = Slider(font_family, mode="quality", min_value=0, max_value=200, default_value=75, unit="%", icon_path="./icon/compress.png")        
        layout.addWidget(self.quality_slider)
        layout.addSpacing(10)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        self.open_location_btn.clicked.connect(self.open_file_location)
        button_layout.addWidget(self.open_location_btn)

        button_layout.addSpacing(10)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedSize(100, 40)
        self.export_btn.setFont(QFont(font_family, 13))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        self.export_btn.clicked.connect(self.export_audio)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #282a32;")

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def export_audio(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        print(f"Starting export for file: {self.selected_audio_file}")
        try:
            self.render_window = RenderWindow(self)
            self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            screen_geometry = QApplication.desktop().screenGeometry()
            window_geometry = self.render_window.geometry()
            self.render_window.move(
                (screen_geometry.width() - window_geometry.width()) // 2,
                (screen_geometry.height() - window_geometry.height()) // 2
            )
            
            self.render_window.updateProgress(0)
            self.render_window.updateStatus("Preparing audio...")
            self.render_window.updateTimeRemaining("Calculating...")
            self.render_window.show()

            self.export_btn.setEnabled(False)
            
            self.fake_progress_steps = [
                (1, 20, "Loading audio...", "3 seconds"),
                (2, 40, "Compressing audio...", "2 seconds"),
                (3, 60, "Processing audio...", "2 seconds"),
                (4, 80, "Saving file...", "1 second"),
            ]
            
            self.fake_progress_timer = QTimer(self)
            self.fake_progress_index = 0
            
            def update_fake_progress():
                if self.fake_progress_index < len(self.fake_progress_steps):
                    _, progress, status, time_remaining = self.fake_progress_steps[self.fake_progress_index]
                    self.render_window.updateProgress(progress)
                    self.render_window.updateStatus(status)
                    self.render_window.updateTimeRemaining(time_remaining)
                    self.fake_progress_index += 1
            
            self.fake_progress_timer.timeout.connect(update_fake_progress)
            self.fake_progress_timer.start(1000)

            # Tải file âm thanh
            print("Loading audio file...")
            audio, sr = librosa.load(self.selected_audio_file, sr=None)
            print(f"Audio loaded: sample rate = {sr}, length = {len(audio)}")

            # Lấy giá trị chất lượng từ slider
            quality_percent = self.quality_slider.get_processed_value()
            print(f"Selected quality: {quality_percent}%")
            
            # Ánh xạ chất lượng sang sample rate mới (0% = giữ nguyên, 500% = thấp nhất)
            sample_rate_map = {
                0: sr,      # Giữ nguyên
                100: 11025, # Chất lượng cơ bản
                200: 8000,  # Thấp hơn
                300: 6000,  # Rất thấp
                400: 4000,  # Cực thấp
                500: 2000   # Thấp nhất có thể nghe được
            }
            quality_steps = [0, 100, 200, 300, 400, 500]
            closest_quality = min(quality_steps, key=lambda x: abs(x - quality_percent))
            new_sr = sample_rate_map[closest_quality]
            print(f"Using sample rate: {new_sr}")

            # Thay đổi sample rate nếu cần
            if new_sr != sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=new_sr)
                print(f"Resampled audio to sample rate: {new_sr}")

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.selected_audio_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_compressed_{closest_quality}%.wav")
            print(f"Output file path: {output_file}")

            # Lưu file WAV
            sf.write(output_file, audio, new_sr)
            print(f"File saved successfully at: {output_file}")

            self.fake_progress_timer.stop()
            self.render_window.updateProgress(100)
            self.render_window.updateStatus("Export complete!")
            self.render_window.updateTimeRemaining("Done!")
            QTimer.singleShot(1000, self.render_window.close)
            
            self.audio_player.set_audio_file(output_file)
            self.export_btn.setEnabled(True)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            if hasattr(self, 'fake_progress_timer'):
                self.fake_progress_timer.stop()
            if hasattr(self, 'render_window'):
                self.render_window.close()
            noti_window = NotiWindow()
            noti_window.update_message(f"Export failed: {str(e)}")
            self.export_btn.setEnabled(True)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(0)