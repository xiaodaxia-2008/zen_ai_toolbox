# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

# <code>
import os
import time
from dotenv import load_dotenv

import azure.cognitiveservices.speech as speechsdk

load_dotenv()

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

audio_config = speechsdk.audio.AudioConfig(filename="./audios/recording.wav")
# audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "zh-CN"

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_config)

print("Say something...")


# Starts speech recognition, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of 15
# seconds of audio is processed.  The task returns the recognition text as result.
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query.
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.
result = speech_recognizer.recognize_once()
# result = speech_recognizer.start_continuous_recognition()
# connect to EventSignal to receive recognition results
# result.connect(lambda evt: print(evt.result.text))
# result.connect(lambda evt: print(evt))

# while True:
#     time.sleep(1)

# Checks result.
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
# </code>
