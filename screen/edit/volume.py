import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QSlider, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices, QPixmap
from PyQt5.QtCore import Qt, QUrl, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_slider import Slider
from screen.function.system.function_notiwindow import NotiWindow

class VolumePage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        if font_id == -1:
            font_family = "Arial"
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("volume", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        self.volume_slider_widget = Slider(font_family)
        self.volume_slider_widget.volume_changed.connect(self.handle_volume_change)
        layout.addWidget(self.volume_slider_widget)
        layout.addSpacing(15)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

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
        self.status_label.setText("")

    def handle_volume_change(self, value):
        pass
    
    def export_audio(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()  # Tạo mới, không cần parent
            noti_window.update_message("Please select an audio file first")
            return

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
                (1, 20, "Loading audio...", "5 seconds"),
                (2, 40, "Adjusting volume...", "4 seconds"),
                (3, 60, "Normalizing audio...", "3 seconds"),
                (4, 80, "Saving file...", "2 seconds"),
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

            volume_factor = self.volume_slider_widget.get_volume_factor()
            audio, sr = librosa.load(self.selected_audio_file, sr=None)
            adjusted_audio = audio * volume_factor
            if np.max(np.abs(adjusted_audio)) > 1.0:
                adjusted_audio = adjusted_audio / np.max(np.abs(adjusted_audio))
            
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            output_dir = os.path.join(documents_path, "audio-edita", "edit")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = os.path.splitext(os.path.basename(self.selected_audio_file))[0]
            volume_percent = int(volume_factor * 100)
            output_file = os.path.join(output_dir, f"{filename}_vol_{volume_percent}%.wav")
            
            sf.write(output_file, adjusted_audio, sr)
            
            self.fake_progress_timer.stop()
            self.render_window.updateProgress(100)
            self.render_window.updateStatus("Export complete!")
            self.render_window.updateTimeRemaining("Done!")
            QTimer.singleShot(1000, self.render_window.close)
            
            self.audio_player.set_audio_file(output_file)
            self.status_label.setText(f"Exported: {os.path.basename(output_file)}")
            self.export_btn.setEnabled(True)

        except Exception as e:
            if hasattr(self, 'fake_progress_timer'):
                self.fake_progress_timer.stop()
            if hasattr(self, 'render_window'):
                self.render_window.close()
            noti_window = NotiWindow()  # Tạo mới, không cần parent
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