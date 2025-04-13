import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QVBoxLayout, QScrollArea)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase, QDesktopServices
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_scrollarea import CustomScrollArea
from screen.function.system.system_thememanager import ThemeManager

class OutputSeparateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_path = None
        self.original_filename = None
        self.scroll_layout = None

        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_button_colors)
        
        self.setupUI()

    def setupUI(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Create custom scroll area
        scroll_area = CustomScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create scroll content widget
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)

        # Sẽ được điền khi update_audio_files được gọi
        self.scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

        # Add buttons
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Open file location button
        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())
        self.open_location_btn.clicked.connect(self.open_file_location)

        # Add Back button
        done_btn = QPushButton("Back")
        done_btn.setFixedSize(100, 40)
        done_btn.setFont(QFont(font_family, 13))
        done_btn.setStyleSheet(self.get_button_stylesheet())
        done_btn.clicked.connect(self.go_back)

        # Add buttons to layout in correct order
        button_layout.addWidget(self.open_location_btn)
        button_layout.addSpacing(10)  
        button_layout.addWidget(done_btn)
        main_layout.addLayout(button_layout)

    def get_button_stylesheet(self):
        """Tạo stylesheet cho các nút dựa trên theme hiện tại"""
        return f"""
            QPushButton {{
                background-color: {self.current_colors['shadow']};
                border-radius: 12px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.current_colors['dark']};
            }}
        """

    def update_button_colors(self, colors):
        """Cập nhật màu sắc của các nút khi theme thay đổi"""
        self.current_colors = colors
        self.open_location_btn.setStyleSheet(self.get_button_stylesheet())

    def update_audio_files(self, output_path, original_filename):
        """Cập nhật widget với thông tin về đường dẫn output và file gốc"""
        self.output_path = output_path
        self.original_filename = original_filename
        
        # Xóa các widget cũ (trừ stretch ở cuối)
        self.clear_layout_except_last()
        
        # Tải các file âm thanh mới
        self.load_audio_files()

    def clear_layout_except_last(self):
        """Xóa tất cả các widget trong scroll_layout ngoại trừ item cuối cùng (stretch)"""
        if self.scroll_layout:
            for i in reversed(range(self.scroll_layout.count() - 1)):  # -1 để giữ lại stretch
                item = self.scroll_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                    layout = item.layout()
                    if layout:
                        self.clear_layout(layout)
                    self.scroll_layout.removeItem(item)
    
    def clear_layout(self, layout):
        """Xóa hoàn toàn một layout và các widget con"""
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                child_layout = item.layout()
                if child_layout:
                    self.clear_layout(child_layout)

    def load_audio_files(self):
        """Tìm và tải các file âm thanh đã tách"""
        if not self.output_path or not self.original_filename:
            return

        # Lấy tên cơ sở (không có extension)
        base_name = os.path.splitext(os.path.basename(self.original_filename))[0]
        
        # Kiểm tra thư mục con
        subfolder_path = os.path.join(self.output_path, base_name)
        
        if os.path.exists(subfolder_path):
            # Tìm tất cả file audio trong thư mục con
            audio_files = []
            for file in os.listdir(subfolder_path):
                if file.endswith(('.wav', '.mp3')):
                    audio_files.append((file, os.path.join(subfolder_path, file)))
            
            # Sắp xếp file theo tên (để có thứ tự nhất quán)
            audio_files.sort()
            
            # Tạo player cho mỗi file âm thanh
            for filename, filepath in audio_files:
                track_name = os.path.splitext(filename)[0]
                self.add_track_player(self.scroll_layout, track_name, filepath)
        
        # Cập nhật nút mở vị trí file
        if os.path.exists(subfolder_path):
            self.open_location_btn.setEnabled(True)
            # Lưu đường dẫn để mở khi cần
            self.output_folder = subfolder_path
        else:
            self.open_location_btn.setEnabled(False)

    def add_track_player(self, layout, track_name, audio_file):
        """Thêm một hàng player cho một track"""
        track_layout = QHBoxLayout()
        track_layout.setContentsMargins(10, 5, 10, 5)
        track_layout.setSpacing(20)

        # Icon - Chọn icon dựa trên tên track
        icon_label = QLabel()
        icon_label.setFixedSize(30, 30)
        icon_label.setStyleSheet("QLabel { background-color: transparent; border: none; }")
        
        # Chọn icon dựa vào tên track
        icon_path = "./icon/micro.png"  # Mặc định
        track_lower = track_name.lower()
        if "vocal" in track_lower:
            icon_path = "./icon/micro.png"
        elif "accompaniment" in track_lower:
            icon_path = "./icon/music.png"  
        elif "other" in track_lower:
            icon_path = "./icon/music.png" 
        elif "bass" in track_lower:
            icon_path = "./icon/bass.png"  
        elif "drums" in track_lower:
            icon_path = "./icon/drum.png" 
        elif "piano" in track_lower:
            icon_path = "./icon/piano.png" 
        
        icon = QIcon(icon_path)
        icon_label.setPixmap(icon.pixmap(30, 30))
        
        # Audio player
        audio_player = DropAreaLabel()
        audio_player.setFixedHeight(220)  
        audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Thiết lập file âm thanh cho player
        audio_player.set_audio_file(audio_file)
        
        track_layout.addWidget(icon_label)
        track_layout.addWidget(audio_player)
        
        # Thêm vào layout trước stretch
        # Lấy vị trí của stretch (item cuối cùng)
        stretch_index = layout.count() - 1
        layout.insertLayout(stretch_index, track_layout)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "separate")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("Separate")
            if page_widget:
                stack.setCurrentWidget(page_widget)