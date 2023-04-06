import pyttsx3
engine = pyttsx3.init()

text = "您好,这是试运行。hello, this is a test."
engine.say(text)
engine.say("I will speak this text")
engine.runAndWait()
