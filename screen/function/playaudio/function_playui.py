from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QSlider, QStackedWidget, QSizePolicy)
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from screen.function.playaudio.function_wavevisual import WaveformWidget

def setupUI(drop_area_label):
    # Create stacked widget
    drop_area_label.stacked_widget = QStackedWidget(drop_area_label)
    
    # Create and setup both UI states
    setup_drop_area_ui(drop_area_label)
    setup_player_ui(drop_area_label)
    
    # Main layout
    main_layout = QVBoxLayout(drop_area_label)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(drop_area_label.stacked_widget)

def setup_drop_area_ui(drop_area_label):
    # Drop area widget
    drop_widget = QWidget()
    drop_widget.setStyleSheet("""
        QWidget {
            background-color: #7d8bd4;
            border: 3px solid #FBFFE4;
            border-radius: 25px;
        }
    """)
    
    # Drop area label
    drop_label = QLabel("click to select file or drop a file here")
    drop_label.setFont(QFont(drop_area_label.font_family, 12))
    drop_label.setStyleSheet("color: white; border: none;")
    drop_label.setAlignment(Qt.AlignCenter)
    
    # Layout
    drop_layout = QVBoxLayout(drop_widget)
    drop_layout.addWidget(drop_label)
    
    drop_area_label.stacked_widget.addWidget(drop_widget)

def setup_player_ui(drop_area_label):
    # Player widget
    player_widget = QWidget()
    player_layout = QVBoxLayout(player_widget)
    player_layout.setContentsMargins(0, 0, 0, 0)
    player_layout.setSpacing(0)

    # Upper section (seekbar)
    upper_widget = QWidget()
    upper_widget.setFixedHeight(220)
    upper_widget.setStyleSheet("""
        QWidget {
            background-color: #7d8bd4;
            border-radius: 25px;
        }
    """)
    upper_layout = QVBoxLayout(upper_widget)
    upper_layout.setContentsMargins(0, 0, 0, 0)
    upper_layout.setAlignment(Qt.AlignTop)
    upper_layout.setSpacing(0)

    # Tạo container cho seekbar và waveform
    seekbar_container = QWidget()
    seekbar_container.setFixedHeight(190)
    seekbar_layout = QVBoxLayout(seekbar_container)
    seekbar_layout.setContentsMargins(0, 0, 0, 0)
    seekbar_layout.setSpacing(0)

    # Create seekbar as background
    drop_area_label.seekbar = QSlider(Qt.Horizontal)
    drop_area_label.seekbar.setFixedHeight(190)
    drop_area_label.seekbar.setStyleSheet("""
        QSlider {
            background: transparent;
            margin: 0px;
            padding: 0px;
            border-top: none;
        }
        QSlider::groove:horizontal {
            height: 190px;
            background: #474f7a;
            border-radius: 25px;
            margin: 0px;
        }
        QSlider::handle:horizontal {
            width: 0px;
            height: 0px;
        }
        QSlider::sub-page:horizontal {
            height: 190px;
            background: #98a4e6;
            border-radius: 25px;
            margin: 0px;
        }
    """)
    drop_area_label.seekbar.sliderMoved.connect(drop_area_label.seek_position)
    drop_area_label.seekbar.setEnabled(False)

    # Tạo waveform widget
    drop_area_label.waveform = WaveformWidget(drop_area_label.seekbar)
    drop_area_label.waveform.setFixedHeight(190)
    drop_area_label.waveform.setGeometry(drop_area_label.seekbar.geometry())

    # Add animation
    drop_area_label.seekbar_animation = QPropertyAnimation(drop_area_label.seekbar, b"value")
    drop_area_label.seekbar_animation.setEasingCurve(QEasingCurve.Linear)
    drop_area_label.seekbar_animation.setDuration(8)
    
    # Thêm vào layout
    seekbar_layout.addWidget(drop_area_label.seekbar)
    upper_layout.addWidget(seekbar_container)

    # Lower section (controls)
    lower_widget = QWidget()
    lower_widget.setFixedHeight(30)
    lower_widget.setStyleSheet("""
        QWidget {
            background-color: none;
            margin: 0px;
        }
    """)
    lower_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    lower_layout = QHBoxLayout(lower_widget)
    lower_layout.setContentsMargins(20, 0, 20, 0)
    lower_layout.setSpacing(0)
    lower_layout.setAlignment(Qt.AlignVCenter)

    # Create play button with icon
    drop_area_label.back_btn = QPushButton()
    drop_area_label.back_btn.setFixedSize(30, 30)
    drop_area_label.back_btn.setIcon(QIcon("./icon/arrow-back.png"))
    drop_area_label.back_btn.clicked.connect(lambda: drop_area_label.seek_relative(-5000))

    drop_area_label.play_btn = QPushButton()
    drop_area_label.play_btn.setFixedSize(20, 20)
    drop_area_label.play_icon = QIcon("./icon/play.png")
    drop_area_label.pause_icon = QIcon("./icon/pause.png")
    drop_area_label.play_btn.setIcon(drop_area_label.play_icon)
    drop_area_label.play_btn.clicked.connect(drop_area_label.toggle_playback)

    drop_area_label.forward_btn = QPushButton()
    drop_area_label.forward_btn.setFixedSize(30, 30)
    drop_area_label.forward_btn.setIcon(QIcon("./icon/arrow-forward.png"))
    drop_area_label.forward_btn.clicked.connect(lambda: drop_area_label.seek_relative(5000))

    # Create time labels
    drop_area_label.current_time = QLabel("00:00")
    drop_area_label.total_time = QLabel("00:00")
    for label in [drop_area_label.current_time, drop_area_label.total_time]:
        label.setStyleSheet("color: white; border: none;")
        label.setFont(QFont(drop_area_label.font_family, 10))
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(50)

    # Add elements to lower section
    lower_layout.addWidget(drop_area_label.current_time)
    lower_layout.addStretch()
    lower_layout.addWidget(drop_area_label.back_btn)
    lower_layout.addWidget(drop_area_label.play_btn)
    lower_layout.addWidget(drop_area_label.forward_btn)
    lower_layout.addStretch()
    lower_layout.addWidget(drop_area_label.total_time)

    # Add both sections to main player layout
    player_layout.addWidget(upper_widget)
    player_layout.addWidget(lower_widget)

    drop_area_label.stacked_widget.addWidget(player_widget)