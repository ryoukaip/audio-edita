from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QSizePolicy, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt
from screen.function.mainscreen.function_toolbar import ToolBar
from screen.menu.menu_edit import MenuEditPage
from screen.menu.menu_separate import MenuSeparatePage
from screen.menu.menu_check import MenuCheckPage
from screen.menu.menu_download import MenuDownloadPage

class MenuToolPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Thêm font cho ứng dụng
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 50, 12, 12)
        layout.setSpacing(0)  # Không có khoảng cách giữa các thành phần
        
        # Container đơn
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Không có margins
        container_layout.setSpacing(0)  # Không có khoảng cách
        
        # Tạo ToolBar
        self.tabs_container = ToolBar(self)
        self.content_stack = QStackedWidget()
        
        self.edit_page = MenuEditPage()
        self.content_stack.addWidget(self.edit_page)
        
        self.trim_page = MenuSeparatePage()
        self.content_stack.addWidget(self.trim_page)
        
        self.check_page = MenuCheckPage()
        self.content_stack.addWidget(self.check_page)
        
        self.download_page = MenuDownloadPage()
        self.content_stack.addWidget(self.download_page)
        
        # Kết nối sự kiện chuyển tab của ToolBar với content_stack
        self.tabs_container.content_stack.currentChanged.connect(self.on_tab_changed)
        
        # Thêm ToolBar và content_stack vào container với alignment
        container_layout.addWidget(self.tabs_container, 0, Qt.AlignCenter)
        container_layout.addWidget(self.content_stack, 1)  # Số 1 là stretch factor
        
        # Thêm container vào layout chính
        layout.addWidget(container)
        layout.addStretch()  # Đẩy lưới nút lên khi mở rộng cửa sổ
    
    def on_tab_changed(self, index):
        # Chuyển đổi nội dung theo tab được chọn
        self.content_stack.setCurrentIndex(index)