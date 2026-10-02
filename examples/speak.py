from lastlight_voice import SpeechEngine

# Uses eSpeak NG when it is installed locally. No network access is performed.
speech = SpeechEngine(language="en")
speech.say("LastLight Voice is running offline.")
