import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_notiwindow import NotiWindow
from screen.edit.worker_trim import TrimWorker

class TrimPage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager
        self.selected_audio_file = None
        self.active_label = "to"  # Mặc định ô "to" được chọn để cập nhật thời gian
        self.initUI()
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        top_bar = FunctionBar("trim", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # File drop area (input, cho phép thả và chia sẻ)
        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        self.audio_player.time_updated.connect(self.update_trim_times)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)
        
        trim_label = QLabel("trim this audio")
        trim_label.setFont(QFont(font_family, 13))
        trim_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(trim_label, alignment=Qt.AlignCenter)

        # Layout cho hai nhãn thời gian "from" và "to"
        time_layout = QHBoxLayout()
        time_layout.addStretch()

        from_label = QLabel("from")
        from_label.setFont(QFont(font_family, 13))
        from_label.setStyleSheet("color: #ffffff;")
        time_layout.addWidget(from_label)

        self.start_time_label = QLabel("00:00")
        self.start_time_label.setFont(QFont(font_family, 13, QFont.Bold))
        self.start_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #292d47;  /* Màu mặc định cho "from" */
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        self.start_time_label.setCursor(Qt.PointingHandCursor)  # Con trỏ chuột dạng tay
        self.start_time_label.mousePressEvent = self.on_start_time_clicked  # Gắn sự kiện click
        time_layout.addWidget(self.start_time_label)

        time_layout.addSpacing(20)

        to_label = QLabel("to")
        to_label.setFont(QFont(font_family, 13))
        to_label.setStyleSheet("color: #ffffff;")
        time_layout.addWidget(to_label)

        self.end_time_label = QLabel("00:00")
        self.end_time_label.setFont(QFont(font_family, 13, QFont.Bold))
        self.end_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #474f7a;  /* Màu mặc định cho "to" */
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        self.end_time_label.setCursor(Qt.PointingHandCursor)  # Con trỏ chuột dạng tay
        self.end_time_label.mousePressEvent = self.on_end_time_clicked  # Gắn sự kiện click
        time_layout.addWidget(self.end_time_label)

        time_layout.addStretch()
        layout.addLayout(time_layout)
        
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
                background-color: #292d47;
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
                background-color: #292d47;
            }
        """)
        export_btn.clicked.connect(self.show_output_widget)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)
        self.setStyleSheet("background-color: #282a32;")

        # Tải tệp âm thanh từ AudioDataManager khi khởi tạo
        self.audio_player.load_shared_audio()

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def update_trim_times(self, time_str):
        # Cập nhật thời gian dựa trên ô nào đang được chọn
        if self.active_label == "to":
            self.end_time_label.setText(time_str)
        elif self.active_label == "from":
            self.start_time_label.setText(time_str)

    def on_start_time_clicked(self, event):
        # Khi nhấp vào ô "from"
        self.active_label = "from"
        # Đổi màu: "from" thành #474f7a, "to" thành #292d47
        self.start_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #474f7a;
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        self.end_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #292d47;
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        # Nhảy seekbar về thời gian trong "from"
        time_str = self.start_time_label.text()
        try:
            minutes, seconds = map(int, time_str.split(":"))
            position = (minutes * 60 + seconds) * 1000  # Chuyển sang milliseconds
            self.audio_player.player.setPosition(position)
        except ValueError:
            print("Invalid time format in start_time_label")

    def on_end_time_clicked(self, event):
        # Khi nhấp vào ô "to"
        self.active_label = "to"
        # Đổi màu: "to" thành #474f7a, "from" thành #292d47
        self.end_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #474f7a;
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        self.start_time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #292d47;
                border-radius: 18px;
                padding: 6px 10px;
            }
        """)
        # Nhảy seekbar về thời gian trong "to"
        time_str = self.end_time_label.text()
        try:
            minutes, seconds = map(int, time_str.split(":"))
            position = (minutes * 60 + seconds) * 1000  # Chuyển sang milliseconds
            self.audio_player.player.setPosition(position)
        except ValueError:
            print("Invalid time format in end_time_label")

    def show_output_widget(self):
        if not self.selected_audio_file:
            noti_window = NotiWindow()
            noti_window.update_message("Please select an audio file first")
            return

        if self.audio_player.player.state() == self.audio_player.player.PlayingState:
            self.audio_player.player.pause()
            print("Audio paused before export")

        start_time_str = self.start_time_label.text()
        end_time_str = self.end_time_label.text()
        try:
            start_minutes, start_seconds = map(int, start_time_str.split(":"))
            end_minutes, end_seconds = map(int, end_time_str.split(":"))
            start_time = start_minutes * 60 + start_seconds
            end_time = end_minutes * 60 + end_seconds
            if start_time >= end_time:
                raise ValueError("End time must be greater than start time!")
        except ValueError as e:
            noti_window = NotiWindow()
            noti_window.update_message(str(e) if str(e) else "Invalid time format!")
            return

        self.render_window = RenderWindow(None)
        self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen_geometry = self.audio_player.screen().geometry()
        window_geometry = self.render_window.geometry()
        self.render_window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        self.render_window.show()

        self.worker = TrimWorker(self.selected_audio_file, start_time, end_time)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error.connect(self.on_export_error)
        self.worker.start()

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        print(f"Export finished, output file: {output_file}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.audio_player.set_audio_file(output_file)  # Cập nhật trình phát với tệp đầu ra
        self.audio_data_manager.set_audio_file(output_file)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "trim")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
        
    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuEdit")
            if page_widget:
                stack.setCurrentWidget(page_widget)