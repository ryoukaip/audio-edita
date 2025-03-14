import os
import shutil
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow

# Worker thread để xử lý trích xuất âm thanh từ video
class VideoToAudioWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, video_file, output_file):
        super().__init__()
        self.video_file = video_file
        self.output_file = output_file

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading video...", "3 seconds"),
                (40, "Extracting audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            # Bước 1: Chuẩn bị
            self.progress_updated.emit(0, "Preparing video...", "Calculating...")
            # Giả sử sử dụng ffmpeg để trích xuất âm thanh (cần cài đặt ffmpeg)
            import subprocess
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Bước 2: Trích xuất âm thanh
            cmd = [
                "ffmpeg", "-i", self.video_file, "-vn", "-acodec", "mp3",
                "-y", self.output_file  # -y để ghi đè nếu file đã tồn tại
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Bước 3: Giả lập xử lý (có thể bỏ qua nếu không cần thêm bước)
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Bước 4: Lưu file
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(self.output_file)

        except Exception as e:
            self.error.emit(f"Error extracting audio: {str(e)}")

class Video2AudioPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_video_file = None
        self.temp_audio_file = None
        self.initUI()

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("video to audio", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
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
        logging.debug(f"File dropped: {file_path}")
        video_extensions = {'.mp4', '.mkv', '.mov', '.flv', '.avi'}
        if any(file_path.lower().endswith(ext) for ext in video_extensions):
            self.selected_video_file = file_path
            file_name = os.path.basename(file_path)
            self.audio_player.setText(f"Loaded: {file_name}")
            self.audio_player.set_audio_file(file_path)  # Giả sử DropAreaLabel xử lý phát âm thanh
        else:
            self.audio_player.setText("Only video files are supported (e.g., .mp4, .mkv, .mov, .flv, .avi)")
            logging.warning(f"Unsupported file format: {file_path}")

    def export_audio(self):
        if not self.selected_video_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select a video file first")
            return

        # Dừng phát âm thanh nếu đang phát
        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            logging.debug("Audio paused before export")

        # Tạo đường dẫn đầu ra
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "separate")
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.selected_video_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}_audio.mp3")

        # Hiển thị cửa sổ render
        self.render_window = RenderWindow(self)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = self.audio_player.screen().geometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        # Tạo worker thread
        self.worker = VideoToAudioWorker(self.selected_video_file, output_file)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.export_btn.setEnabled(False)
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
        self.export_btn.setEnabled(True)
        logging.debug(f"Audio exported successfully: {output_file}")

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "separate")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(1)  # Quay lại trang chính hoặc trang trước