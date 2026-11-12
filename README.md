# LastLight-Voice

**Offline speech recognition and text-to-speech.** Listen, transcribe and respond aloud with no cloud API.

## Features

- **English STT:** bundled Vosk small model; microphone input.
- **English TTS:** bundled Piper Amy voice; speaks directly through speakers.
- **Spanish TTS:** eSpeak NG, if installed on the system.
- **Voice interaction:** transcribe a message and answer “Hello, I have received your message.”
- **Extensible:** interchangeable voices and response callbacks, ready for optional [LastLight](https://github.com/edujbarrios/lastlight) knowledge retrieval.

## Install

```bash
git clone https://github.com/edujbarrios/LastLight-Voice.git
cd LastLight-Voice
python -m pip install -e .
```

Piper, Vosk and the English voice/STT models are included. After installation,
speech processing works **offline**. A working microphone and speakers are
required for interaction; Linux may also require the system `libportaudio2` package.

## Text to audio — basic example

```python
from lastlight_voice import SpeechEngine

voice = SpeechEngine(language="en")  # Bundled offline Piper Amy
voice.say("Hello from LastLight!")    # Play through your speakers

audio = voice.synthesize("Hello from LastLight!")  # AudioBuffer (WAV)
audio.save("hello.wav")               # Optional: save the WAV file
# audio.data contains the WAV bytes for use in your Python application
```

Without speakers, generate a WAV directly with `python examples/tts_basic.py`.
`say()` plays audio and returns `None`; `synthesize()` returns the audio in memory.

## Talk

```bash
lastlight-voice interact
```

Speak in English. The library transcribes your message and replies aloud,
without saving audio files. Use `lastlight-voice interact --seconds 15` for a
longer listening window.

```python
from lastlight_voice import VoiceInteraction

VoiceInteraction().interact_once()
```

## Prepared for LastLight

The optional adapter uses only the original LastLight public
`LastLight.query()` contract: it speaks an **accepted passage**, or a
deterministic refusal if the query is rejected. No LastLight dependency is
required for normal voice interaction.

```python
from lastlight import LastLight  # Optional, installed separately
from lastlight_voice import VoiceInteraction
from lastlight_voice.integrations import make_lastlight_responder

knowledge = LastLight("my-knowledge-pack.zip")
VoiceInteraction(responder=make_lastlight_responder(knowledge)).interact_once()
```

[Adapter example](examples/lastlight_integration.py) ·
[Integration guide](docs/lastlight_integration.md) ·
[Architecture](docs/architecture.md)

## Licenses

Code: **MPL-2.0** · Piper runtime: **GPL-3.0-or-later** · Vosk:
**Apache-2.0**. The Piper Amy weight redistribution rights require separate
review before publishing to PyPI.

[Voice attribution](THIRD_PARTY_VOICES.md) · [STT attribution](THIRD_PARTY_STT.md) · [License](LICENSE)
