from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt5.QtWidgets import QLabel, QFileDialog, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from screen.function.playaudio.function_playloading import LoadingSpinner, LoadingOverlay


class DropAreaLabel(QLabel):
    file_dropped = pyqtSignal(str)
    time_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(360)  # 16:9 ratio với width 640

        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)  # Khởi tạo QMediaPlayer
        self.is_playing = False
        self.first_load = True

        self.setupUI()

    def setupUI(self):
        self.stacked_widget = QStackedWidget(self)

        self.setup_drop_area_ui()
        self.setup_player_ui()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)

        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setGeometry(self.rect())

    def setup_drop_area_ui(self):
        drop_widget = QWidget()
        drop_widget.setStyleSheet("""
            QWidget {
                background-color: #7d8bd4;
                border: 3px solid #FBFFE4;
                border-radius: 25px;
            }
        """)

        drop_label = QLabel("click to select file or drop a file here")
        drop_label.setFont(QFont(self.font_family, 12))
        drop_label.setStyleSheet("color: white; border: none;")
        drop_label.setAlignment(Qt.AlignCenter)

        drop_layout = QVBoxLayout(drop_widget)
        drop_layout.addWidget(drop_label)

        self.stacked_widget.addWidget(drop_widget)

    def setup_player_ui(self):
        player_widget = QWidget()
        player_layout = QVBoxLayout(player_widget)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_layout.setSpacing(0)

        # Widget để hiển thị video
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(640, 360)  # 16:9 ratio
        self.video_widget.setStyleSheet("background-color: black;")
        self.player.setVideoOutput(self.video_widget)  # Gắn QMediaPlayer với QVideoWidget

        # Thanh điều khiển
        lower_widget = QWidget()
        lower_widget.setFixedHeight(30)
        lower_widget.setStyleSheet("""
            QWidget {
                background-color: #7d8bd4;
                border-top-left-radius: 0px;  
                border-top-right-radius: 0px;     
                border-bottom-left-radius: 15px;  
                border-bottom-right-radius: 15px; 
                margin: 0px;
            }
        """)
        lower_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lower_layout = QHBoxLayout(lower_widget)
        lower_layout.setContentsMargins(20, 0, 20, 0)
        lower_layout.setSpacing(0)

        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setIcon(QIcon("./icon/arrow-back.png"))
        self.back_btn.clicked.connect(self.seek_backward)

        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(20, 20)
        self.play_icon = QIcon("./icon/play.png")
        self.pause_icon = QIcon("./icon/pause.png")
        self.play_btn.setIcon(self.play_icon)
        self.play_btn.clicked.connect(self.toggle_playback)

        self.forward_btn = QPushButton()
        self.forward_btn.setFixedSize(30, 30)
        self.forward_btn.setIcon(QIcon("./icon/arrow-forward.png"))
        self.forward_btn.clicked.connect(self.seek_forward)

        self.current_time = QLabel("00:00")
        self.total_time = QLabel("00:00")
        for label in [self.current_time, self.total_time]:
            label.setStyleSheet("color: white; border: none;")
            label.setFont(QFont(self.font_family, 10))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(50)

        lower_layout.addWidget(self.current_time)
        lower_layout.addStretch()
        lower_layout.addWidget(self.back_btn)
        lower_layout.addWidget(self.play_btn)
        lower_layout.addWidget(self.forward_btn)
        lower_layout.addStretch()
        lower_layout.addWidget(self.total_time)

        player_layout.addWidget(self.video_widget)
        player_layout.addWidget(lower_widget)

        self.stacked_widget.addWidget(player_widget)

        # Timer để cập nhật thời gian phát
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

    def set_audio_file(self, file_path):
        self.stacked_widget.setCurrentIndex(1)

        if self.first_load:
            self.loading_overlay.show_loading()

        # Tạo media từ file path
        media = QMediaContent(QUrl.fromLocalFile(file_path))
        self.player.setMedia(media)
        self.player.play()
        self.is_playing = True
        self.play_btn.setIcon(self.pause_icon)

        # Bắt đầu timer để cập nhật thời gian
        self.timer.start(1000)

        if self.first_load:
            self.loading_overlay.hide_loading()
            self.first_load = False

    def toggle_playback(self):
        if self.is_playing:
            self.player.pause()
            self.play_btn.setIcon(self.play_icon)
        else:
            self.player.play()
            self.play_btn.setIcon(self.pause_icon)
        self.is_playing = not self.is_playing

    def seek_backward(self):
        # Tua lại 10 giây
        new_position = max(0, self.player.position() - 10000)
        self.player.setPosition(new_position)

    def seek_forward(self):
        # Chuyển tiếp 10 giây
        total_duration = self.player.duration()
        new_position = min(total_duration, self.player.position() + 10000)
        self.player.setPosition(new_position)

    def update_time(self):
        # Cập nhật thời gian hiện tại và tổng thời gian
        current_time = self.player.position() // 1000
        total_time = self.player.duration() // 1000
        self.current_time.setText(f"{current_time // 60:02d}:{current_time % 60:02d}")
        self.total_time.setText(f"{total_time // 60:02d}:{total_time % 60:02d}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._is_media_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if self._is_media_file(file_path):
                self.set_audio_file(file_path)
                self.file_dropped.emit(file_path)
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._open_file_dialog()

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media Files (*.mp4 *.mp3 *.wav *.ogg *.m4a *.flac)"
        )
        if file_path:
            self.set_audio_file(file_path)
            self.file_dropped.emit(file_path)

    @staticmethod
    def _is_media_file(file_path):
        media_extensions = {'.mp4', '.mp3', '.wav', '.ogg', '.m4a', '.flac'}
        return any(file_path.lower().endswith(ext) for ext in media_extensions)