import tkinter as tk
import pyaudio
import wave
import threading

class RecorderGUI:
    def __init__(self, master):
        # initialize GUI elements
        self.master = master
        master.title("Audio Recorder")

        self.record_button = tk.Button(master, text="Record", command=self.start_recording)
        self.record_button.pack()

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_recording)
        self.stop_button.pack()
        self.stop_button.config(state='disabled')  # disable Stop button at start

        self.transcribe_button = tk.Button(master, text="Transcribe", command=self.transcribe_audio)
        self.transcribe_button.pack()
        self.transcribe_button.config(state='disabled')  # disable Transcribe button until recording is done

        self.text_editor = tk.Text(master)
        self.text_editor.pack()

        self.quit_button = tk.Button(master, text="Quit", command=self.quit)
        self.quit_button.pack()

        # initialize PyAudio
        self.is_recording = False

        self.nlp = None

    def start_recording(self):
        # set parameters for recording
        RATE = 44100
        CHUNK = 1024

        self.audio = pyaudio.PyAudio()
        # create stream object
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                       channels=1,
                                       rate=RATE,
                                       input=True,
                                       frames_per_buffer=CHUNK)

        # create wave file object for saving the recording
        self.frames = []
        self.wf = wave.open("recording.wav", "wb")
        self.wf.setnchannels(1)
        self.wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        self.wf.setframerate(RATE)

        # update GUI state
        self.is_recording = True
        self.record_button.config(state='disabled')
        self.stop_button.config(state='normal')

        # start recording in a new thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

    def record_audio(self):
        # recording loop
        CHUNK = 1024
        while self.is_recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)
            self.wf.writeframes(data)
        
        # stop recording and close the stream and file objects
        print("Done recording!")
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.wf.close()

        # update GUI state
        self.record_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.transcribe_button.config(state='normal')

    def stop_recording(self):
        self.is_recording = False

    def transcribe_audio(self):
        if not self.nlp:
            # initialize transformer pipeline for speech-to-text
            # self.nlp = pipeline("speech2text", model="facebook/wav2vec2-large-960h-lv60-self")
            self.nlp = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")
        # transcribe recorded audio to text using transformer pipeline
        print("Transcribing...")
        self.transcription = self.nlp("recording.wav")

        # update text editor with transcription
        self.text_editor.delete("1.0", tk.END)
        # for sentence in self.transcription:
        #     self.text_editor.insert(tk.END, sentence['text'] + '\n')
        self.text_editor.insert(tk.END, self.transcription['text'] + '\n')
        
        print("Transcription done.")
        
    def quit(self):
        self.is_recording = False
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    gui = RecorderGUI(root)
    root.mainloop()
