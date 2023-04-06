import os

import openai
from dotenv import load_dotenv
from IPython import embed

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
audio_file = open("./audios/recording.wav", "rb")

transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")

print(transcript["text"])

embed()

