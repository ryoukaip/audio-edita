import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import Qt, QSize, QPoint

# Import AudioDataManager
from screen.function.system.function_datamanager import AudioDataManager
from screen.function.playaudio.function_playaudio import DropAreaLabel

# Các import khác giữ nguyên
from menu_edit import MenuEditPage
from menu_separate import MenuSeparatePage
from menu_check import MenuCheckPage
from menu_download import MenuDownloadPage
from screen.edit.equalizer import EqualizerPage
from screen.edit.trim import TrimPage
from screen.edit.merge import MergePage
from screen.edit.split import SplitPage
from screen.edit.volume import VolumePage
from screen.edit.reverse import ReversePage
from screen.edit.speed import SpeedPage
from screen.edit.compress import CompressPage
from screen.edit.convert import ConvertPage
from screen.edit.voice import VoicePage
from screen.separate.separate import SeparatePage
from screen.separate.video2audio import Video2AudioPage
from screen.separate.noise import NoisePage
from screen.check.checkonline import CheckOnlinePage
from screen.check.checkoffline import CheckOfflinePage
from screen.download.youtube import YoutubeDownloadPage
from screen.download.tiktok import TiktokDownloadPage
from screen.download.facebook import FacebookDownloadPage
from screen.download.instagram import InstagramDownloadPage
from screen.download.x import XDownloadPage
from screen.download.soundcloud import SoundcloudDownloadPage
from screen.download.bluesky import BlueskyDownloadPage
from screen.download.tumblr import TumblrDownloadPage
from screen.download.reddit import RedditDownloadPage
from screen.download.bilibili import BilibiliDownloadPage
from screen.separate.output_separate import OutputSeparateWidget
from screen.function.mainscreen.function_titlebar import CustomTitleBar
from screen.function.mainscreen.function_sidebar import CustomSidebar

class AudioEditorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_button = None
        self.output_widget = None
        self.dragging = False
        self.drag_pos = QPoint()
        self.is_maximized = False
        self.page_mapping = {}
        self.previous_widget = None  # Lưu trữ màn hình trước đó
        
        # Khởi tạo AudioDataManager
        self.audio_data_manager = AudioDataManager()
        
        self.initUI()

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setWindowTitle("audio edita")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1c1b1f; color: white;")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.center_window()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout = content_layout

        self.title_bar = CustomTitleBar(self, font_family)
        self.sidebar = CustomSidebar(self, font_family)
        self.sidebar.buttonClicked.connect(self.handle_sidebar_button)
        
        self.stack = QStackedWidget()
        
        # Truyền AudioDataManager vào các trang
        self.add_page("MenuEdit", MenuEditPage())
        self.add_page("MenuSeparate", MenuSeparatePage())
        self.add_page("MenuCheck", MenuCheckPage())
        self.add_page("MenuDownload", MenuDownloadPage())
        self.add_page("Equalizer", EqualizerPage(self.audio_data_manager))
        self.add_page("Trim", TrimPage(self.audio_data_manager))
        self.add_page("Merge", MergePage(self.audio_data_manager))
        self.add_page("Split", SplitPage(self.audio_data_manager))
        self.add_page("Volume", VolumePage(self.audio_data_manager))
        self.add_page("Reverse", ReversePage(self.audio_data_manager))
        self.add_page("Speed", SpeedPage(self.audio_data_manager))
        self.add_page("Compress", CompressPage(self.audio_data_manager))
        self.add_page("Convert", ConvertPage(self.audio_data_manager))
        self.add_page("Voice", VoicePage(self.audio_data_manager))
        self.add_page("CheckOnline", CheckOnlinePage(self.audio_data_manager))
        self.add_page("CheckOffline", CheckOfflinePage())
        self.add_page("OutputSeparate", OutputSeparateWidget())
        self.add_page("Separate", SeparatePage(self.audio_data_manager))
        self.add_page("Video2Audio", Video2AudioPage(self.audio_data_manager))
        self.add_page("Noise", NoisePage(self.audio_data_manager))
        self.add_page("YoutubeDownload", YoutubeDownloadPage())
        self.add_page("TiktokDownload", TiktokDownloadPage())
        self.add_page("FacebookDownload", FacebookDownloadPage())
        self.add_page("InstagramDownload", InstagramDownloadPage())
        self.add_page("XDownload", XDownloadPage())
        self.add_page("SoundcloudDownload", SoundcloudDownloadPage())
        self.add_page("BlueskyDownload", BlueskyDownloadPage())
        self.add_page("TumblrDownload", TumblrDownloadPage())
        self.add_page("RedditDownload", RedditDownloadPage())
        self.add_page("BilibiliDownload", BilibiliDownloadPage())

        content_layout.addWidget(self.sidebar, 1)
        content_layout.addWidget(self.stack, 4)
        self.stack.setStyleSheet("""
            background-color: #282a32;
            border-top-left-radius: 22px;
        """)

        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(content_layout)

        self.sidebar.set_active_button(self.sidebar.edit_btn)
        self.is_maximized = False
        
        # Khi chuyển trang, xử lý hủy và tải lại tệp âm thanh
        self.stack.currentChanged.connect(self.on_screen_changed)

    def add_page(self, page_id, page_widget):
        """Thêm một trang vào stack và lưu vào từ điển ánh xạ."""
        index = self.stack.addWidget(page_widget)
        self.page_mapping[page_id] = page_widget

    def center_window(self):
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        window_rect = self.frameGeometry()
        center_point = screen_rect.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())

    def toggleMaximize(self):
        if not self.is_maximized:
            self.content_layout.setStretch(0, 1)
            self.content_layout.setStretch(1, 8)
        else:
            self.content_layout.setStretch(0, 1)
            self.content_layout.setStretch(1, 4)
        self.title_bar.toggleMaximize()

    def handle_sidebar_button(self, index, button):
        """Xử lý sự kiện nhấn nút sidebar, sử dụng định danh thay vì chỉ số."""
        if button == self.sidebar.edit_btn:
            page_id = "MenuEdit"
        elif button == self.sidebar.separate_btn:
            page_id = "MenuSeparate"
        elif button == self.sidebar.check_btn:
            page_id = "MenuCheck"
        elif button == self.sidebar.download_btn:
            page_id = "MenuDownload"
        else:
            return 
        
        page_widget = self.page_mapping.get(page_id)
        if page_widget:
            self.stack.setCurrentWidget(page_widget)
        self.sidebar.set_active_button(button)

    def on_screen_changed(self, index):
        """Xử lý khi màn hình thay đổi: hủy tệp âm thanh của màn hình cũ và tải lại cho màn hình mới."""
        # Lấy widget hiện tại
        current_widget = self.stack.widget(index)
        
        # Nếu có màn hình trước đó và khác với màn hình hiện tại, hủy tệp âm thanh cũ
        if self.previous_widget and self.previous_widget != current_widget:
            old_player = getattr(self.previous_widget, 'audio_player', None) or \
                        getattr(self.previous_widget, 'audio_player_input', None)
            if old_player and isinstance(old_player, DropAreaLabel):
                # Dừng phát và xóa media từ QMediaPlayer
                old_player.player.stop()
                old_player.player.setMedia(QMediaContent())
                # Xóa tệp tạm nếu có
                old_player._clear_temp_file()
                # Reset giao diện về trạng thái ban đầu (nếu cần)
                old_player.clear()

        # Tải lại tệp âm thanh cho màn hình hiện tại nếu cần
        if hasattr(current_widget, 'audio_player') or hasattr(current_widget, 'audio_player_input'):
            player = getattr(current_widget, 'audio_player', None) or \
                    getattr(current_widget, 'audio_player_input', None)
            if player and isinstance(player, DropAreaLabel):
                player.load_shared_audio()

        # Cập nhật widget trước đó
        self.previous_widget = current_widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioEditorUI()
    window.show()
    sys.exit(app.exec_())