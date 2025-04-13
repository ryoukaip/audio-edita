from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtGui import QFont, QIcon
from screen.function.system.function_scrollarea import CustomScrollArea
from screen.function.system.function_marqueelabel import MarqueeLabel
from screen.function.system.system_thememanager import ThemeManager

class DownloadUI(QWidget):
    def __init__(self, placeholder_text="paste url here"):
        super().__init__()
        self.downloaded_files = []
        self.font_family = None
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_colors)
        
        self.initUI(placeholder_text)
    
    def initUI(self, placeholder_text):
        # Tải font
        from PyQt5.QtGui import QFontDatabase
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(self.font_family))

        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Container nhập link
        self.link_container = QWidget()
        self.update_link_container_stylesheet()
        link_layout = QHBoxLayout(self.link_container)
        link_layout.setContentsMargins(10, 10, 10, 10)
        link_layout.setSpacing(10)

        # Ô nhập link
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText(placeholder_text)
        self.link_input.setFont(QFont(self.font_family, 12))
        self.link_input.setFixedHeight(40)
        self.link_input.setStyleSheet("""
            border-radius: 8px;
            border: none;
            padding: 5px;
            color: #ffffff;
        """)
        link_layout.addWidget(self.link_input)

        # Nút paste
        self.paste_btn = QPushButton()
        self.paste_btn.setFixedSize(40, 40)
        self.paste_btn.setIcon(QIcon("./icon/paste.png"))
        self.paste_btn.setIconSize(QSize(20, 20))
        self.paste_btn.setStyleSheet(self.get_button_stylesheet())
        self.paste_btn.clicked.connect(self.paste_link)
        link_layout.addWidget(self.paste_btn)

        # Nút download
        self.download_btn = QPushButton()
        self.download_btn.setFixedSize(40, 40)
        self.download_btn.setIcon(QIcon("./icon/download.png"))
        self.download_btn.setIconSize(QSize(20, 20))
        self.download_btn.setStyleSheet(self.get_button_stylesheet())
        # Không connect ở đây, sẽ để lớp sử dụng connect sau
        link_layout.addWidget(self.download_btn)

        layout.addWidget(self.link_container)

        # Scroll area cho danh sách tải
        self.scroll_area = CustomScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(5)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.setStyleSheet("background-color: #282a32;")

    def get_button_stylesheet(self):
        """Tạo stylesheet cho các nút Paste và Download dựa trên theme hiện tại"""
        return f"""
            QPushButton {{
                background-color: {self.current_colors['highlight']};
                border-radius: 10px;
                border: none;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.current_colors['background']};
                border: none;
            }}
        """

    def get_link_container_stylesheet(self):
        """Tạo stylesheet cho link_container dựa trên theme hiện tại"""
        return f"""
            background-color: {self.current_colors['secondary']};
            border-radius: 15px;
            border: 3px solid #FBFFE4;
        """

    def get_file_widget_stylesheet(self):
        """Tạo stylesheet cho file_widget dựa trên theme hiện tại"""
        return f"""
            QWidget {{
                background-color: transparent;
                border-radius: 8px;
            }}
            QWidget:hover {{
                background-color: {self.current_colors['shadow']};
            }}
        """

    def get_progress_bar_stylesheet(self):
        """Tạo stylesheet cho progress_bar dựa trên theme hiện tại"""
        return f"""
            QProgressBar {{
                border: none;
                background-color: {self.current_colors['shadow']};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {self.current_colors['secondary']};
                border-radius: 2px;
            }}
        """

    def update_link_container_stylesheet(self):
        """Cập nhật stylesheet cho link_container"""
        self.link_container.setStyleSheet(self.get_link_container_stylesheet())

    def update_colors(self, colors):
        """Cập nhật màu sắc của các thành phần khi theme thay đổi"""
        self.current_colors = colors
        self.update_link_container_stylesheet()
        self.paste_btn.setStyleSheet(self.get_button_stylesheet())
        self.download_btn.setStyleSheet(self.get_button_stylesheet())
        # Cập nhật các file_widget và progress_bar trong scroll_layout
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.setStyleSheet(self.get_file_widget_stylesheet())
                # Tìm progress_bar trong main_layout của file_widget
                main_layout = widget.layout()
                for j in range(main_layout.count()):
                    sub_item = main_layout.itemAt(j)
                    if sub_item and sub_item.widget() and isinstance(sub_item.widget(), QProgressBar):
                        sub_item.widget().setStyleSheet(self.get_progress_bar_stylesheet())

    def paste_link(self):
        """Dán link từ clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        self.link_input.setText(clipboard.text())

    def add_download_item(self):
        """Thêm một mục tải vào danh sách"""
        file_widget = QWidget()
        file_widget.setStyleSheet(self.get_file_widget_stylesheet())
        main_layout = QVBoxLayout(file_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(12, 5, 12, 5)
        
        name_label = MarqueeLabel("Downloading...")
        name_label.setFont(QFont(self.font_family, 12))
        name_label.setStyleSheet("color: white;")
        name_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(name_label)
        
        info_layout.addStretch()
        
        size_label = QLabel("0 MB")
        size_label.setFont(QFont(self.font_family, 12))
        size_label.setStyleSheet("color: #7d8bd4;")
        size_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(size_label)
        
        main_layout.addLayout(info_layout)

        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(4)
        progress_bar.setStyleSheet(self.get_progress_bar_stylesheet())
        main_layout.addWidget(progress_bar)
        self.scroll_layout.addWidget(file_widget)
        
        # Cuộn mượt mà xuống dưới
        self.scroll_area.scroll_to_bottom()
        return name_label, size_label, progress_bar, main_layout

    def update_download_item(self, name_label, size_label, progress_bar, main_layout, file_name, file_size):
        """Cập nhật thông tin mục tải khi hoàn thành"""
        name_label.setText(file_name)
        size_label.setText(file_size)
        main_layout.removeWidget(progress_bar)
        progress_bar.deleteLater()
        self.downloaded_files.append((file_name, file_size))

    def remove_download_item(self, file_widget):
        """Xóa một mục tải khỏi danh sách"""
        self.scroll_layout.removeWidget(file_widget)
        file_widget.deleteLater()