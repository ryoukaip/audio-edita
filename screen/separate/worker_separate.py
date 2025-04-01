import subprocess
import os
import sys
from PyQt5.QtCore import QThread, pyqtSignal

class SpleeterSeparator(QThread):
    progress = pyqtSignal(str)  # Signal to emit progress updates
    finished = pyqtSignal(str)  # Signal when separation is complete
    error = pyqtSignal(str)     # Signal for errors

    def __init__(self, input_file, output_path, stems=2, high_quality=True):  # Mặc định high_quality=True
        super().__init__()
        self.input_file = ensure_unicode_path(input_file)
        self.output_path = ensure_unicode_path(output_path)
        self.stems = stems
        self.high_quality = high_quality

    def run(self):
        try:
            # Check ffmpeg installation with specific path
            ffmpeg_path = os.path.join(os.path.expanduser("~"), "scoop", "shims", "ffmpeg.exe")
            if not os.path.exists(ffmpeg_path):
                self.error.emit(f"FFmpeg not found at {ffmpeg_path}")
                return

            # Add ffmpeg to system PATH temporarily
            os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]

            # Verify input file exists
            if not os.path.exists(self.input_file):
                raise FileNotFoundError(f"Input file not found: {self.input_file}")

            # Create output directory if it doesn't exist
            os.makedirs(self.output_path, exist_ok=True)

            # Configure Spleeter command based on number of stems
            if self.stems == 2:
                stem_config = "spleeter:2stems"
            elif self.stems == 4:
                stem_config = "spleeter:4stems"
            elif self.stems == 5:
                stem_config = "spleeter:5stems"
            else:
                raise ValueError(f"Invalid number of stems: {self.stems}")

            self.progress.emit("Loading audio file")

            # Construct command as a list
            command = [
                sys.executable,
                "-m",
                "spleeter",
                "separate",
                self.input_file,
                "-p",
                stem_config,
                "-o",
                self.output_path
            ]

            # Always enable high quality (bitrate 320k)
            command.extend(["-b", "320k"])

            self.progress.emit(f"Running command: {' '.join(command)}")
            
            # Execute command with proper encoding
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            # Monitor process output
            while True:
                try:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.progress.emit(output.strip())
                        if "Loading tensorflow model" in output:
                            self.progress.emit("Loading AI separation model")
                except UnicodeDecodeError:
                    self.progress.emit("Could not decode some characters in output")

            # Check for errors
            if process.returncode != 0:
                try:
                    error = process.stderr.read()
                    self.error.emit(f"Separation failed: {error}")
                except UnicodeDecodeError:
                    self.error.emit("Separation failed with encoding issues in error message")
                return

            self.finished.emit(self.output_path)

        except Exception as e:
            self.error.emit(f"Error during separation: {str(e)}")

def ensure_unicode_path(path):
    """
    Ensure path is properly encoded in UTF-8
    """
    if isinstance(path, str):
        try:
            return os.path.normpath(path)
        except:
            return path.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    return path

def start_separation(input_file, output_dir, stems=2, high_quality=True):  # Mặc định high_quality=True
    """
    Start the audio separation process
    
    Args:
        input_file (str): Path to input audio file
        output_dir (str): Output directory path
        stems (int): Number of stems (2, 4, or 5)
        high_quality (bool): Use high quality mode (default: True)
    
    Returns:
        SpleeterSeparator: The separator thread instance
    """
    try:
        input_file = ensure_unicode_path(input_file)
        
        if not os.path.exists(input_file):
            raise FileNotFoundError("Input audio file not found")

        separator = SpleeterSeparator(input_file, output_dir, stems, high_quality)
        separator.start()
        return separator
    except Exception as e:
        raise Exception(f"Failed to start separation: {str(e)}")