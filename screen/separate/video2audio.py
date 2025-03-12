import os
import subprocess
import tempfile
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow

class ExtractAudioThread(QThread):
    finished = pyqtSignal(str, int)  # Thêm tham số duration
    error = pyqtSignal(str)

    def __init__(self, video_file):
        super().__init__()
        self.video_file = video_file
        self.temp_audio_file = None

    def run(self):
        try:
            # Tạo file âm thanh tạm thời
            fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            self.temp_audio_file = temp_path

            # Lấy thời lượng video bằng FFprobe
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', self.video_file
            ]
            duration_output = subprocess.check_output(duration_cmd, universal_newlines=True).strip()
            duration_ms = int(float(duration_output) * 1000)  # Chuyển sang milliseconds

            # Sử dụng FFmpeg để trích xuất âm thanh
            command = [
                'ffmpeg', '-i', self.video_file, 
                '-q:a', '0', '-map', 'a', 
                '-y', self.temp_audio_file
            ]
            
            # Thực thi lệnh FFmpeg
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
            
            # Gửi signal khi hoàn thành, kèm theo thời lượng
            self.finished.emit(self.temp_audio_file, duration_ms)
            
        except Exception as e:
            self.error.emit(f"Error extracting audio: {str(e)}")


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
            
            # Sử dụng FFmpeg để trích xuất âm thanh
            self.progress_updated.emit(50, "Extracting audio...")
            
            # Lệnh FFmpeg để chuyển đổi video thành audio
            command = [
                'ffmpeg', '-i', self.video_file, 
                '-q:a', '0', '-map', 'a', 
                '-y', output_file
            ]
            
            # Thực thi lệnh FFmpeg
            subprocess.run(command, check=True)

            # Cập nhật tiến trình
            self.progress_updated.emit(100, "Export complete!")

            # Phát tín hiệu hoàn thành
            self.export_finished.emit(output_file)

        except Exception as e:
            error_msg = f"Error exporting audio: {str(e)}"
            self.export_error.emit(error_msg)


class Video2AudioPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_video_file = None  # Khởi tạo biến để lưu đường dẫn file
        self.temp_audio_file = None  # Lưu đường dẫn file âm thanh tạm thời
        self.extract_thread = None  # Thread để trích xuất âm thanh
        self.actual_duration = 0  # Lưu thời lượng thực của video
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
        self.selected_video_file = file_path
        
        # Kiểm tra nếu đây là file video được hỗ trợ
        video_extensions = {'.mp4', '.mkv', '.mov', '.flv', '.avi'}
        if any(file_path.lower().endswith(ext) for ext in video_extensions):
            
            # Hiển thị tên file
            file_name = os.path.basename(file_path)
            self.audio_player.setText(f"Loading: {file_name}")
            
            # Trích xuất âm thanh từ video bằng thread riêng
            self.extract_thread = ExtractAudioThread(file_path)
            self.extract_thread.finished.connect(self.on_audio_extracted)
            self.extract_thread.error.connect(self.on_extraction_error)
            self.extract_thread.start()
        else:
            # Nếu không phải file video, hiển thị thông báo lỗi và không xử lý
            self.audio_player.setText("Only video files are supported (e.g., .mp4, .mkv, .mov, .flv, .avi)")
            print(f"Unsupported file format: {file_path}")

    def on_audio_extracted(self, temp_audio_file, duration_ms):
        # Lưu đường dẫn file tạm để xóa sau này
        self.temp_audio_file = temp_audio_file
        self.actual_duration = duration_ms
        
        # Phát file âm thanh tạm thời
        self.audio_player.set_audio_file(temp_audio_file)
        
        # Ẩn loading overlay nếu cần
        self.audio_player.loading_overlay.hide_loading()
        
        # Khi QMediaPlayer đã load xong, điều chỉnh thời lượng
        def set_duration():
            if self.audio_player.player.duration() > 0:
                # Ghi đè thời lượng bằng giá trị thực từ video
                self.audio_player.player.setNotifyInterval(50)  # Đảm bảo cập nhật mượt
                self.audio_player.seekbar.setRange(0, self.actual_duration)
                self.audio_player.total_time.setText(self.audio_player.format_time(self.actual_duration))
            else:
                # Thử lại sau 100ms nếu media chưa sẵn sàng
                QTimer.singleShot(100, set_duration)
                
        set_duration()

    def on_extraction_error(self, error_msg):
        print(error_msg)
        self.audio_player.loading_overlay.hide_loading()
        self.audio_player.setText("Error extracting audio from video")

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "separate")  
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def export_audio(self):
        if not self.selected_video_file:
            print("No video file selected!")
            return

        # Dừng phát nếu đang phát
        self.audio_player.player.stop()

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
        self.export_thread = VideoToAudioThread(self.selected_video_file)
        
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
        # Dừng phát nếu đang phát
        self.audio_player.player.stop()
        
        # Xóa file tạm nếu tồn tại
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
            except:
                pass
        
        # Xóa nội dung trình phát audio
        self.audio_player.clear() 
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(1)
    
    def closeEvent(self, event):
        # Xóa file tạm khi đóng ứng dụng
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
            except:
                pass
        super().closeEvent(event)