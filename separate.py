import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QButtonGroup, QStackedWidget
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont, QFontDatabase
from screen.function.playaudio.function_playaudio import DropAreaLabel
from screen.function.separate.function_separate import SpleeterSeparator, start_separation


class SeparatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_file = None
        self.selected_stems = 2  # Default value
    
    def initUI(self):
        # Create main widget to hold everything
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Content layout (everything except Export button)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.setFont(QFont(font_family))

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

    def show_output_widget(self):
        if not self.selected_file:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Please select an audio file first")
            return

        try:
            # Get selected stems
            stems = self.selected_stems
            
            # Create output directory in Documents folder
            documents_path = os.path.expanduser("~\\Documents\\audio-edita")
            output_dir = os.path.join(documents_path, "separate")
            os.makedirs(output_dir, exist_ok=True)

            # Start separation with proper path handling
            self.separator = start_separation(
                input_file=self.selected_file,
                output_dir=output_dir,
                stems=stems,
                high_quality=True  # You can make this configurable
            )

            # Connect signals
            self.separator.progress.connect(self.update_progress)
            self.separator.finished.connect(self.separation_complete)
            self.separator.error.connect(self.separation_error)

        except Exception as e:
            self.separation_error(str(e))

    def update_progress(self, message):
        """Handle progress updates from separator"""
        print(f"Progress: {message}")
        # Add progress bar or label update here

    def separation_complete(self, output_path):
        """Handle completion of separation"""
        print(f"Separation complete. Output at: {output_path}")
        main_window = self.window()
        main_window.stack.setCurrentIndex(15)  # Switch to output view

    def separation_error(self, error_message):
        """Handle separation errors"""
        print(f"Error: {error_message}")
        # Show error message to user

    def handle_file_dropped(self, file_path):
        # Store the file path from DropAreaLabel
        self.selected_file = os.path.abspath(file_path)  # Get absolute path
        print(f"Selected audio file: {self.selected_file}")

    def handle_stem_selection(self, button):
        self.selected_stems = int(button.text())