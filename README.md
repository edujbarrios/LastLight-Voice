# LastLight-Voice

**Offline speech for LastLight.** English neural TTS with Piper, Spanish via eSpeak NG, no cloud calls or model downloads at runtime.

## Features

- **English:** bundled Piper `en_US-amy-low` (ONNX, 63.1 MB), selected automatically.
- **Spanish:** eSpeak NG if installed on your system.
- **Python:** `SpeechEngine.say()`, `synthesize()`, `save()`, `voices()`.
- **CLI:** `speak`, `synthesize`, `voices`, `doctor`, `inspect`.
- **Offline:** all neural weights and configuration ship with the library; no network during speech.
- **Extensible:** language-to-voice mappings are stored in a JSON catalog, not hard-coded in the engine.

Speech-to-text and wake-word detection are not yet supported.

## Installation

LastLight-Voice is **not yet published on PyPI**. From this review branch:

```bash
git clone --branch feat/piper-amy-pypi-review https://github.com/edujbarrios/LastLight-Voice.git
cd LastLight-Voice
python -m pip install -e .
```

That's it for English: **`pip install -e .` installs Piper and includes the Amy voice**, with no extras, separate voice package, environment variables or post-install downloads. Building a standard wheel with `python -m build` also includes the model.

The Git clone transfers the model with the source files. Pip downloads ordinary Python dependencies at install time; **speech synthesis itself needs no Internet**. For Spanish, install `espeak-ng` separately using your OS package manager.

## Usage

```python
from lastlight_voice import SpeechEngine

speech = SpeechEngine(language="en")  # Piper Amy automatically
speech.say("LastLight works offline.")
speech.save("Emergency information is available.", "message.wav")

spanish = SpeechEngine(language="es")  # eSpeak NG if installed
spanish.say("La información está disponible sin conexión.")
```

```bash
lastlight-voice synthesize --language en "Stay safe." output.wav
lastlight-voice speak --language en "Knowledge remains available."
lastlight-voice voices --backend piper --language en
lastlight-voice doctor
lastlight-voice inspect
```

Use `backend="espeak"` or `backend="dummy"` explicitly to select other engines. If Piper is unavailable for English, eSpeak NG is the local fallback; the library does not download a replacement model.

## Packaging and license

- **Python package:** MPL-2.0 source code; required `piper-tts` dependency is GPL-3.0-or-later.
- **Voice:** Piper/Rhasspy `en_US-amy-low`. Credits to Michael Hansen, Rhasspy/Piper contributors and the original model/data providers. The original `MODEL_CARD` and attribution notice ship inside the installed package.
- **Review required:** the Piper collection is labeled MIT, but Amy's own model card refers to a Mimic 3 dataset and Ryan fine-tuning lineage. Permission to redistribute Amy weights under that label is not established by the card alone.
- **Release status:** code and model are on the GitHub review branch; **nothing has been uploaded to PyPI**.

[Voice attribution and license review](THIRD_PARTY_VOICES.md) · [PyPI checklist](docs/PIPER_RELEASE_REVIEW.md) · [Contributing](CONTRIBUTING.md) · [License](LICENSE)
