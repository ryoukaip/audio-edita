import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.system.function_sliderequalizer import EqualizerControls
from screen.function.system.function_notiwindow import NotiWindow
from screen.edit.worker_equalizer import EqualizerWorker 

class EqualizerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_file = None
        self.initUI()

    def initUI(self):
        # Add font
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 25)

        # Add function bar
        top_bar = FunctionBar("equalizer", font_family, self)
        layout.addLayout(top_bar)
        layout.addSpacing(10)

        # File drop area
        self.audio_player = DropAreaLabel()
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        layout.addWidget(self.audio_player)
        layout.addSpacing(10)

        # Equalizer controls
        self.equalizer_controls = EqualizerControls(font_family)
        self.equalizer_controls.value_changed.connect(self.handle_eq_change)
        layout.addWidget(self.equalizer_controls)
        layout.addSpacing(15)

        # Stretch to push buttons to the bottom
        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_location_btn = QPushButton("Open file location")
        self.open_location_btn.setFixedSize(180, 40)
        self.open_location_btn.setFont(QFont(font_family, 13))
        self.open_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        self.open_location_btn.clicked.connect(self.open_file_location)
        button_layout.addWidget(self.open_location_btn)

        button_layout.addSpacing(10)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedSize(100, 40)
        self.export_btn.setFont(QFont(font_family, 13))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        self.export_btn.clicked.connect(self.export_audio)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

        # Set background style
        self.setStyleSheet("background-color: #282a32;")

    def on_file_dropped(self, file_path):
        print(f"File dropped: {file_path}")
        self.selected_audio_file = file_path

    def handle_eq_change(self, value):
        # Placeholder for real-time preview if needed
        pass

    def export_audio(self):
        try:
            if not self.selected_audio_file:
                noti_window = NotiWindow()
                noti_window.update_message("Please select an audio file first")
                return

            print(f"Starting export for file: {self.selected_audio_file}")
            print(f"EQ settings: {self.equalizer_controls.get_eq_settings()}")
            
            # Show render window
            self.render_window = RenderWindow(None)
            self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            screen_geometry = QApplication.desktop().screenGeometry()
            window_geometry = self.render_window.geometry()
            self.render_window.move(
                (screen_geometry.width() - window_geometry.width()) // 2,
                (screen_geometry.height() - window_geometry.height()) // 2
            )
            self.render_window.show()

            self.export_btn.setEnabled(False)

            # Gather equalizer settings
            eq_settings = self.equalizer_controls.get_eq_settings()

            # Create worker thread
            self.worker = EqualizerWorker(self.selected_audio_file, eq_settings)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.finished.connect(self.on_export_finished)
            self.worker.error.connect(self.on_export_error)
            self.worker.start()
            print("Worker thread started")
        except Exception as e:
            print(f"Error in export_audio: {str(e)}")
            noti_window = NotiWindow()
            noti_window.update_message(f"Error: {str(e)}")
            self.export_btn.setEnabled(True)

    def update_progress(self, progress, status, time_remaining):
        self.render_window.updateProgress(progress)
        self.render_window.updateStatus(status)
        self.render_window.updateTimeRemaining(time_remaining)

    def on_export_finished(self, output_file):
        print(f"Export finished, output file: {output_file}")
        self.render_window.updateProgress(100)
        self.render_window.updateStatus("Export complete!")
        self.render_window.updateTimeRemaining("Done!")
        self.open_file_location()
        QTimer.singleShot(1000, self.render_window.close)
        self.audio_player.set_audio_file(output_file)
        self.export_btn.setEnabled(True)

    def on_export_error(self, error_message):
        self.render_window.close()
        noti_window = NotiWindow()
        noti_window.update_message(f"Export failed: {error_message}")
        self.export_btn.setEnabled(True)

    def open_file_location(self):
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        output_dir = os.path.join(documents_path, "audio-edita", "edit", "equalizer")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuEdit")
            if page_widget:
                stack.setCurrentWidget(page_widget)