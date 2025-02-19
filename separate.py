from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase
from function.function_playaudio import DropAreaLabel

class SeparatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_file = None
    
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

        self.drop_area = DropAreaLabel()
        self.drop_area.file_dropped.connect(self.handle_file_dropped)

        # Create options layout
        options_layout = QHBoxLayout()  # Change to horizontal to create two columns
        
        # Left column - number buttons
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        left_column.setContentsMargins(50, 0, 25, 0)

        # Right column - checkboxes
        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        right_column.setContentsMargins(25, 0, 50, 0)
        
        # Create button group for exclusive selection
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

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
            button_group.addButton(btn)
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
            btn.setCheckable(True)
            
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

        # Add both columns to options layout
        options_layout.addLayout(left_column)
        options_layout.addLayout(right_column)
        
        content_layout.addWidget(self.drop_area)
        content_layout.addSpacing(20)
        content_layout.addLayout(options_layout)
        
        # Create export button
        export_btn = QPushButton("Export")
        export_btn.setFixedSize(100, 40)
        export_btn.setFont(QFont(font_family, 13))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #474f7a;
                border-radius: 12px;
                color: white;
            }
            QPushButton:pressed {
                background-color: #7d8bd4;
            }
        """)
        
        # Add content and export button to main layout
        main_layout.addLayout(content_layout)
        main_layout.addWidget(export_btn, 0, Qt.AlignRight | Qt.AlignBottom)

        # Set the main widget as the central widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_widget)
        self.setLayout(layout)

    def handle_file_dropped(self, file_path):
        self.selected_file = file_path
        # Here you can add additional logic to handle the selected file
        print(f"Selected audio file: {file_path}")