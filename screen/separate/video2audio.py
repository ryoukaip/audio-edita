import os
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playvideo.function_playvideo import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from moviepy.video.io.VideoFileClip import VideoFileClip

class VideoToAudioThread(QThread):
    progress_updated = pyqtSignal(int, str)
    export_finished = pyqtSignal(str)
    export_error = pyqtSignal(str)

    def __init__(self, video_file):
        super().__init__()
        self.video_file = video_file

    def run(self):
        try:
            # Đường dẫn đầu ra
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            output_dir = os.path.join(documents_path, "audio-edita", "separate")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Tạo tên file đầu ra (thay đuôi thành .mp3)
            input_file_name = os.path.splitext(os.path.basename(self.video_file))[0]
            output_file = os.path.join(output_dir, f"{input_file_name}_audio.mp3")

            # Cập nhật tiến trình
            self.progress_updated.emit(20, "Loading video...")
            
            # Trích xuất âm thanh từ video
            video = VideoFileClip(self.video_file)
            audio = video.audio

            # Cập nhật tiến trình
            self.progress_updated.emit(50, "Extracting audio...")
            audio.write_audiofile(output_file, codec='mp3')
            
            # Đóng file video để giải phóng tài nguyên
            video.close()

            # Cập nhật tiến trình
            self.progress_updated.emit(80, "Saving audio...")
            self.progress_updated.emit(100, "Export complete!")

            # Phát tín hiệu hoàn thành
            self.export_finished.emit(output_file)

        except Exception as e:
            error_msg = f"Error exporting audio: {str(e)}"
            self.export_error.emit(error_msg)

class Video2AudioPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None  # Khởi tạo biến để lưu đường dẫn file
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
        self.selected_audio_file = file_path

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "separate")  
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def export_audio(self):
        if not hasattr(self, 'selected_audio_file') or not self.selected_audio_file:
            print("No video file selected!")
            return

        # Khởi tạo cửa sổ render
        self.render_window = RenderWindow(self)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # Đặt vị trí cửa sổ ở giữa màn hình
        screen_geometry = QApplication.desktop().screenGeometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        
        # Hiển thị cửa sổ render
        self.render_window.show()

        # Tạo và bắt đầu luồng xử lý
        self.export_thread = VideoToAudioThread(self.selected_audio_file)
        
        # Kết nối các tín hiệu
        def update_progress_and_status(progress, status):
            self.render_window.updateProgress(progress)
            self.render_window.updateStatus(status)

        self.export_thread.progress_updated.connect(update_progress_and_status)
        self.export_thread.export_finished.connect(self.on_export_finished)
        self.export_thread.export_error.connect(self.on_export_error)

        # Vô hiệu hóa nút export
        self.export_btn.setEnabled(False)

        # Bắt đầu luồng
        self.export_thread.start()

    def on_export_finished(self, output_file):
        print(f"Audio exported successfully to: {output_file}")
        
        # Mở thư mục chứa file
        self.open_file_location()
        
        # Đóng cửa sổ render sau 1 giây
        QTimer.singleShot(1000, self.render_window.close)
        
        # Bật lại nút export
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_msg):
        print(error_msg)
        
        # Đóng cửa sổ render
        self.render_window.close()
        
        # Bật lại nút export
        self.export_btn.setEnabled(True)

    def go_back(self):
        self.audio_player.clear() # Xóa nội dung trình phát video
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(1)