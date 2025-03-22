import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl, QThread
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from screen.function.playaudio.function_playloading import LoadingSpinner

class AudioLoader(QThread):
    loaded = pyqtSignal(QMediaContent)
    
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path
        
    def run(self):
        media_content = QMediaContent(QUrl.fromLocalFile(self.audio_path))
        self.loaded.emit(media_content)

class BootWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Thiết lập cửa sổ
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 600)
        self.center()

        # Khởi tạo player
        self.player = QMediaPlayer()
        self.player.setVolume(100)
        
        # Tạo luồng để tải file âm thanh
        self.audio_loader = AudioLoader("./audio/edita.mp3")
        self.audio_loader.loaded.connect(self.on_audio_loaded)
        self.audio_loader.start()
        
        # Kiểm tra trạng thái media và phát khi sẵn sàng
        self.player.mediaStatusChanged.connect(self.handle_media_status)

        # Nạp font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Tạo layout chính
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tạo container cho hình ảnh và chữ
        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)

        # Thêm hình ảnh
        image_label = QLabel()
        pixmap = QPixmap("./screen/boot/hoguom.png")
        scaled_pixmap = pixmap.scaled(
            self.width(), 
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Thêm chữ
        location_label = QLabel("Hoan Kiem Lake - Hanoi")
        location_label.setFont(QFont(font_family, 12, QFont.Bold))
        location_label.setStyleSheet("color: white;")
        location_label.setContentsMargins(10, 5, 10, 5)
        location_label.setFixedSize(location_label.sizeHint())

        # Overlay cho chữ trên ảnh
        image_container.setStyleSheet("background-color: transparent;")
        image_container_layout.addWidget(image_label)
        overlay_container = QWidget(image_container)
        overlay_container.setGeometry(0, 0, self.width(), self.height())
        location_label.setParent(overlay_container)
        location_label.move(20, 20)

        # Khung dưới
        bottom_frame = QWidget()
        bottom_frame.setStyleSheet("background-color: #1c1b1f;")
        bottom_frame.setFixedHeight(100)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(35, 0, 35, 0)
        bottom_layout.setSpacing(10)

        # App icon
        app_icon = QLabel()
        pixmap_icon = QPixmap("./icon/edita.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_icon.setPixmap(pixmap_icon)

        # App title
        app_title = QLabel("audio edita")
        app_title.setFont(QFont(font_family, 18, QFont.Bold))
        app_title.setStyleSheet("color: white;")

        # Nhãn trạng thái
        self.status_label = QLabel("loading resources")
        self.status_label.setFont(QFont(font_family, 14))
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Thêm spinner
        self.spinner = LoadingSpinner(self)
        self.spinner.setFixedSize(30, 30)  # Điều chỉnh kích thước cho phù hợp
        
        # Layout cho status và spinner
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.spinner)

        bottom_layout.addWidget(app_icon)
        bottom_layout.addWidget(app_title)
        bottom_layout.addStretch()
        bottom_layout.addWidget(status_container)

        bottom_frame.setLayout(bottom_layout)

        # Thanh loading (ẩn)
        self.loading_bar = QProgressBar(self)
        self.loading_bar.setFixedHeight(8)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setValue(0)
        self.loading_bar.setVisible(False)  # Ẩn thanh loading
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #323754;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #7d8bd4;
            }
        """)

        # Áp dụng layout
        main_layout.addWidget(image_container)
        main_layout.addStretch()
        main_layout.addWidget(bottom_frame)
        main_layout.addWidget(self.loading_bar)  # Vẫn giữ lại nhưng không hiển thị
        self.setLayout(main_layout)

        # Logic loading
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(60)
        
        # Bắt đầu animation cho spinner
        self.spinner.start()

    def on_audio_loaded(self, media_content):
        # Được gọi khi luồng tải âm thanh hoàn tất
        self.player.setMedia(media_content)
        # Phát nếu đã sẵn sàng
        if self.player.mediaStatus() in [QMediaPlayer.BufferedMedia, QMediaPlayer.LoadedMedia]:
            self.player.play()

    def center(self):
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def handle_media_status(self, status):
        # Phát nhạc khi media đã được tải hoàn toàn
        if status == QMediaPlayer.BufferedMedia or status == QMediaPlayer.LoadedMedia:
            self.player.play()

    def update_progress(self):
        self.progress += 1
        self.loading_bar.setValue(self.progress)  # Vẫn cập nhật giá trị nhưng không hiển thị
        if self.progress >= 100:
            self.timer.stop()
            self.spinner.stop()
            self.close()

    def closeEvent(self, event):
        self.player.stop()
        # Đảm bảo dừng thread trước khi đóng cửa sổ
        if self.audio_loader.isRunning():
            self.audio_loader.terminate()
            self.audio_loader.wait()
        self.closed.emit()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BootWindow()
    window.show()
    sys.exit(app.exec_())