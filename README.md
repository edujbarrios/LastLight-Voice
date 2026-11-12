# LastLight-Voice

**Offline text-to-speech for [LastLight](https://github.com/edujbarrios/lastlight) and Python applications.** No cloud services or runtime model downloads.

## Features

- **English:** Piper TTS with bundled `en_US-amy-low` model (~63 MB), selected automatically.
- **Spanish:** eSpeak NG (requires the system executable).
- **API + CLI:** speak, synthesize WAV, list voices, inspect and diagnose.
- **Extensible:** local voice catalog designed for adding languages; optional LastLight integration.
- **Offline inference:** model weights and configuration are included in the package.

## Install

Not yet on PyPI. Install the current **`main` branch** directly:

```bash
python -m pip install "git+https://github.com/edujbarrios/LastLight-Voice.git"
```

For development (editable install):

```bash
git clone https://github.com/edujbarrios/LastLight-Voice.git
cd LastLight-Voice
python -m pip install -e .
```

**Both commands install Piper and the English Amy voice automatically.** No `[piper]` extra, model download, or environment variables are needed. Installation may use the Internet for GitHub and Python dependencies; **synthesis works offline** afterward. For Spanish, install `espeak-ng` separately with your system package manager.

## Usage

```python
from lastlight_voice import SpeechEngine

speech = SpeechEngine(language="en")  # Piper Amy
speech.save("Emergency information is available offline.", "message.wav")
speech.say("Stay safe.")  # Requires a local audio player

# If eSpeak NG is installed:
SpeechEngine(language="es").save("Información disponible sin conexión.", "es.wav")
```

```bash
lastlight-voice synthesize --language en "LastLight works offline." voice.wav
lastlight-voice voices --backend piper --language en
lastlight-voice doctor
```

## Licenses and attribution

LastLight-Voice code: **MPL-2.0**. Piper runtime: **GPL-3.0-or-later**. English voice: **Piper/Rhasspy Amy low**, credited to Michael Hansen, Piper contributors and upstream providers. The model and original `MODEL_CARD` ship with the package.

The Piper voice repository is tagged MIT, but **Amy's individual model card does not independently establish redistribution rights for its weights or Ryan-derived training lineage**. Review this before PyPI publication.

[Third-party voice notices](THIRD_PARTY_VOICES.md) · [PyPI release checklist](docs/PIPER_RELEASE_REVIEW.md) · [Architecture](docs/architecture.md) · [License](LICENSE)
