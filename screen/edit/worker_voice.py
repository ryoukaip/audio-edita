import os
import librosa
import soundfile as sf
import numpy as np
import pyworld as pw
from PyQt5.QtCore import QThread, pyqtSignal
from pydub import AudioSegment  # Thêm import pydub

class VoiceWorker(QThread):
    progress_updated = pyqtSignal(int, str, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_file, voice_type, pitch_shift=0, formant_shift=0):
        super().__init__()
        self.input_file = input_file
        self.voice_type = voice_type
        self.pitch_shift = pitch_shift
        self.formant_shift = formant_shift

    def run(self):
        try:
            fake_progress_steps = [
                (15, "Loading audio...", "6 seconds"),
                (30, "Analyzing voice with WORLD...", "5 seconds"),
                (45, "Extracting pitch and formants...", "4 seconds"),
                (60, "Modifying voice parameters...", "3 seconds"),
                (75, "Synthesizing new voice...", "2 seconds"),
                (90, "Saving file...", "1 second"),
            ]

            self.progress_updated.emit(0, "Preparing audio...", "Calculating...")
            audio, sr = librosa.load(self.input_file, sr=None)
            audio = audio.astype(np.float64)

            self.progress_updated.emit(fake_progress_steps[0][0], fake_progress_steps[0][1], fake_progress_steps[0][2])
            f0, sp, ap = pw.wav2world(audio, sr)

            self.progress_updated.emit(fake_progress_steps[1][0], fake_progress_steps[1][1], fake_progress_steps[1][2])
            modified_f0 = f0.copy()
            modified_sp = sp.copy()
            pitch_factor = 2 ** (self.pitch_shift / 12.0)
            formant_factor = 1.0 + (self.formant_shift / 10.0)

            if self.voice_type == "Female":
                modified_f0 *= pitch_factor * 2.0
                if formant_factor != 1.0:
                    freq_axis = np.linspace(0, sr/2, sp.shape[1])
                    new_freq_axis = freq_axis * formant_factor
                    modified_sp = np.zeros_like(sp)
                    for i in range(len(sp)):
                        modified_sp[i] = np.interp(freq_axis, new_freq_axis, sp[i])
                modified_sp *= np.linspace(1.0, 1.2, sp.shape[1])

            elif self.voice_type == "Male":
                modified_f0 *= pitch_factor * 0.5
                if formant_factor != 1.0:
                    freq_axis = np.linspace(0, sr/2, sp.shape[1])
                    new_freq_axis = freq_axis * formant_factor
                    modified_sp = np.zeros_like(sp)
                    for i in range(len(sp)):
                        modified_sp[i] = np.interp(freq_axis, new_freq_axis, sp[i])

            elif self.voice_type == "Child":
                modified_f0 *= pitch_factor * 2.5
                formant_factor += 0.4
                freq_axis = np.linspace(0, sr/2, sp.shape[1])
                new_freq_axis = freq_axis * formant_factor
                modified_sp = np.zeros_like(sp)
                for i in range(len(sp)):
                    modified_sp[i] = np.interp(freq_axis, new_freq_axis, sp[i])

            elif self.voice_type == "Elderly":
                modified_f0 *= pitch_factor * 0.9
                t = np.arange(len(f0)) / sr
                tremolo = 1 + 0.15 * np.sin(2 * np.pi * 6 * t)
                modified_f0 *= tremolo

            elif self.voice_type == "Robot":
                modified_f0 = np.where(modified_f0 > 0, 100, 0)
                modified_sp *= 0.8

            self.progress_updated.emit(fake_progress_steps[2][0], fake_progress_steps[2][1], fake_progress_steps[2][2])
            modified_audio = pw.synthesize(modified_f0, modified_sp, ap, sr, frame_period=pw.default_frame_period)

            self.progress_updated.emit(fake_progress_steps[3][0], fake_progress_steps[3][1], fake_progress_steps[3][2])
            if np.max(np.abs(modified_audio)) > 1.0:
                modified_audio = modified_audio * 0.95 / np.max(np.abs(modified_audio))

            self.progress_updated.emit(fake_progress_steps[4][0], fake_progress_steps[4][1], fake_progress_steps[4][2])
            output_dir = os.path.join(os.path.expanduser("~"), "Documents", "audio-edita", "edit", "voice-changer")
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(self.input_file))[0]
            temp_wav_file = os.path.join(output_dir, f"{filename}_{self.voice_type}_voice_temp.wav")
            output_file = os.path.join(output_dir, f"{filename}_{self.voice_type}_voice.mp3")

            # Lưu file WAV tạm thời
            sf.write(temp_wav_file, modified_audio, sr, subtype='PCM_24')

            # Chuyển đổi sang MP3 bằng pydub
            audio_segment = AudioSegment.from_wav(temp_wav_file)
            audio_segment.export(output_file, format="mp3", bitrate="192k")  # Bitrate 192k cho chất lượng tốt, nhẹ file

            # Xóa file WAV tạm thời
            os.remove(temp_wav_file)

            self.progress_updated.emit(100, "Export complete!", "Done!")
            self.finished.emit(output_file)

        except Exception as e:
            import traceback
            self.error.emit(f"Error during processing: {str(e)}\nDetails: {traceback.format_exc()}")