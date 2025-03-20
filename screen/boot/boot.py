import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class BootWindow(QWidget):
    closed = pyqtSignal()  # Tín hiệu khi cửa sổ đóng

    def __init__(self):
        super().__init__()

        # Thiết lập cửa sổ không khung và kích thước cố định
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 600)

        # Căn giữa màn hình
        self.center()
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("./audio/edita.mp3")))
        self.player.setVolume(100) 
        self.showEvent = lambda e: self.player.play()

        # Nạp font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))
 
        # Tạo layout chính
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Không có lề
        main_layout.setSpacing(0)  # Không có khoảng cách giữa các thành phần

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

        # Thêm chữ vào góc trên bên trái
        location_label = QLabel("Hoan Kiem Lake - Hanoi")
        location_label.setFont(QFont(font_family, 12, QFont.Bold))
        location_label.setStyleSheet("color: white;")
        location_label.setContentsMargins(10, 5, 10, 5)
        
        # Đặt vị trí cho location_label
        location_label.setFixedSize(location_label.sizeHint())
        location_label.move(20, 20)  # Vị trí tại góc trên bên trái

        # Thiết lập container để có thể đặt label lên trên ảnh
        image_container.setStyleSheet("background-color: transparent;")
        image_container_layout.addWidget(image_label)
        
        # Overlay container để đặt location_label lên trên ảnh
        overlay_container = QWidget(image_container)
        overlay_container.setGeometry(0, 0, self.width(), self.height())
        location_label.setParent(overlay_container)
        location_label.move(20, 20)

        # Tạo khung chữ nhật dưới đáy
        bottom_frame = QWidget()
        bottom_frame.setStyleSheet("background-color: #1c1b1f;")
        bottom_frame.setFixedHeight(100)

        # Layout cho khung dưới
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(35, 0, 35, 0)  # Lề trái và phải 35px
        bottom_layout.setSpacing(10)  # Khoảng cách giữa các thành phần

        # App icon
        app_icon = QLabel()
        pixmap_icon = QPixmap("./icon/edita.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app_icon.setPixmap(pixmap_icon)

        # App title
        app_title = QLabel("audio edita")
        app_title.setFont(QFont(font_family, 18, QFont.Bold))
        app_title.setStyleSheet("color: white;")

        # Nhãn trạng thái (sẽ cập nhật %)
        self.status_label = QLabel("loading resources - 0%")
        self.status_label.setFont(QFont(font_family, 14))
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Thêm các thành phần vào bottom_layout
        bottom_layout.addWidget(app_icon)
        bottom_layout.addWidget(app_title)
        bottom_layout.addStretch()  # Đẩy phần trạng thái sang phải
        bottom_layout.addWidget(self.status_label)

        # Áp dụng layout cho khung dưới
        bottom_frame.setLayout(bottom_layout)

        # Tạo thanh loading
        self.loading_bar = QProgressBar(self)
        self.loading_bar.setFixedHeight(8)  # Chiều cao thanh loading
        self.loading_bar.setTextVisible(False)  # Ẩn text phần trăm
        self.loading_bar.setValue(0)  # Giá trị ban đầu là 0%
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

        # Thêm các thành phần vào layout chính
        main_layout.addWidget(image_container)
        main_layout.addStretch()  # Đẩy khung chữ nhật xuống dưới
        main_layout.addWidget(bottom_frame)
        main_layout.addWidget(self.loading_bar)

        # Áp dụng layout chính
        self.setLayout(main_layout)

        # Thiết lập logic loading 6 giây
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(60)  

    def center(self):
        # Căn giữa màn hình
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_progress(self):
        # Cập nhật thanh tiến độ và nhãn trạng thái
        self.progress += 1
        self.loading_bar.setValue(self.progress)
        self.status_label.setText(f"loading resources - {self.progress}%")

        # Khi đạt 100%, dừng timer và đóng cửa sổ
        if self.progress >= 100:
            self.timer.stop()
            self.close()

    def closeEvent(self, event):
        self.player.stop()
        self.closed.emit()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BootWindow()
    window.show()
    sys.exit(app.exec_())