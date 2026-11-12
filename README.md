# LastLight-Voice

**Offline text-to-speech for LastLight.** Local synthesis, no cloud APIs, telemetry or runtime downloads.

## Features

- **eSpeak NG (default):** low-resource English and Spanish speech.
- **Piper (optional):** English neural voice `en_US-amy-low` (~63 MB ONNX), stored in this review branch.
- **Python API:** `SpeechEngine.say()`, `synthesize()`, `save()`, and `voices()`.
- **CLI:** `speak`, `synthesize`, `voices`, `doctor`, and `inspect`.
- **Offline-first:** explicit backend selection, no model downloads during synthesis.
- **Extensible voices:** JSON voice catalog and separate language wheels for future languages.
- **Testing:** deterministic dummy backend and Python 3.10+ tests.

Speech-to-text and wake words are not implemented yet.

## Install (GitHub review branch)

```bash
git clone --branch feat/piper-amy-pypi-review https://github.com/edujbarrios/LastLight-Voice.git
cd LastLight-Voice
python -m pip install -e ".[piper]"
```

**What gets installed?**

| Command | What it does |
| --- | --- |
| `pip install -e .` | Installs the core library, **not** Piper or any voice weights |
| `pip install -e ".[piper]"` | Installs the core library **and the Piper runtime**, but does **not** download weights |
| `git clone --branch feat/piper-amy-pypi-review …` | Fetches the model already committed to GitHub under `voice_assets/en_US-amy-low/` |

The model is currently **in the review branch, not `main`**, and is **not included in the core pip wheel**. eSpeak NG must be installed separately if you want its lightweight backend.

## Use Piper offline (English)

Point the backend at the model that came with your Git clone:

```bash
export LASTLIGHT_VOICE_MODELS_DIR="$PWD/voice_assets"
lastlight-voice synthesize --backend piper --language en \
  "Knowledge remains available offline." voice.wav
```

PowerShell: `$env:LASTLIGHT_VOICE_MODELS_DIR = (Resolve-Path voice_assets).Path`

Or use Python without an environment variable:

```python
from lastlight_voice import SpeechEngine
from lastlight_voice.backends.piper import PiperBackend

speech = SpeechEngine(language="en", backend=PiperBackend(models_dir="voice_assets"))
speech.save("Stay safe.", "voice.wav")
```

The model and Piper must be installed locally **before** going offline. No network is used during synthesis.

## Use eSpeak NG or the CLI

```python
from lastlight_voice import SpeechEngine

SpeechEngine(language="es").say("La información está disponible sin conexión.")
SpeechEngine(backend="dummy").save("Test", "test.wav")
```

```bash
lastlight-voice doctor
lastlight-voice inspect
lastlight-voice voices --backend piper --language en
```

## Packaging and license

- **PyPI:** not published. The lightweight `lastlight-voice` core and optional `lastlight-voice-model-en` voice wheel are prepared for review, not release.
- **Model source:** [Piper Voices](https://huggingface.co/rhasspy/piper-voices), maintained by Michael Hansen and the Rhasspy/Piper community; the original `MODEL_CARD` is included.
- **Rights:** the Piper voice collection is labeled MIT, but Amy's model card references Mimic 3 and a Ryan-derived training lineage. Rights to redistribute the trained weights still require review.
- **Licenses:** application code MPL-2.0; optional Piper runtime has its own GPL license. See [third-party credits and licensing](THIRD_PARTY_VOICES.md) and the [PyPI release checklist](docs/PIPER_RELEASE_REVIEW.md).

[LastLight integration](src/lastlight_voice/integrations/lastlight.py) · [Contributing](CONTRIBUTING.md) · [License](LICENSE)
