# screen/separate/separate.py
import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QButtonGroup, QStackedWidget, QApplication
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QFont, QFontDatabase
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.separate.worker_separate import start_separation
from screen.function.system.function_renderwindow import RenderWindow
from screen.separate.output_separate import OutputSeparateWidget

class SeparatePage(QWidget):
    def __init__(self, audio_data_manager):
        super().__init__()
        self.audio_data_manager = audio_data_manager 
        self.selected_file = None
        self.selected_stems = 2  # Default value
        self.initUI()  
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Main layout setup
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 15, 25, 25)

        # Top bar
        main_layout.addLayout(FunctionBar("vocal separation", font_family, self))
        main_layout.addSpacing(10)

        # Drop area and columns
        drop_columns_container = QWidget()
        drop_columns_layout = QVBoxLayout(drop_columns_container)
        drop_columns_layout.setContentsMargins(0, 0, 0, 0)
        drop_columns_layout.setSpacing(20)

        self.audio_player = DropAreaLabel(self.audio_data_manager, allow_drop=True)
        self.audio_player.setFixedHeight(220)
        self.audio_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.audio_player.file_dropped.connect(self.on_file_dropped)
        drop_columns_layout.addWidget(self.audio_player)

        # Columns setup
        columns_container = QWidget()
        columns_container.setFixedWidth(600)
        columns_layout = QHBoxLayout(columns_container)
        columns_layout.setContentsMargins(0, 10, 0, 0)

        # Button group for stem selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.handle_stem_selection)

        # Common button style
        button_style = """
            QPushButton {
                background-color: #323754;
                border-radius: 15px;
                color: white;
            }
            QPushButton:checked {
                background-color: #7d8bd4;
            }
        """

        # Left and right column options
        self.create_column(columns_layout, "left", [("vocal + instrument", "2")], font_family, button_style)
        self.create_column(columns_layout, "right", [("vocal + 3 instrument", "4")], font_family, button_style)

        drop_columns_layout.addWidget(columns_container, 0, Qt.AlignCenter)
        drop_columns_layout.addStretch()
        main_layout.addWidget(drop_columns_container)

        # Export button
        export_btn = self.create_export_button(font_family)
        main_layout.addWidget(export_btn, 0, Qt.AlignRight | Qt.AlignBottom)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_widget)
        self.setLayout(layout)

        # Default selection and load audio
        self.button_group.buttons()[0].setChecked(True)
        self.audio_player.load_shared_audio()

    def create_column(self, parent_layout, side, options, font_family, button_style):
        """Helper method to create a column with options"""
        container = QWidget()
        column_layout = QVBoxLayout(container)
        column_layout.setSpacing(20)
        margins = (50, 0, 25, 0) if side == "left" else (25, 0, 50, 0)
        column_layout.setContentsMargins(*margins)

        for text, number in options:
            row = QHBoxLayout()
            row.setSpacing(15)

            btn = QPushButton(number)
            btn.setFixedSize(54, 50)
            btn.setFont(QFont(font_family, 16))
            btn.setCheckable(True)
            btn.setStyleSheet(button_style)
            self.button_group.addButton(btn)

            label = QLabel(text)
            label.setFont(QFont(font_family, 13))
            label.setStyleSheet("color: white;")

            row.addWidget(btn)
            row.addWidget(label)
            row.addStretch()
            column_layout.addLayout(row)

        parent_layout.addWidget(container)

    def create_export_button(self, font_family):
        """Helper method to create export button"""
        btn = QPushButton("Export")
        btn.setFixedSize(100, 40)
        btn.setFont(QFont(font_family, 13))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #292d47;
            }
        """)
        btn.clicked.connect(self.show_output_widget)
        return btn

    def show_output_widget(self):
        if not self.selected_file:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Please select an audio file first")
            return

        try:
            # Create and show render window
            self.render_window = RenderWindow(None)
            self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            
            # Căn giữa cửa sổ trên màn hình
            screen_geometry = QApplication.desktop().screenGeometry()
            window_geometry = self.render_window.geometry()
            self.render_window.move(
                (screen_geometry.width() - window_geometry.width()) // 2,
                (screen_geometry.height() - window_geometry.height()) // 2
            )
            
            # Initial setup
            self.render_window.updateProgress(0)
            self.render_window.updateStatus("Initializing separation...")
            self.render_window.updateTimeRemaining("Calculating...")
            self.render_window.show()

            # Get selected stems
            stems = self.selected_stems
            
            # Create output directory
            documents_path = os.path.expanduser("~\\Documents\\audio-edita")
            output_dir = os.path.join(documents_path, "separate")
            os.makedirs(output_dir, exist_ok=True)

            # Khởi tạo bộ đếm thời gian giả để cập nhật tiến trình
            self.fake_progress_steps = [
                (2, 5, "Loading audio file...", "Preparing..."),
                (5, 15, "Analyzing audio content...", "50 seconds remaining"),
                (8, 25, "Loading AI separation model...", "40 seconds remaining"),
                (12, 35, "Separating audio tracks...", "35 seconds remaining"),
                (20, 45, "Processing vocal tracks...", "30 seconds remaining"),
                (25, 55, "Processing instrumental tracks...", "25 seconds remaining"),
                (30, 65, "Applying audio filters...", "20 seconds remaining"),
                (35, 75, "Refining separated tracks...", "15 seconds remaining"),
                (40, 85, "Finalizing tracks...", "10 seconds remaining"),
                (50, 95, "Saving separated tracks...", "Almost done"),
            ]
            
            # Tạo QTimer để cập nhật tiến trình giả
            self.fake_progress_timer = QTimer()
            self.fake_progress_index = 0
            self.separation_is_complete = False
            
            def update_fake_progress():
                if self.fake_progress_index < len(self.fake_progress_steps):
                    seconds, progress, status, time_remaining = self.fake_progress_steps[self.fake_progress_index]
                    self.render_window.updateProgress(progress)
                    self.render_window.updateStatus(status)
                    self.render_window.updateTimeRemaining(time_remaining)
                    self.fake_progress_index += 1
                else:
                    # Hoàn thành các bước giả nhưng vẫn chờ tiến trình thật
                    self.fake_progress_timer.stop()
                    if not self.separation_is_complete:
                        self.render_window.updateStatus("Separating audio...")
                        self.render_window.updateTimeRemaining("please wait...")
            
            # Kết nối timer để cập nhật tiến trình
            self.fake_progress_timer.timeout.connect(update_fake_progress)
            self.fake_progress_timer.start(1000)  # Cập nhật mỗi giây
            
            # Start separation process (thực hiện ngầm)
            self.separator = start_separation(
                input_file=self.selected_file,
                output_dir=output_dir,
                stems=stems,
                high_quality=True
            )

            # Connect signals
            self.separator.error.connect(self.separation_error)
            
            # Connect real completion signal to override fake progress if completed early
            def real_completion_handler(output_path):
                self.separation_is_complete = True
                self.fake_progress_timer.stop()
                self.separation_complete(output_path)
            
            self.separator.finished.connect(real_completion_handler)

            # Connect cancel button to stop process
            self.render_window.cancel_button.clicked.disconnect()  # Disconnect default close
            self.render_window.cancel_button.clicked.connect(self.cancel_separation)

        except Exception as e:
            self.separation_error(str(e))

    def separation_complete(self, output_path):
        """Handle completion of separation"""
        if hasattr(self, 'render_window') and not self.render_window.isHidden():
            self.render_window.updateProgress(100)
            self.render_window.updateStatus("Separation complete!")
            self.render_window.updateTimeRemaining("Done!")
            QTimer.singleShot(1000, self.render_window.close)
        self.separation_is_complete = True
        
        # Switch to output view and update with new separation results
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            output_widget = main_window.page_mapping.get("OutputSeparate")
            
            if isinstance(output_widget, OutputSeparateWidget):
                output_widget.update_audio_files(output_path, self.selected_file)
            
            # Chuyển đến trang output
            if output_widget:
                main_window.stack.setCurrentWidget(output_widget)

    def separation_error(self, error_message):
        """Handle separation errors"""
        if hasattr(self, 'render_window'):
            self.render_window.close()
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", f"Separation failed: {error_message}")

    def cancel_separation(self):
        """Cancel the separation process"""
        if hasattr(self, 'fake_progress_timer') and self.fake_progress_timer.isActive():
            self.fake_progress_timer.stop()
        if hasattr(self, 'separator'):
            self.separator.terminate()
        if hasattr(self, 'render_window'):
            self.render_window.close()

    def on_file_dropped(self, file_path):
        # Store the file path from DropAreaLabel
        self.selected_file = os.path.abspath(file_path)  # Get absolute path
        print(f"Selected audio file: {self.selected_file}")

    def handle_stem_selection(self, button):
        self.selected_stems = int(button.text())
    
    def go_back(self):
        main_window = self.window()
        if main_window:
            stack = main_window.stack
            page_widget = main_window.page_mapping.get("MenuTool")
            if page_widget:
                stack.setCurrentWidget(page_widget)