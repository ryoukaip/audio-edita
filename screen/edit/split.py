import os
import librosa
import soundfile as sf
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel

class SplitPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_audio_file = None
    
    def initUI(self):
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Add function bar
        top_bar = FunctionBar("split", font_family, self)
        layout.addLayout(top_bar)
        
        # Audio player
        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)  
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        self.audio_player.time_updated.connect(self.update_split_time)
        layout.addWidget(self.audio_player)
        
        # Thêm dòng chữ "split this audio at"
        split_label = QLabel("split this audio at")
        split_label.setFont(QFont(font_family, 13))
        split_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(split_label, alignment=Qt.AlignCenter)  

        # Thêm thanh thời gian "00:00" với nền và bo tròn
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

        # Thêm layout ngang cho nút Export
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Open file location button
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

        # Thêm khoảng cách giữa hai nút
        button_layout.addSpacing(10)

        # Create export button
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
        """Xử lý khi người dùng kéo thả file âm thanh"""
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def update_split_time(self, time_str):
        """Cập nhật thời gian tại split label từ chuỗi đã định dạng"""
        self.time_label.setText(time_str)

    def show_output_widget(self):
        """Cắt và xuất file âm thanh khi nhấn nút Export"""
        if not self.selected_audio_file:
            print("No audio file selected!")
            return
        
        # Dừng phát âm thanh nếu đang phát
        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            print("Audio paused before export")

        # Lấy thời gian hiện tại từ time_label
        time_str = self.time_label.text()
        try:
            minutes, seconds = map(int, time_str.split(":"))
            split_time = minutes * 60 + seconds  # Chuyển sang giây
        except ValueError:
            print("Invalid time format!")
            return

        # Tải file âm thanh bằng librosa
        try:
            audio, sr = librosa.load(self.selected_audio_file, sr=None)  # Giữ nguyên sample rate gốc
            total_duration = librosa.get_duration(y=audio, sr=sr)  # Tổng thời gian (giây)

            if split_time >= total_duration or split_time <= 0:
                print("Split time is out of bounds!")
                return

            # Chuyển thời gian từ giây sang số mẫu
            split_samples = int(split_time * sr)

            # Cắt file âm thanh thành 2 phần
            part1 = audio[:split_samples]  # Từ đầu đến điểm cắt
            part2 = audio[split_samples:]  # Từ điểm cắt đến cuối

            # Đường dẫn lưu file
            output_dir = os.path.expanduser("~/Documents/audio-edita/edit")
            os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa có

            # Lấy tên file gốc mà không có phần mở rộng
            base_name = os.path.splitext(os.path.basename(self.selected_audio_file))[0]
            file_ext = os.path.splitext(self.selected_audio_file)[1]  # Giữ nguyên định dạng file gốc

            # Đường dẫn cho 2 file đầu ra
            output_file1 = os.path.join(output_dir, f"{base_name}_split_1{file_ext}")
            output_file2 = os.path.join(output_dir, f"{base_name}_split_2{file_ext}")

            # Lưu 2 file âm thanh bằng soundfile
            sf.write(output_file1, part1, sr, format='WAV')
            sf.write(output_file2, part2, sr, format='WAV')
            print(f"Files exported successfully: {output_file1}, {output_file2}")

        except Exception as e:
            print(f"Error during export: {e}")

    def open_file_location(self):
        """Mở thư mục chứa file đã xuất (tương thích đa nền tảng)"""
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit")
        
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
        
    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            stack.setCurrentIndex(0)