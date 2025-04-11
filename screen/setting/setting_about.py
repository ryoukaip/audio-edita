from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class AboutTab(QWidget):
    def __init__(self, font_family="Arial", parent=None):
        super().__init__(parent)
        self.initUI(font_family)

    def initUI(self, font_family):
        # Layout chính cho tab About
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(10)

        # Layout hai cột
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(2)

        # Cột bên trái
        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignTop)
        
        # Widget chứa nội dung cột trái với chiều rộng cố định
        left_widget = QWidget()
        left_widget.setFixedWidth(450)  # Chiều rộng cố định cho cột trái
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignLeft)  # Căn lề trái

        # Ảnh furry.png
        image_label = QLabel()
        pixmap = QPixmap("./icon/furry.png")
        image_label.setPixmap(pixmap.scaled(380, 380, Qt.KeepAspectRatio))  # Chiều rộng khớp với cột
        image_label.setAlignment(Qt.AlignCenter)  # Căn giữa ảnh
        left_layout.addWidget(image_label)

        # Thêm khoảng trống linh hoạt để đẩy nội dung xuống dưới
        left_layout.addStretch()

        # Thông tin dưới cùng cột trái
        left_info = [
            "Privacy Policy",
            "EULA - End User License Agreement",
            "Version: Microsoft Store - 1.0.0"
        ]
        for info in left_info:
            info_label = QLabel(info)
            info_label.setFont(QFont(font_family, 10))
            info_label.setStyleSheet("color: white;")
            left_layout.addWidget(info_label)  # Đã căn trái nhờ left_layout

        left_column.addWidget(left_widget)

        # Cột bên phải
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignTop)

        # Widget chứa nội dung cột phải với chiều rộng cố định
        right_widget = QWidget()
        right_widget.setFixedWidth(300)  # Chiều rộng cố định cho cột phải
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignHCenter)  # Căn giữa ngang

        # Tiêu đề nhà tài trợ
        sponsors_title = QLabel("--- Sponsors ---")
        sponsors_title.setFont(QFont(font_family, 12, QFont.Bold))
        sponsors_title.setStyleSheet("color: white;")
        sponsors_title.setAlignment(Qt.AlignCenter)  # Căn giữa tiêu đề
        right_layout.addWidget(sponsors_title)

        # Danh sách nhà tài trợ
        sponsors = [
            "xAI Corporation",
            "Tech Innovators Inc.",
            "Future Fund",
            "Community Supporters"
        ]
        for sponsor in sponsors:
            sponsor_label = QLabel(sponsor)
            sponsor_label.setFont(QFont(font_family, 11.5))
            sponsor_label.setStyleSheet("color: white;")
            sponsor_label.setAlignment(Qt.AlignCenter)  # Căn giữa từng dòng
            right_layout.addWidget(sponsor_label)

        # Thêm khoảng trống phía dưới cột phải
        right_layout.addStretch()

        right_column.addWidget(right_widget)

        # Thêm hai cột vào layout chính
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)
        main_layout.addLayout(columns_layout)

        # Thêm khoảng trống phía dưới toàn bộ giao diện
        main_layout.addStretch()