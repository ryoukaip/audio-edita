import sys
import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QSlider
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap


class WaveformThread(QThread):
    waveform_generated = pyqtSignal(str)  # Signal to send the generated waveform image path

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        # Load audio file and generate waveform
        y, sr = librosa.load(self.filepath, sr=None)
        waveform = np.abs(y)

        # Plot waveform
        plt.figure(figsize=(8, 3))
        plt.plot(waveform, color="blue")
        plt.axis("off")
        plt.tight_layout()

        # Save the plot as an image
        output_path = "waveform.png"
        plt.savefig(output_path)
        plt.close()

        # Emit the signal with the image path
        self.waveform_generated.emit(output_path)

class AudioPlayer(QWidget):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.init_ui()
        self.audio_data, self.sr = librosa.load(filepath, sr=None)  # Load audio
        self.audio_stream = None
        self.is_playing = False
        self.current_sample = 0  # Keep track of the current audio sample
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slider)

    def init_ui(self):
        self.setWindowTitle("Audio Player")
        self.setGeometry(150, 150, 500, 150)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.seek_audio)

        layout = QVBoxLayout()
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def toggle_play(self):
        if self.is_playing:
            self.pause_audio()
        else:
            self.play_audio()

    def play_audio(self):
        if not self.audio_stream:
            self.audio_stream = sd.OutputStream(
                samplerate=self.sr, channels=1, callback=self.audio_callback
            )
            self.audio_stream.start()
        self.is_playing = True
        self.play_button.setText("Pause")
        self.timer.start(100)  # Update slider every 100 ms

    def pause_audio(self):
        self.is_playing = False
        self.play_button.setText("Play")
        self.timer.stop()

    # def seek_audio(self, value):
    #     if self.audio_stream:
    #         self.audio_stream.stop()
    #     self.current_sample = int(value / 100 * len(self.audio_data))
    #     self.audio_stream.start()
    def seek_audio(self, value):
        # Calculate the new sample index based on the slider value
        self.current_sample = int(value / 100 * len(self.audio_data))

        # Ensure the audio stream is running
        if self.audio_stream and not self.audio_stream.active:
            self.audio_stream.start()

        # Reset the playback position by updating the current sample directly
        self.timer.start(100)  # Continue updating the slider


    def update_slider(self):
        position = (self.current_sample / len(self.audio_data)) * 100
        self.slider.setValue(int(position))

    def audio_callback(self, outdata, frames, time, status):
        if not self.is_playing:
            outdata[:] = np.zeros((frames, 1))
            return
        start = self.current_sample
        end = min(len(self.audio_data), start + frames)
        outdata[: end - start] = self.audio_data[start:end].reshape(-1, 1)
        self.current_sample += frames
        if self.current_sample >= len(self.audio_data):
            self.is_playing = False
            self.timer.stop()

    def closeEvent(self, event):
        # Stop audio playback when the window is closed
        if self.audio_stream and self.audio_stream.active:
            self.audio_stream.stop()
        event.accept()


class AudioEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Audio Editor")
        self.setGeometry(100, 100, 800, 600)

        # Button for selecting a file
        self.select_file_button = QPushButton("Select Audio File", self)
        self.select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.select_file_button.clicked.connect(self.open_file_dialog)

        # Label to display the waveform
        self.waveform_label = QLabel("Drop an audio file here or use the button above", self)
        self.waveform_label.setAlignment(Qt.AlignCenter)
        self.waveform_label.setStyleSheet("border: 2px dashed #aaa;")
        self.waveform_label.setAcceptDrops(True)

        # Button to open the player
        self.player_button = QPushButton("Play Audio", self)
        self.player_button.setEnabled(False)
        self.player_button.clicked.connect(self.open_player)

        # Layouts
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.select_file_button, alignment=Qt.AlignLeft)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.waveform_label)
        main_layout.addWidget(self.player_button)

        self.setLayout(main_layout)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.endswith((".wav", ".mp3")):
                self.filepath = filepath
                self.start_waveform_generation(filepath)
            else:
                self.waveform_label.setText("Invalid file type!")

    def open_file_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3)")
        if filepath:
            self.filepath = filepath
            self.start_waveform_generation(filepath)

    def start_waveform_generation(self, filepath):
        self.waveform_label.setText("Loading waveform...")
        self.thread = WaveformThread(filepath)
        self.thread.waveform_generated.connect(self.display_waveform)
        self.thread.start()

    def display_waveform(self, image_path):
        pixmap = QPixmap(image_path)
        self.waveform_label.setPixmap(pixmap)
        self.player_button.setEnabled(True)  # Enable the play button after generating the waveform

    def open_player(self):
        self.player_window = AudioPlayer(self.filepath)
        self.player_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = AudioEditor()
    editor.show()
    sys.exit(app.exec_())
