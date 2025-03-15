import os
import librosa
import soundfile as sf
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow

# Worker thread để xử lý cắt âm thanh
class SplitWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str, str)  # Signal khi hoàn thành (đường dẫn file đầu ra 1 và 2)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, split_time):
        super().__init__()
        self.input_file = input_file
        self.split_time = split_time

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (20, "Loading audio...", "3 seconds"),
                (40, "Splitting audio...", "2 seconds"),
                (60, "Processing audio...", "2 seconds"),
                (80, "Saving files...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            total_duration = librosa.get_duration(y=audio, sr=sr)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Kiểm tra thời gian cắt
            if self.split_time >= total_duration or self.split_time <= 0:
                raise ValueError("Split time is out of bounds!")

            # Chuyển thời gian từ giây sang số mẫu
            split_samples = int(self.split_time * sr)

            # Cắt file âm thanh thành 2 phần
            part1 = audio[:split_samples]
            part2 = audio[split_samples:]
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Giả lập bước xử lý (nếu cần thêm logic sau này)
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "split")
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            file_ext = os.path.splitext(self.input_file)[1]

            output_file1 = os.path.join(output_dir, f"{base_name}_split_1{file_ext}")
            output_file2 = os.path.join(output_dir, f"{base_name}_split_2{file_ext}")

            sf.write(output_file1, part1, sr, format='WAV')
            sf.write(output_file2, part2, sr, format='WAV')
            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file1, output_file2)

        except Exception as e:
            self.error.emit(str(e))

class SplitPage(QWidget):
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

        top_bar = FunctionBar("split", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        self.audio_player.time_updated.connect(self.update_split_time)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)
        
        split_label = QLabel("split this audio at")
        split_label.setFont(QFont(font_family, 13))
        split_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(split_label, alignment=Qt.AlignCenter)

        self.time_label = QLabel("00:00")
        self.time_label.setFont(QFont(font_family, 13, QFont.Bold))
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #474f7a;
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        layout.addWidget(self.time_label, alignment=Qt.AlignCenter)
        
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

        export_btn = QPushButton("Export")
        export_btn.setFixedSize(100, 40)
        export_btn.setFont(QFont(font_family, 13))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        export_btn.clicked.connect(self.show_output_widget)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)
        self.setStyleSheet("background-color: #282a32;")

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def update_split_time(self, time_str):
        self.time_label.setText(time_str)

    def show_output_widget(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        # Dừng phát âm thanh nếu đang phát
        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            print("Audio paused before export")

        # Lấy thời gian hiện tại từ time_label
        time_str = self.time_label.text()
        try:
            minutes, seconds = map(int, time_str.split(":"))
            split_time = minutes * 60 + seconds
        except ValueError:
            noti_window = NotiWindow()
            noti_window.update_message("Invalid time format!")
            return

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
        self.worker = SplitWorker(self.selected_audio_file, split_time)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file1, output_file2):
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        print(f"Files exported successfully: {output_file1}, {output_file2}")

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "split")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
        
    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(0)