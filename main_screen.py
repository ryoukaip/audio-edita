import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import Qt, QSize, QPoint

from screen.function.system.system_datamanager import AudioDataManager
from screen.function.system.system_thememanager import ThemeManager
from screen.function.playaudio.function_playaudio import DropAreaLabel

from screen.menu.menu_tool import MenuToolPage
from screen.menu.menu_edit import MenuEditPage
from screen.menu.menu_separate import MenuSeparatePage
from screen.menu.menu_check import MenuCheckPage
from screen.menu.menu_download import MenuDownloadPage
from screen.menu.menu_community import MenuCommunityPage
from screen.menu.menu_setting import MenuSettingPage

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
        self.previous_widget = None

        self.theme_manager = ThemeManager()
        self.audio_data_manager = AudioDataManager()

        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.initUI()

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.center_window()

        central_widget = QWidget()
        # Set solid background for central_widget
        central_widget.setStyleSheet("background-color: #1c1b1f;")
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
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: #282a32;
                border-top-left-radius: 22px;
            }}
        """)

        self.add_page("MenuTool", MenuToolPage())
        self.add_page("MenuEdit", MenuEditPage())
        self.add_page("MenuSeparate", MenuSeparatePage())
        self.add_page("MenuCheck", MenuCheckPage())
        self.add_page("MenuDownload", MenuDownloadPage())
        self.add_page("MenuCommunity", MenuCommunityPage())
        setting_page = MenuSettingPage()
        setting_page.theme_changed.connect(self.update_theme)
        self.add_page("MenuSetting", setting_page)

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

        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(content_layout)

        self.sidebar.set_active_button(self.sidebar.tool_btn)
        self.is_maximized = False
        self.stack.currentChanged.connect(self.on_screen_changed)

    def add_page(self, page_id, page_widget):
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
        if button == self.sidebar.tool_btn:
            page_id = "MenuTool"
        elif button == self.sidebar.community_btn:
            page_id = "MenuCommunity"
        elif button == self.sidebar.setting_btn:
            page_id = "MenuSetting"
        else:
            return
        page_widget = self.page_mapping.get(page_id)
        if page_widget:
            self.stack.setCurrentWidget(page_widget)
        self.sidebar.set_active_button(button)

    def on_screen_changed(self, index):
        current_widget = self.stack.widget(index)
        if self.previous_widget and self.previous_widget != current_widget:
            old_player = getattr(self.previous_widget, 'audio_player', None) or \
                        getattr(self.previous_widget, 'audio_player_input', None)
            if old_player and isinstance(old_player, DropAreaLabel):
                old_player.player.stop()
                old_player.player.setMedia(QMediaContent())
                old_player._clear_temp_file()
                old_player.clear()
        if hasattr(current_widget, 'audio_player') or hasattr(current_widget, 'audio_player_input'):
            player = getattr(current_widget, 'audio_player', None) or \
                    getattr(current_widget, 'audio_player_input', None)
            if player and isinstance(player, DropAreaLabel):
                player.load_shared_audio()
        self.previous_widget = current_widget

    def update_theme(self, colors):
        self.theme_manager.update_theme(colors)

    def on_theme_changed(self, colors):
        """Xử lý khi theme thay đổi"""
        # Áp dụng theme cho sidebar
        if hasattr(self.sidebar, 'set_theme'):
            self.sidebar.set_theme(colors)
            
        # Áp dụng theme cho title bar
        if hasattr(self.title_bar, 'set_theme'):
            self.title_bar.set_theme(colors)
            
        # Áp dụng theme cho tất cả các trang
        for page_id, page_widget in self.page_mapping.items():
            if hasattr(page_widget, 'set_theme'):
                page_widget.set_theme(colors)