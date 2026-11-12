from lastlight_voice import SpeechEngine

# Bundled offline Piper Amy voice is selected for English automatically.
speech = SpeechEngine(language="en")
speech.say("LastLight Voice is running offline.")
