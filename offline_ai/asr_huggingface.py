from transformers import pipeline
import time


print("Loading model...")
t1 = time.time()
# pipe = pipeline("automatic-speech-recognition",
#                  model="jonatasgrosman/wav2vec2-large-xlsr-53-english")
pipe = pipeline("automatic-speech-recognition", model="xmzhu/whisper-tiny-zh")
print("Model loaded in", time.time() - t1, "seconds")

fname = "./recording.wav"
res = pipe(fname)
print(res)
