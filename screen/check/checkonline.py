import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QProgressBar, QSizePolicy, QGridLayout
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QPainter, QBrush, QColor
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_marqueelabel import MarqueeLabel
from screen.check.worker_shazam import ShazamApp
from screen.function.system.system_thememanager import ThemeManager

class RoundedPhotoLabel(QLabel):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setFixedSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(self.get_stylesheet())
        
    def get_stylesheet(self):
        """Tạo stylesheet cho nhãn ảnh bìa dựa trên theme hiện tại"""
        return f"""
            QLabel {{
                background-color: {self.theme_manager.get_theme_colors()['shadow']};
                border-radius: 18px;
            }}
        """

    def update_colors(self):
        """Cập nhật màu sắc khi theme thay đổi"""
        self.setStyleSheet(self.get_stylesheet())

    def setPixmap(self, pixmap):
        if pixmap:
            radius = 18
            target = QPixmap(self.width(), self.height())
            target.fill(Qt.transparent)
            
            painter = QPainter(target)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(self.theme_manager.get_theme_colors()['shadow'])))
            painter.setPen(Qt.NoPen)
            
            # Vẽ nền hình tròn
            painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)
            
            # Scaled và canh giữa hình ảnh
            scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Vẽ hình ảnh vào giữa nền với mask bo tròn
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            
            painter.end()
            super().setPixmap(target)
        else:
            super().setPixmap(QPixmap())

