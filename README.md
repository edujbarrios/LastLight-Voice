# LastLight-Voice

**Offline voice interaction for [LastLight](https://github.com/edujbarrios/lastlight) and Python.** Listen, transcribe and answer aloud without a cloud service.

## Features

- **Speech-to-text (English):** bundled Vosk small model; records directly from your microphone.
- **Text-to-speech:** bundled Piper Amy voice for English; eSpeak NG for Spanish if installed.
- **Interaction:** microphone → transcript → spoken acknowledgement, without output files.
- **Extensible:** inject a response handler to use LastLight results in the future.
- **Python API and CLI:** speech synthesis, conversation, diagnostics.

## Install

The library is not yet published on PyPI. Install from GitHub:

```bash
pip install "git+https://github.com/edujbarrios/LastLight-Voice.git"
```

For an editable development installation:

```bash
git clone https://github.com/edujbarrios/LastLight-Voice.git
cd LastLight-Voice
pip install -e .
```

The default installation includes **Piper, Amy, Vosk and the English STT model**.
You need a working microphone and speakers with PortAudio support; on some
Linux systems you may need the system `libportaudio2` package. Model inference
and the exchange of voice messages work **without an Internet connection**.
Installation may need Internet access for dependencies.

## Talk to the library

```bash
lastlight-voice interact
```

Speak in English. It transcribes the first utterance and replies aloud:
**“Hello, I have received your message.”** No WAV file path is required.

```bash
lastlight-voice interact --seconds 15
lastlight-voice doctor
```

## Python API

```python
from lastlight_voice import VoiceInteraction, SpeechEngine

VoiceInteraction().interact_once()  # Listen -> transcribe -> speak

tts = SpeechEngine(language="en")  # Piper Amy automatically
tts.say("LastLight is available offline.")
```

To prepare for future LastLight integration, replace only the response callback:

```python
from lastlight_voice import VoiceInteraction

def respond(transcript: str) -> str:
    # Future: send transcript to LastLight and return an approved passage
    return "Hello, I have received your message."

VoiceInteraction(responder=respond).interact_once()
```

English STT and Piper are installed automatically. Spanish currently supports
**eSpeak NG TTS only**; Spanish transcription requires an additional STT model.

## Licenses

Library: **MPL-2.0**; Piper runtime: **GPL-3.0-or-later**; Vosk STT/model:
**Apache-2.0**. Piper Amy's source repository is marked MIT, but its individual
model/derivation rights still need review before PyPI publication.

[STT model attribution](THIRD_PARTY_STT.md) · [Piper voice attribution](THIRD_PARTY_VOICES.md) · [Architecture](docs/architecture.md) · [License](LICENSE)
