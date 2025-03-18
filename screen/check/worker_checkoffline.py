import os
import numpy as np
import librosa
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool

# Hàm độc lập để trích xuất dấu vân tay
def extract_fingerprint(args):
    """Trích xuất dấu vân tay âm thanh từ file audio"""
    audio, sr, max_peaks_per_frame = args
    hop_length = 51  # Giảm từ 512 xuống 51 để tăng mật độ dữ liệu
    n_fft = 2048
    spec = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    spec_db = librosa.amplitude_to_db(np.abs(spec), ref=np.max)

    # Tìm các đỉnh trong spectrogram với giới hạn số đỉnh
    peaks = []
    for i in range(spec_db.shape[1]):  # Duyệt qua các khung thời gian
        freq_peaks = librosa.util.peak_pick(spec_db[:, i], pre_max=3, post_max=3, 
                                            pre_avg=3, post_avg=3, delta=5, wait=10)
        if len(freq_peaks) > max_peaks_per_frame:
            freq_peaks = freq_peaks[:max_peaks_per_frame]  # Giới hạn số đỉnh
        peaks.extend(freq_peaks)
    
    # Tạo dấu vân tay: danh sách các cặp (tần số, thời gian)
    fingerprints = []
    for i in range(len(peaks) - 1):
        freq1 = peaks[i]
        freq2 = peaks[i + 1]
        time_diff = (i + 1 - i) * hop_length / sr
        fingerprints.append((freq1, freq2, time_diff))
    
    return fingerprints

class CheckOfflineWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)  # Signal cho tiến trình
    finished = pyqtSignal(str)  # Signal khi hoàn thành (trả về chuỗi thay vì float)
    error = pyqtSignal(str)  # Signal khi có lỗi

    def __init__(self, input_file1, input_file2):
        super().__init__()
        self.input_file1 = input_file1
        self.input_file2 = input_file2

    def compare_fingerprints(self, fp1, fp2):
        """So sánh hai tập dấu vân tay và trả về kết quả tương đồng"""
        if not fp1 or not fp2:
            return "no similarity"

        matches = 0
        tolerance_freq = 5
        tolerance_time = 0.005  # Giảm từ 0.05 xuống 0.005

        for f1, f2, t1 in fp1:
            for g1, g2, t2 in fp2:
                if (abs(f1 - g1) <= tolerance_freq and 
                    abs(f2 - g2) <= tolerance_freq and 
                    abs(t1 - t2) <= tolerance_time):
                    matches += 1
                    break

        min_len = min(len(fp1), len(fp2))
        if min_len == 0:
            return "no similarity"

        # Tính tỷ lệ khớp
        similarity = matches / min_len * 100
        # Đặt ngưỡng tương đồng
        threshold = 99.99
        if similarity >= threshold:
            return "similarity"
        else:
            return "no similarity"

    def run(self):
        try:
            fake_progress_steps = [
                (20, "Loading audio files...", "3 seconds"),
                (40, "Extracting fingerprints...", "2 seconds"),
                (60, "Comparing fingerprints...", "2 seconds"),
                (80, "Calculating similarity...", "1 second"),
            ]

            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio1, sr1 = librosa.load(self.input_file1, sr=None)
            audio2, sr2 = librosa.load(self.input_file2, sr=None)
            self.progress_updated.emit(*fake_progress_steps[0])

            if sr1 != sr2:
                audio2 = librosa.resample(audio2, orig_sr=sr2, target_sr=sr1)
                sr2 = sr1

            # Song song hóa việc trích xuất dấu vân tay
            max_peaks_per_frame = 10  # Giới hạn số đỉnh mỗi khung
            args = [(audio1, sr1, max_peaks_per_frame), (audio2, sr2, max_peaks_per_frame)]
            self.progress_updated.emit(*fake_progress_steps[1])
            with Pool(processes=2) as pool:
                fp1, fp2 = pool.map(extract_fingerprint, args)

            self.progress_updated.emit(*fake_progress_steps[2])
            result = self.compare_fingerprints(fp1, fp2)

            self.progress_updated.emit(*fake_progress_steps[3])
            self.progress_updated.emit(100, "Comparison complete!", "Done!")
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))
