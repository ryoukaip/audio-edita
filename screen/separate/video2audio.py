import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow

class VideoToAudioThread(QThread):
    progress_updated = pyqtSignal(int, str)
    export_finished = pyqtSignal(str)
    export_error = pyqtSignal(str)

    def __init__(self, temp_audio_file):
        super().__init__()
        self.temp_audio_file = temp_audio_file  

    def run(self):
        try:
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            output_dir = os.path.join(documents_path, "audio-edita", "separate")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_file = os.path.join(output_dir, f"exported_audio_{os.path.basename(self.temp_audio_file)}")

            self.progress_updated.emit(20, "Preparing to export...")
            self.progress_updated.emit(50, "Saving audio...")
            shutil.copy2(self.temp_audio_file, output_file)
            
            self.progress_updated.emit(100, "Export complete!")
            self.export_finished.emit(output_file)

        except Exception as e:
            error_msg = f"Error exporting audio: {str(e)}"
            self.export_error.emit(error_msg)


class Video2AudioPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_video_file = None
        self.temp_audio_file = None
        self.actual_duration = 0
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
        print(f"File dropped: {file_path}")
        self.selected_video_file = file_path
        
        video_extensions = {'.mp4', '.mkv', '.mov', '.flv', '.avi'}
        if any(file_path.lower().endswith(ext) for ext in video_extensions):
            file_name = os.path.basename(file_path)
            self.audio_player.setText(f"Loading: {file_name}")
            self.audio_player.set_audio_file(file_path)  # Gọi trực tiếp để VideoLoadWorker xử lý
        else:
            self.audio_player.setText("Only video files are supported (e.g., .mp4, .mkv, .mov, .flv, .avi)")
            print(f"Unsupported file format: {file_path}")

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "separate")  
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def export_audio(self):
        if not self.selected_video_file or not self.temp_audio_file:
            print("No video file or audio extracted to export!")
            return

        self.audio_player.player.stop()

        self.render_window = RenderWindow(self)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        
        self.render_window.show()

        self.export_thread = VideoToAudioThread(self.temp_audio_file)  # Dùng file tạm đã có
        
        def update_progress_and_status(progress, status):
            self.render_window.updateProgress(progress)
            self.render_window.updateStatus(status)

        self.export_thread.progress_updated.connect(update_progress_and_status)
        self.export_thread.export_finished.connect(self.on_export_finished)
        self.export_thread.export_error.connect(self.on_export_error)

        self.export_btn.setEnabled(False)
        self.export_thread.start()

    def on_export_finished(self, output_file):
        print(f"Audio exported successfully to: {output_file}")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_msg):
        print(error_msg)
        self.render_window.close()
        self.export_btn.setEnabled(True)

    def go_back(self):
        self.audio_player.player.stop()
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
            except:
                pass
        self.audio_player.clear()
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(1)
    
    def closeEvent(self, event):
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
            except:
                pass
        super().closeEvent(event)