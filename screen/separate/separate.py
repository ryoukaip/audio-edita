import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QButtonGroup, QStackedWidget, QApplication
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QFont, QFontDatabase
from screen.function.mainscreen.function_functionbar import FunctionBar
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.function_separate import start_separation
from screen.function.system.function_renderwindow import RenderWindow
from screen.function.output.output_separate import OutputSeparateWidget

class SeparatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_file = None
        self.selected_stems = 2  # Default value
    
    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

        # Create main widget to hold everything
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 15, 25, 25)

        # Content layout (everything except Export button)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        top_bar = FunctionBar("vocal separation", font_family, self)
        main_layout.addLayout(top_bar)
        main_layout.addSpacing(10)

        # Create container for drop area and columns with fixed spacing
        drop_columns_container = QWidget()
        drop_columns_layout = QVBoxLayout(drop_columns_container)
        drop_columns_layout.setContentsMargins(0, 0, 0, 0)
        drop_columns_layout.setSpacing(20)

        self.drop_area = DropAreaLabel()
        self.drop_area.file_dropped.connect(self.handle_file_dropped)

        # Create container for both columns
        columns_container = QWidget()
        columns_container.setFixedWidth(600)
        columns_layout = QHBoxLayout(columns_container)
        columns_layout.setContentsMargins(0, 10, 0, 0)

        # Left column container
        left_container = QWidget()
        left_column = QVBoxLayout(left_container)
        left_column.setSpacing(20)
        left_column.setContentsMargins(50, 0, 25, 0)

        # Right column container
        right_container = QWidget()
        right_column = QVBoxLayout(right_container)
        right_column.setSpacing(20)
        right_column.setContentsMargins(25, 0, 50, 0)

        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)  # Change this line
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.handle_stem_selection)

        # Left column content - number buttons
        options = [
            ("vocal + melody", "2"),
            ("vocal + 3 instrument", "4"),
            ("vocal + 4 instrument", "5")
        ]
        
        for text, number in options:
            option_row = QHBoxLayout()
            option_row.setSpacing(15)
            
            # Create number button
            btn = QPushButton(number)
            btn.setFixedSize(54, 50)
            btn.setFont(QFont(font_family, 16))
            btn.setCheckable(True)
            self.button_group.addButton(btn)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #323754;
                    border-radius: 15px;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #7d8bd4;
                }
            """)
            
            label = QLabel(text)
            label.setFont(QFont(font_family, 13))
            label.setStyleSheet("color: white;")
            
            option_row.addWidget(btn)
            option_row.addWidget(label)
            option_row.addStretch()
            
            left_column.addLayout(option_row)

        # Right column content - checkboxes
        checkbox_options = ["recombine", "high quality", "quick export"]
        
        for text in checkbox_options:
            checkbox_row = QHBoxLayout()
            checkbox_row.setSpacing(20)
            
            checkbox = QPushButton()
            checkbox.setFixedSize(30, 30)
            checkbox.setCheckable(True)
            checkbox.setStyleSheet("""
                QPushButton {
                    background-color: #323754;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:checked {
                    background-color: #323754;
                    border: none;
                    border-radius: 15px;
                    image: url(./icon/dot.png);  
                }
            """)
            
            label = QLabel(text)
            label.setFont(QFont(font_family, 13))
            label.setStyleSheet("color: white;")
            
            checkbox_row.addWidget(checkbox)
            checkbox_row.addWidget(label)
            checkbox_row.addStretch()
            
            right_column.addLayout(checkbox_row)

        # Add columns to container
        columns_layout.addWidget(left_container)
        columns_layout.addWidget(right_container)
        
        # Add widgets to drop_columns_container with fixed spacing
        drop_columns_layout.addWidget(self.drop_area)
        drop_columns_layout.addWidget(columns_container, 0, Qt.AlignCenter)
        drop_columns_layout.addStretch()

        # Add drop_columns_container to content layout
        content_layout.addWidget(drop_columns_container)
        
        # Create export button
        export_btn = QPushButton("Export")
        export_btn.setFixedSize(100, 40)
        export_btn.setFont(QFont(font_family, 13))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4062;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #474f7a;
            }
        """)
        export_btn.clicked.connect(self.show_output_widget)
        
        # Add content and export button to main layout
        main_layout.addLayout(content_layout)
        main_layout.addWidget(export_btn, 0, Qt.AlignRight | Qt.AlignBottom)

        # Set the main widget as the central widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_widget)
        self.setLayout(layout)

        first_button = self.button_group.buttons()[0]
        first_button.setChecked(True)

    def show_output_widget(self):
        if not self.selected_file:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Please select an audio file first")
            return

        try:
            # Create and show render window
            self.render_window = RenderWindow(None)  # Không có parent để hiển thị trong cửa sổ mới
            self.render_window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            
            # Căn giữa cửa sổ trên màn hình
            from PyQt5.QtWidgets import QApplication
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
                    # Đổi thành cập nhật ít thường xuyên hơn nếu vẫn đang chờ
                    if not self.separation_is_complete:
                        self.render_window.updateStatus("Separating audio...")
                        self.render_window.updateTimeRemaining("please wait...")
                        # Không đóng cửa sổ, chờ tín hiệu hoàn tất từ tiến trình thật
            
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

            # Connect signals (vẫn giữ kết nối này để xử lý lỗi)
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
            # Close render window after 1 second
            QTimer.singleShot(1000, self.render_window.close)

        # Đánh dấu là đã hoàn thành
        self.separation_is_complete = True
        
        # Switch to output view and update with new separation results
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            # Lấy widget output (giả sử nó ở index 15)
            output_widget = main_window.stack.widget(15)
            
            # Kiểm tra nếu là OutputSeparateWidget
            if isinstance(output_widget, OutputSeparateWidget):
                # Cập nhật thông tin cho widget
                output_widget.update_audio_files(output_path, self.selected_file)
            
            # Chuyển đến trang output
            main_window.stack.setCurrentIndex(15)

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

    def handle_file_dropped(self, file_path):
        # Store the file path from DropAreaLabel
        self.selected_file = os.path.abspath(file_path)  # Get absolute path
        print(f"Selected audio file: {self.selected_file}")

    def handle_stem_selection(self, button):
        self.selected_stems = int(button.text())
    
    def go_back(self):
        main_window = self.window()
        if main_window and hasattr(main_window, 'stack'):
            stack = main_window.stack
            stack.setCurrentIndex(1)
