import os
import librosa  
import soundfile as sf
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class MergeWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_file1, input_file2):
        super().__init__()
        self.input_file1 = input_file1
        self.input_file2 = input_file2

    def run(self):
        try:
            fake_progress_steps = [
                (20, "Loading first audio...", "2 seconds"),
                (40, "Loading second audio...", "2 seconds"),
                (60, "Merging audio...", "2 seconds"),
                (80, "Saving file...", "1 second"),
            ]

            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio1, sr1 = librosa.load(self.input_file1, sr=None)
            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])

            audio2, sr2 = librosa.load(self.input_file2, sr=None)
            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])

            if sr1 != sr2:
                audio2 = librosa.resample(audio2, orig_sr=sr2, target_sr=sr1)

            merged_audio = np.concatenate((audio1, audio2))
            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])

            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "merge")
            os.makedirs(output_dir, exist_ok=True)
            filename1 = os.path.splitext(os.path.basename(self.input_file1))[0]
            filename2 = os.path.splitext(os.path.basename(self.input_file2))[0]
            output_file = os.path.join(output_dir, f"{filename1}_merged_{filename2}.wav")
            sf.write(output_file, merged_audio, sr1)

            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])

            self.progress_updated.emit(100, "Merge complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            self.error.emit(str(e))
