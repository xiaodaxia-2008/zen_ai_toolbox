import sys
import time
import wave
import threading

import pyaudio
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                               QPushButton, QStatusBar, QTextEdit, QVBoxLayout,
                               QWidget, QComboBox)
from transformers import pipeline


class RecordingThread(QThread):
    """A QThread subclass for recording audio to a file."""
    # Declare signals for starting/stopping recording and updating the status message
    started_recording = Signal()
    stopped_recording = Signal()
    status_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False

    def run(self):
        # set parameters for recording
        RATE = 44100
        CHUNK = 1024

        # initialize PyAudio
        audio = pyaudio.PyAudio()

        # create stream object
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # create wave file object for saving the recording
        frames = []
        wf = wave.open('recording.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)

        # emit signal to update GUI status
        self.started_recording.emit()

        # recording loop
        while self.is_recording:
            data = stream.read(CHUNK)
            frames.append(data)
            wf.writeframes(data)

        # stop recording and close the stream and file objects
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wf.close()

        # emit signal to update GUI status
        self.stopped_recording.emit()

    def stop(self):
        self.is_recording = False


class RecorderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 400, 300)

        # initialize GUI elements
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.start_recording)
        hbox1.addWidget(self.record_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        hbox1.addWidget(self.stop_button)

        self.transcribe_button = QPushButton('Transcribe', self)
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        self.transcribe_button.setEnabled(False)
        hbox1.addWidget(self.transcribe_button)

        vbox.addLayout(hbox1)
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(['en', 'zh'])
        vbox.addWidget(self.lang_combo)

        self.text_editor = QTextEdit(self)
        vbox.addWidget(self.text_editor)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        central_widget.setLayout(vbox)
        self.nlp = {}
        threading.Thread(target=self._load_model).start()

    def start_recording(self):

        # initialize recording thread
        self.recording_thread = RecordingThread()

        # connect signals/slots between recording thread and GUI
        self.recording_thread.started_recording.connect(
            self.recording_started_handler)
        self.recording_thread.stopped_recording.connect(
            self.recording_stopped_handler)
        self.recording_thread.status_updated.connect(
            self.status_bar.showMessage)
        # update GUI state
        self.is_recording = True
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.transcribe_button.setEnabled(False)

        # start recording thread
        self.recording_thread.is_recording = True
        self.recording_thread.start()

    def stop_recording(self):
        # stop recording thread
        self.recording_thread.stop()

    def _load_model(self):
        # initialize transformer pipeline for speech-to-text
        if not self.nlp:
            print("Loading en model...")
            t1 = time.time()
            self.nlp["en"] = pipeline("automatic-speech-recognition",
                                      model="jonatasgrosman/wav2vec2-large-xlsr-53-english")
            print("en model loaded in", time.time() - t1, "seconds")
            print("Loading zh model...")
            t1 = time.time()
            self.nlp["zh"] = pipeline(
                "automatic-speech-recognition", model="wbbbbb/wav2vec2-large-chinese-zh-cn")
            print("zh model loaded in", time.time() - t1, "seconds")

    def transcribe_audio(self):
        # transcribe recorded audio to text using transformer pipeline
        self.status_bar.showMessage("Transcribing...")
        lang = self.lang_combo.currentText()
        while lang not in self.nlp:
            print("Waiting for model to load...")
            time.sleep(0.5)
        transcription = self.nlp[lang]('recording.wav')

        # update text editor with transcription
        # self.text_editor.clear()
        self.text_editor.append(transcription['text'])

        self.status_bar.showMessage("Transcription done.")

    def recording_started_handler(self):
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.transcribe_button.setEnabled(False)
        self.status_bar.showMessage("Recording...")

    def recording_stopped_handler(self):
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(True)
        self.status_bar.showMessage("Ready")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = RecorderGUI()
    gui.show()
    sys.exit(app.exec())
