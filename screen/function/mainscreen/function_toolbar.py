from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QTimer

class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        
        # Layout chính
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Tiêu đề căn giữa
        self.title = QLabel("audio editing")  # Khởi tạo với "audio editing"
        self.title.setFont(QFont(font_family, 15))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white;")
        self.main_layout.addWidget(self.title)
        
        # Container cho các nút
        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        self.button_layout.setSpacing(15)  # Khoảng cách giữa các nút
        self.button_layout.addStretch()  # Căn giữa bằng stretch
        
        # Danh sách các nút
        self.buttons = []
        
        # Tạo các nút với icon
        edit_icon = QIcon("./icon/edit.png")
        trim_icon = QIcon("./icon/trim.png")
        check_icon = QIcon("./icon/check.png")
        download_icon = QIcon("./icon/download.png")
        
        self.edit_button = QPushButton()
        self.edit_button.setIcon(edit_icon)
        self.edit_button.setIconSize(QSize(22, 22))
        self.edit_button.setFixedSize(40, 40)
        self.edit_button.setStyleSheet("background: transparent; border: none;")
        self.edit_button.clicked.connect(lambda: self.switch_page(0))
        
        self.trim_button = QPushButton()
        self.trim_button.setIcon(trim_icon)
        self.trim_button.setIconSize(QSize(22, 22))
        self.trim_button.setFixedSize(40, 40)
        self.trim_button.setStyleSheet("background: transparent; border: none;")
        self.trim_button.clicked.connect(lambda: self.switch_page(1))
        
        self.check_button = QPushButton()
        self.check_button.setIcon(check_icon)
        self.check_button.setIconSize(QSize(22, 22))
        self.check_button.setFixedSize(40, 40)
        self.check_button.setStyleSheet("background: transparent; border: none;")
        self.check_button.clicked.connect(lambda: self.switch_page(2))
        
        self.download_button = QPushButton()
        self.download_button.setIcon(download_icon)
        self.download_button.setIconSize(QSize(22, 22))
        self.download_button.setFixedSize(40, 40)
        self.download_button.setStyleSheet("background: transparent; border: none;")
        self.download_button.clicked.connect(lambda: self.switch_page(3))
        
        # Thêm các nút vào layout
        self.buttons.extend([self.edit_button, self.trim_button, self.check_button, self.download_button])
        for button in self.buttons:
            self.button_layout.addWidget(button)
        self.button_layout.addStretch()  # Căn giữa bằng stretch
        
        self.main_layout.addWidget(button_container)
        
        # Thanh động
        self.indicator = QWidget(button_container)
        self.indicator.setStyleSheet("background-color: #98a4e6;")
        self.indicator.setFixedHeight(2)
        self.indicator.setFixedWidth(40)
        self.indicator.hide()  # Ẩn trước để tránh hiển thị sai vị trí
        
        # Khu vực nội dung (thay cho tab)
        self.content_stack = QStackedWidget()
        self.setup_edit_page(font_family)
        self.setup_trim_page(font_family)
        self.setup_check_page(font_family)
        self.setup_download_page(font_family)
        self.main_layout.addWidget(self.content_stack)
        
        # Khởi tạo trạng thái ban đầu với edit_icon
        self.switch_page(0)
        
        # Đặt lịch cập nhật vị trí indicator sau khi UI được render
        QTimer.singleShot(0, lambda: self.update_indicator_position(0))
    
    def setup_edit_page(self, font_family):
        self.edit_page = QWidget()
        self.content_stack.addWidget(self.edit_page)

    def setup_trim_page(self, font_family):
        self.trim_page = QWidget()
        self.content_stack.addWidget(self.trim_page)

    def setup_check_page(self, font_family):
        self.check_page = QWidget()
        self.content_stack.addWidget(self.check_page)
        
    def setup_download_page(self, font_family):
        self.download_page = QWidget()
        self.content_stack.addWidget(self.download_page)
    
    def update_indicator_position(self, index):
        # Lấy button đang được chọn
        button = self.buttons[index]
        
        # Tính toán vị trí dựa trên button
        button_rect = button.geometry()
        indicator_x = button_rect.center().x() - self.indicator.width() // 2
        pos_y = button_rect.bottom()  # Đặt ngay dưới nút
        
        # Cập nhật vị trí
        self.indicator.setGeometry(indicator_x, pos_y, self.indicator.width(), 2)
        self.indicator.show()  # Hiển thị indicator sau khi đã tính toán vị trí đúng
        self.indicator.raise_()
    
    def switch_page(self, index):
        # Chuyển nội dung
        self.content_stack.setCurrentIndex(index)
        # Cập nhật tiêu đề dựa trên nút được chọn
        titles = ["audio editing", "audio separate", "audio checking", "audio download"]
        self.title.setText(titles[index])
        # Di chuyển thanh động
        self.update_indicator_position(index)