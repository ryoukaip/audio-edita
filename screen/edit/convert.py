import os
import librosa
import soundfile as sf
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout, QComboBox, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow

# Worker thread để xử lý chuyển đổi định dạng âm thanh
class ConvertWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình (progress, status, time_remaining)
    finished = pyqtSignal(str)  # Signal khi hoàn thành (đường dẫn file đầu ra)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file, output_format):
        super().__init__()
        self.input_file = input_file
        self.output_format = output_format.lower()

    def run(self):
        try:
            # Giả lập các bước tiến trình
            fake_progress_steps = [
                (30, "Loading audio...", "3 seconds"),
                (60, "Converting format...", "2 seconds"),
                (90, "Saving file...", "1 second"),
            ]

            # Tải file âm thanh
            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            # Giả lập bước chuyển đổi (thực tế chỉ cần lưu với định dạng mới)
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            # Tạo thư mục đầu ra và lưu file
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{filename}_converted.{self.output_format}")
            sf.write(output_file, audio, sr, format=self.output_format)

            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            # Hoàn thành
            self.progress_updated.emit(100, "Conversion complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))

class ConvertPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.initUI()

    def initUI(self):
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        # Add function bar
        top_bar = FunctionBar("convert", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # Drop area for audio file
        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        # Format selection label
        format_label = QLabel("convert to format")
        format_label.setFont(QFont(font_family, 13))
        format_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(format_label, alignment=Qt.AlignCenter)

        # Format selection ComboBox
        self.format_combo = QComboBox()
        self.format_combo.addItems(["wav", "mp3", "flac", "ogg"])
        self.format_combo.setFont(QFont(font_family, 13, QFont.Bold))
        self.format_combo.setStyleSheet("""
            QComboBox {
                color: #ffffff;
                background-color: #474f7a;
                border-radius: 18px;
                padding: 6px 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #474f7a;
                color: #ffffff;
                selection-background-color: #3a4062;
            }
        """)
        self.format_combo.setFixedWidth(120)
        layout.addWidget(self.format_combo, alignment=Qt.AlignCenter)
        layout.addSpacing(10)

        layout.addStretch()

        # Buttons
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

        self.convert_btn = QPushButton("Export")
        self.convert_btn.setFixedSize(100, 40)
        self.convert_btn.setFont(QFont(font_family, 13))
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        self.convert_btn.clicked.connect(self.convert_audio)
        button_layout.addWidget(self.convert_btn)

        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #282a32;")

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def convert_audio(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        print(f"Starting conversion for file: {self.selected_audio_file}")
        
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

        self.convert_btn.setEnabled(False)

        # Tạo worker thread
        output_format = self.format_combo.currentText()
        self.worker = ConvertWorker(self.selected_audio_file, output_format)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_convert_finished)
        self.worker.error.connect(self.on_convert_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_convert_finished(self, output_file):
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Conversion complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.audio_player.set_audio_file(output_file)
        self.convert_btn.setEnabled(True)

    def on_convert_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Conversion failed: {error_message}")
        self.convert_btn.setEnabled(True)

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

if __name__ == "__main__":
    app = QApplication([])
    window = ConvertPage()
    window.show()
    app.exec_()