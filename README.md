# LastLight-Voice

**Offline speech for LastLight, built for constrained environments.**

LastLight-Voice is an open-source, low-resource speech runtime for [LastLight](https://github.com/edujbarrios/lastlight) and other infrastructure-constrained environments.

Its purpose is to keep local knowledge accessible when a keyboard, screen, network connection, or even free hands are unavailable. The project starts with lightweight offline text-to-speech and is designed to evolve toward offline speech-to-text and hands-free LastLight interaction without cloud APIs, telemetry, or runtime downloads.

## Status

`0.1.0` is an early alpha focused on a small, auditable TTS foundation. It currently provides:

- a typed `SpeechEngine` API;
- a deterministic `DummyTTSBackend` for tests and integrations;
- low-resource eSpeak NG support on systems where `espeak-ng` is installed;
- English and Spanish language selection for eSpeak NG;
- optional Piper English voice registration (Amy low), without bundled weights or runtime downloads;
- direct speech and WAV synthesis;
- local-only `doctor` and `inspect` diagnostics;
- an optional LastLight query-result adapter;
- tests and CI on Python 3.10, 3.11, and 3.12.

Speech-to-text, wake words and VAD remain roadmap work. The Piper backend is experimental and opt-in; no voice weights are bundled.

## Design principles

- **Offline-first runtime.** No cloud APIs, telemetry, update checks, or automatic downloads.
- **Low-resource by default.** Prefer the smallest viable speech backend over higher-quality but more expensive alternatives.
- **English neural voice first.** Piper currently registers Amy low; eSpeak keeps English and Spanish support.
- **Auditable behavior.** Backend selection and failures should remain explicit.
- **Independent runtime.** LastLight integration is optional; `lastlight_voice` works standalone.
- **Open source.** Source code is licensed under MPL-2.0.

## Development install

LastLight-Voice is not published to PyPI yet. Install it from a checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
pytest
```

The Python package has no mandatory runtime dependencies. Real speech in v0.1 uses a locally installed `espeak-ng` executable. Install eSpeak NG using your operating system's package manager before using the real backend.

## Python API

```python
from lastlight_voice import SpeechEngine

speech = SpeechEngine(language="en")
speech.say("LastLight Voice is running offline.")
```

Spanish:

```python
speech = SpeechEngine(language="es")
speech.say("LastLight Voice está funcionando sin conexión.")
```

Synthesize to memory:

```python
audio = speech.synthesize("Emergency information is available locally.")
print(audio.sample_rate, audio.channels, audio.duration)
```

Synthesize directly to a WAV file:

```python
output = speech.save("Emergency information is available locally.", "answer.wav")
print(output)
```

For deterministic tests without audio hardware:

```python
speech = SpeechEngine(backend="dummy")
```

The dummy backend is never selected silently during normal use.

## CLI

Check the local machine without making any network request:

```bash
lastlight-voice doctor
```

Machine-readable diagnostics:

```bash
lastlight-voice inspect
```

Speak English:

```bash
lastlight-voice speak "LastLight Voice is running offline."
```

Speak Spanish:

```bash
lastlight-voice speak --language es "La información está disponible sin conexión."
```

Create a WAV file:

```bash
lastlight-voice synthesize "Emergency information" answer.wav
```

List voices exposed by the selected backend:

```bash
lastlight-voice voices --language en
```

## Optional Piper voice: English only

The experimental Piper backend registers only `en_US-amy-low` (English, US). It
uses a data-driven JSON catalog (`src/lastlight_voice/piper_catalog.json`), so
future languages and voices need no speech-engine rewrite. The existing
English/Spanish eSpeak NG backend remains the default.

**Licensing gate:** Amy low's upstream MODEL_CARD says its dataset license is
`See URL` and that it was fine-tuned from the Ryan low model. Rights to
redistribute the resulting weights have not been established here. Do **not**
publish an Amy model wheel on PyPI until you have independently confirmed
the voice and training-lineage rights. No model weights are in this repository.

Install Piper as an opt-in dependency (current `piper-tts` is GPL-3.0-or-later,
which may affect how you distribute integrations), then explicitly prepare
the voice once while online:

```sh
python -m pip install -e ".[piper]"
python scripts/package_piper_voices.py --list
python scripts/package_piper_voices.py --voice en_US-amy-low --download
export LASTLIGHT_VOICE_MODELS_DIR=.piper-model-cache
lastlight-voice synthesize --backend piper --language en "Stay safe." speech.wav
```

On Windows PowerShell, use
`$env:LASTLIGHT_VOICE_MODELS_DIR='.piper-model-cache'` instead of `export`.
After provisioning, inference works without network access. No downloads
occur at import, installation or synthesis time.

Python API:

```python
from lastlight_voice import SpeechEngine
from lastlight_voice.backends.piper import PiperBackend

engine = SpeechEngine(
    language="en",
    backend=PiperBackend(models_dir=".piper-model-cache"),
)
engine.save("Knowledge remains available offline.", "speech.wav")
```

**Future PyPI voice packs:** after confirming redistribution rights, run the
separate explicit `--prepare-packs --acknowledge-licenses` option to generate
the source for a local English voice wheel containing ONNX, JSON and MODEL_CARD.
Use `python -m build --wheel <generated-directory>` to build that wheel.
The wheel name is `lastlight-voice-model-en` and is discovered automatically
when installed alongside the main package. It is not currently published.
The English model is around 63.1 MB before wheel compression and dependencies.
Separate voice wheels let the core package stay small as new languages arrive.

Custom local model directories may contain the two voice files either
directly or inside a directory named `en_US-amy-low`. The engine never
silently falls back to another voice if an expected Piper model is missing.

## Offline contract

Normal runtime behavior must not require a network connection. The core intentionally performs no:

- HTTP requests;
- cloud speech calls;
- telemetry;
- automatic model downloads;
- automatic update checks;
- account or API-token authentication.

External speech engines or future models must be installed explicitly before offline use.

## LastLight integration

LastLight remains the authority for retrieval and refusal. LastLight-Voice only speaks the result; it does not generate or rewrite knowledge.

```python
from lastlight import LastLight
from lastlight_voice import SpeechEngine
from lastlight_voice.integrations.lastlight import speak_query_result

knowledge = LastLight("lastlight-example-en.zip")
speech = SpeechEngine(language="en")

result = knowledge.query("How long will food stay safe in the refrigerator?")
speak_query_result(result, speech)
```

If `result.accepted` is false, the adapter speaks a deterministic refusal instead of inventing an answer.

## Long-term direction

```text
microphone
   |
   v
offline STT
   |
   v
LastLight
   |
   v
offline TTS
   |
   v
speaker
```

The target is hands-free, fully local access to LastLight in emergency and infrastructure-failure environments where conventional input devices may be unavailable or impractical.

Future work will remain biased toward small English/Spanish models, measurable resource use, graceful fallback, and Raspberry Pi / low-power Linux hardware.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New runtime dependencies, network access, or significantly heavier models should be justified against the project's low-resource and offline goals.

## License

Mozilla Public License 2.0. See [LICENSE](LICENSE).
