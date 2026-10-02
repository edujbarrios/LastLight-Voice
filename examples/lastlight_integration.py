from lastlight import LastLight
from lastlight_voice import SpeechEngine
from lastlight_voice.integrations import speak_query_result

knowledge = LastLight("lastlight-example-en.zip")
speech = SpeechEngine(language="en")

result = knowledge.query(
    "How long will food stay safe in my refrigerator if I keep the door closed?"
)
speak_query_result(result, speech)
