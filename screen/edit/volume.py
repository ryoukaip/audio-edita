import os
import librosa
import soundfile as sf
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QSlider, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices, QPixmap
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_slider import Slider
from screen.function.system.function_notiwindow import NotiWindow

# Worker thread để xử lý điều chỉnh âm lượng
class VolumeWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, volume_factor):
        super().__init__()
        self.input_file = input_file
        self.volume_factor = volume_factor

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "5 seconds"),
                (40, "Adjusting volume...", "4 seconds"),
                (60, "Normalizing audio...", "3 seconds"),
                (80, "Saving file...", "2 seconds"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Điều chỉnh âm lượng
            adjusted_audio = audio * self.volume_factor
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Chuẩn hóa nếu âm lượng vượt quá giới hạn
            if np.max(np.abs(adjusted_audio)) > 1.0:
                adjusted_audio = adjusted_audio / np.max(np.abs(adjusted_audio))
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "volume")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_volume_{int(self.volume_factor * 100)}%.wav")
            sf.write(output_file, adjusted_audio, sr)

            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))

class VolumePage(QWidget):
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

        top_bar = FunctionBar("volume", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        self.volume_slider_widget = Slider(font_family, mode="volume", min_value=0, max_value=200, default_value=100, unit="%")
        self.volume_slider_widget.value_changed.connect(self.handle_volume_change)
        layout.addWidget(self.volume_slider_widget)
        layout.addSpacing(15)

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

    def handle_volume_change(self, value):
        pass
    
    def export_audio(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        print(f"Starting export for file: {self.selected_audio_file}")
        
        # Hiển thị cửa sổ render
        self.render_window = RenderWindow(self)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        self.export_btn.setEnabled(False)

        # Tạo worker thread
        volume_factor = self.volume_slider_widget.get_processed_value()
        self.worker = VolumeWorker(self.selected_audio_file, volume_factor)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.audio_player.set_audio_file(output_file)
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "volume")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(0)