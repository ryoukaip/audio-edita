import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QPoint

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
from screen.check.checkonline import CheckOnlinePage
from screen.check.checkoffline import CheckOfflinePage
from screen.download.youtube import YoutubeDownloadPage
from screen.download.tiktok import TiktokDownloadPage
from screen.download.facebook import FacebookDownloadPage
from screen.download.instagram import InstagramDownloadPage
from screen.download.x import XDownloadPage
from screen.download.soundcloud import SoundcloudDownloadPage
from screen.download.bandcamp import BandcampDownloadPage
from screen.download.deezer import DeezerDownloadPage
from screen.download.tidal import TidalDownloadPage
from screen.download.mixcloud import MixcloudDownloadPage
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
        self.initUI()

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setWindowTitle("audio edita")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1c1b1f; color: white;")
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # Hỗ trợ opacity
        
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
        self.stack.addWidget(MenuEditPage())
        self.stack.addWidget(MenuSeparatePage())
        self.stack.addWidget(MenuCheckPage())
        self.stack.addWidget(MenuDownloadPage())
        self.stack.addWidget(EqualizerPage())
        self.stack.addWidget(TrimPage())
        self.stack.addWidget(MergePage())
        self.stack.addWidget(SplitPage())
        self.stack.addWidget(VolumePage())
        self.stack.addWidget(ReversePage())
        self.stack.addWidget(SpeedPage())
        self.stack.addWidget(CompressPage())
        self.stack.addWidget(ConvertPage())
        self.stack.addWidget(VoicePage())
        self.stack.addWidget(CheckOnlinePage())
        self.stack.addWidget(CheckOfflinePage())
        self.stack.addWidget(OutputSeparateWidget())
        self.stack.addWidget(SeparatePage())
        self.stack.addWidget(Video2AudioPage())
        self.stack.addWidget(YoutubeDownloadPage())
        self.stack.addWidget(TiktokDownloadPage())
        self.stack.addWidget(FacebookDownloadPage())
        self.stack.addWidget(InstagramDownloadPage())
        self.stack.addWidget(XDownloadPage())
        self.stack.addWidget(SoundcloudDownloadPage())
        self.stack.addWidget(BandcampDownloadPage())
        self.stack.addWidget(DeezerDownloadPage())
        self.stack.addWidget(TidalDownloadPage())
        self.stack.addWidget(MixcloudDownloadPage())

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
        if button == self.sidebar.edit_btn:
            self.stack.setCurrentIndex(0)  # MenuEditPage
        elif button == self.sidebar.separate_btn:
            self.stack.setCurrentIndex(1)  # MenuSeparatePage
        elif button == self.sidebar.check_btn:
            self.stack.setCurrentIndex(2)  # MenuCheckPage
        elif button == self.sidebar.download_btn:
            self.stack.setCurrentIndex(3)  # MenuDownloadPage
        self.sidebar.set_active_button(button)