class CheckOnlinePage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager
        self.shazam_app = ShazamApp()
        
        # Sử dụng ThemeManager để quản lý màu sắc
        self.theme_manager = ThemeManager()
        self.current_colors = self.theme_manager.get_theme_colors()
        
        # Kết nối tín hiệu từ ThemeManager để cập nhật màu
        self.theme_manager.theme_changed.connect(self.update_colors)
        
        self.initUI()
    
    def initUI(self):
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))
        self.font_family = font_family

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        # Add function bar
        top_bar = FunctionBar("check copyright online", font_family, self)
        layout.addLayout(top_bar)

        # Results area
        self.results_widget = QWidget()
        results_layout = QHBoxLayout(self.results_widget)
        
        # Thay đổi QLabel thành RoundedPhotoLabel tùy chỉnh
        self.album_art_label = RoundedPhotoLabel(self.theme_manager)
        results_layout.addWidget(self.album_art_label)
        results_layout.addSpacing(10)
        
        self.info_widget = QWidget()
        self.info_widget.setFixedSize(400, 200)
        self.info_widget.setStyleSheet(self.get_info_widget_stylesheet())
        
        # Sử dụng QGridLayout thay vì QVBoxLayout và các QHBoxLayout
        info_layout = QGridLayout(self.info_widget)
        info_layout.setContentsMargins(25, 15, 15, 15)
        
        # Title row - Sử dụng MarqueeLabel thay vì QLabel
        self.title_label = MarqueeLabel("song title")
        self.title_label.setFont(QFont(font_family, 14, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        info_layout.addWidget(self.title_label, 0, 0, 1, 2)
        
        # Artist row - sử dụng grid để căn chỉnh chính xác
        artist_icon = QLabel()
        artist_icon.setPixmap(QIcon("./icon/artist.png").pixmap(26, 26))
        info_layout.addWidget(artist_icon, 1, 0)
        
        self.artist_label = MarqueeLabel("artist")
        self.artist_label.setFont(QFont(font_family, 12))
        self.artist_label.setStyleSheet("color: white;")
        info_layout.addWidget(self.artist_label, 1, 1)
        
        # Album row
        album_icon = QLabel()
        album_icon.setPixmap(QIcon("./icon/song.png").pixmap(23, 23))
        info_layout.addWidget(album_icon, 2, 0)
        
        self.album_label = MarqueeLabel("album")
        self.album_label.setFont(QFont(font_family, 12))
        self.album_label.setStyleSheet("color: white;")
        info_layout.addWidget(self.album_label, 2, 1)
        
        # Year row
        year_icon = QLabel()
        year_icon.setPixmap(QIcon("./icon/clock.png").pixmap(23, 23))
        info_layout.addWidget(year_icon, 3, 0)
        
        self.year_label = MarqueeLabel("year")
        self.year_label.setFont(QFont(font_family, 12))
        self.year_label.setStyleSheet("color: white;")
        info_layout.addWidget(self.year_label, 3, 1)
        
        # Đảm bảo cột 0 có kích thước cố định
        info_layout.setColumnMinimumWidth(0, 30)
        
        # Đảm bảo cột 1 được kéo giãn
        info_layout.setColumnStretch(1, 1)
        
        # Thêm khoảng trống ở dưới
        info_layout.setRowStretch(4, 1)
        
        results_layout.addWidget(self.info_widget)
        
        layout.addWidget(self.results_widget)
        layout.addSpacing(2)
        
        # DropAreaLabel (tích hợp AudioDataManager)
        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)
        
        # Button layout
        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedWidth(500) 
        self.progress_bar.hide()
        button_layout.addWidget(self.progress_bar)
        button_layout.addSpacing(15)
        
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setFixedSize(100, 40)
        self.analyze_button.setFont(QFont(font_family, 13))
        self.analyze_button.setStyleSheet(self.get_button_stylesheet())
        self.analyze_button.clicked.connect(self.start_recognition)
        button_layout.addWidget(self.analyze_button)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("background-color: #282a32;")
        
        # Tải tệp âm thanh từ AudioDataManager khi khởi tạo
        self.audio_player.load_shared_audio()

    def get_button_stylesheet(self):
        """Tạo stylesheet cho nút Analyze dựa trên theme hiện tại"""
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

    def get_info_widget_stylesheet(self):
        """Tạo stylesheet cho widget thông tin kết quả dựa trên theme hiện tại"""
        return f"""
            QWidget {{
                background-color: {self.current_colors['dark']};
                border-radius: 18px;
            }}
        """

    def update_colors(self, colors):
        """Cập nhật màu sắc của các thành phần khi theme thay đổi"""
        self.current_colors = colors
        self.analyze_button.setStyleSheet(self.get_button_stylesheet())
        self.album_art_label.update_colors()
        self.info_widget.setStyleSheet(self.get_info_widget_stylesheet())

    def toggle_playback(self):
        # Placeholder
        pass

    def on_file_dropped(self, file_path):
        text = self.shazam_app.on_file_dropped(file_path)
        self.audio_player.setText(text)
        # Tệp đã được lưu vào AudioDataManager qua DropAreaLabel

    def start_recognition(self):
        error, worker = self.shazam_app.start_recognition()
        if error:
            self.audio_player.setText(error)
            return
        
        self.progress_bar.show()
        self.analyze_button.setEnabled(False)
        
        worker.signals.finished.connect(self.process_results)
        worker.signals.error.connect(self.handle_error)
        self.shazam_app.threadpool.start(worker)
    
    def process_results(self, result):
        self.progress_bar.hide()
        self.analyze_button.setEnabled(True)
        
        error, title, artist, album, album_art, year = self.shazam_app.process_results(result)
        if error:
            self.handle_error(error)
            return
        
        self.title_label.setText(title)
        self.artist_label.setText(artist)
        self.album_label.setText(album)
        self.album_art_label.setPixmap(album_art)
        self.year_label.setText(year)
    
    def handle_error(self, error_message):
        self.progress_bar.hide()
        self.analyze_button.setEnabled(True)
        self.audio_player.setText(f"Error: {error_message}")
        self.title_label.setText("no matching result")
        self.artist_label.setText("???")
        self.album_label.setText("???")
        self.year_label.setText("???")
        self.album_art_label.setPixmap(QPixmap())

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)