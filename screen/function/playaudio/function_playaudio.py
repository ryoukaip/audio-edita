from PyQt5.QtCore import Qt, QMimeData, QUrl, QTimer, pyqtSignal
from PyQt5.QtWidgets import (QLabel, QFileDialog)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QFont, QFontDatabase
from screen.function.playaudio.function_wavevisual import WaveformWidget
from screen.function.playaudio.function_playloading import LoadingSpinner, LoadingOverlay
from screen.function.playaudio.process_audio import AudioLoadWorker, format_time, is_audio_file
from screen.function.playaudio.process_video import VideoLoadWorker, is_video_file
from screen.function.playaudio.function_playui import setupUI, setup_drop_area_ui, setup_player_ui
import os

class DropAreaLabel(QLabel):
    file_dropped = pyqtSignal(str)
    time_updated = pyqtSignal(str)
    temp_file_updated = pyqtSignal(str)  # Thêm tín hiệu để báo temp_audio_file thay đổi

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(220)
        
        font_id = QFontDatabase.addApplicationFont("./fonts/Cabin-Bold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        
        self.player = QMediaPlayer()
        self.is_playing = False
        self.first_load = True
        self.temp_audio_file = None
        self.loading_worker = None  # Theo dõi worker hiện tại
        
        self.setupUI()
        
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setGeometry(self.rect())
        
        self.update_timer = QTimer()
        self.update_timer.setInterval(8)
        self.update_timer.timeout.connect(self.update_position)
        
        self.player.stateChanged.connect(self.on_state_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

    def setupUI(self):
        setupUI(self)

    def set_audio_file(self, file_path):
        # Dừng và hủy worker cũ nếu đang chạy
        if self.loading_worker and self.loading_worker.isRunning():
            self.loading_worker.terminate()
            self.loading_worker.wait()
        
        # Reset player an toàn
        self.player.stop()
        self.player.setMedia(QMediaContent())
        self.player.blockSignals(True)
        QTimer.singleShot(100, self._clear_temp_file)
        
        self.original_file_path = file_path
        self.seekbar.setEnabled(False)
        self.stacked_widget.setCurrentIndex(1)
        
        if self.first_load:
            self.loading_overlay.show_loading()
        
        if is_audio_file(file_path):
            self.loading_worker = AudioLoadWorker(file_path)
            self.loading_worker.finished.connect(self.on_audio_loaded)
            self.loading_worker.start()
        elif is_video_file(file_path):
            self.loading_worker = VideoLoadWorker(file_path)
            self.loading_worker.finished.connect(self.on_video_audio_loaded)
            self.loading_worker.start()
        else:
            print(f"Unsupported file format: {file_path}")
            self.loading_overlay.hide_loading()
            self.setText("Unsupported file format")
            return
        
        self.player.blockSignals(False)

    def _clear_temp_file(self):
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
                print(f"Deleted temp file: {self.temp_audio_file}")
            except Exception as e:
                print(f"Error deleting temp file: {e}")
            self.temp_audio_file = None

    def on_audio_loaded(self, file_path, data):
        print(f"on_audio_loaded: file_path={file_path}, data={data}")
        if data:
            waveform_data, sr = data
            self.waveform.set_waveform_data(waveform_data)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        if self.first_load:
            self.loading_overlay.hide_loading()
            self.first_load = False
        self.seekbar.setEnabled(True)
        self.file_dropped.emit(self.original_file_path)

    def on_video_audio_loaded(self, temp_audio_path, data, duration_ms):
        print(f"on_video_audio_loaded: temp_audio_path={temp_audio_path}, data={data}, duration_ms={duration_ms}")
        if temp_audio_path:
            self.temp_audio_file = temp_audio_path
            self.temp_file_updated.emit(temp_audio_path)  # Báo cho Video2AudioPage
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_audio_path)))
            if data:
                waveform_data, sr = data
                self.waveform.set_waveform_data(waveform_data)
            self.seekbar.setRange(0, duration_ms)
            self.total_time.setText(format_time(duration_ms))
        if self.first_load:
            self.loading_overlay.hide_loading()
            self.first_load = False
        self.seekbar.setEnabled(True)
        self.file_dropped.emit(self.original_file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(is_audio_file(url.toLocalFile()) or is_video_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if is_audio_file(file_path) or is_video_file(file_path):
                self.set_audio_file(file_path)
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._open_file_dialog()

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio or Video File",
            "",
            "Media Files (*.mp3 *.wav *.ogg *.m4a *.flac *.mp4 *.mkv *.mov *.flv *.avi)"
        )
        if file_path:
            self.set_audio_file(file_path)

    def toggle_playback(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.update_timer.stop()
        else:
            self.player.play()
            self.update_timer.start()

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.pause_icon)
            self.is_playing = True
            self.waveform.set_playing(True)
        else:
            self.play_btn.setIcon(self.play_icon)
            self.is_playing = False
            self.waveform.set_playing(False)

    def update_position(self):
        if not self.seekbar.isSliderDown():
            position = self.player.position()
            self.seekbar_animation.setStartValue(self.seekbar.value())
            self.seekbar_animation.setEndValue(position)
            self.seekbar_animation.start()
            duration = self.player.duration()
            if duration > 0:
                progress = (position / duration) * 100
                self.waveform.set_progress(progress)
            time_str = format_time(position)
            self.current_time.setText(time_str)
            self.time_updated.emit(time_str)

    def position_changed(self, position):
        if self.seekbar.isSliderDown():
            self.seekbar.setValue(position)
            duration = self.player.duration()
            if duration > 0:
                progress = (position / duration) * 100
                self.waveform.set_progress(progress)
            self.current_time.setText(format_time(position))

    def duration_changed(self, duration):
        if not self.temp_audio_file:  # Chỉ dùng duration từ QMediaPlayer cho audio
            print(f"QMediaPlayer duration: {duration} ms ({duration // 1000} seconds)")
            self.seekbar.setRange(0, duration)
            self.total_time.setText(format_time(duration))

    def seek_position(self, position):
        self.player.setPosition(position)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setGeometry(self.rect())
        
    def seek_relative(self, ms):
        new_position = self.player.position() + ms
        self.player.setPosition(new_position)

    def clear(self):
        self.player.stop()
        self.player.setMedia(QMediaContent())
        self.stacked_widget.setCurrentIndex(0)
        self.seekbar.setValue(0)
        self.current_time.setText("00:00")
        self.total_time.setText("00:00")
        self.waveform.clear_waveform()
        self._clear_temp_file()