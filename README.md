# LastLight-Voice

**Offline speech for LastLight, built for constrained environments.**

LastLight-Voice is an open-source, low-resource speech runtime for [LastLight](https://github.com/edujbarrios/lastlight) and other infrastructure-constrained environments.

Its goal is to keep local knowledge accessible when a keyboard, screen, network connection, or even free hands are unavailable. The project starts with lightweight offline text-to-speech and is designed to evolve toward offline speech-to-text and hands-free LastLight interaction without cloud APIs, telemetry, or runtime downloads.

## Project status

Early development. The first milestone focuses on a small typed Python API, a dummy backend for deterministic testing, and an eSpeak NG backend for low-resource offline synthesis on Linux.

## Design principles

- Offline-first runtime: no cloud APIs, telemetry, update checks, or automatic downloads.
- Low-resource by default: prefer the smallest viable speech backend.
- English and Spanish first.
- Auditable and deterministic behavior.
- LastLight integration stays optional; the speech runtime must also work standalone.
- Open source under the Mozilla Public License 2.0.

## Planned v0.1

- `SpeechEngine`
- `DummyTTSBackend`
- eSpeak NG backend
- English and Spanish language selection
- `say()` and WAV synthesis
- `lastlight-voice` CLI
- offline `doctor` / `inspect` diagnostics
- typed public API and tests

## Development install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The runtime itself must remain usable without network access after installation.

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

The eventual objective is hands-free, fully local access to LastLight in the same kinds of emergency and infrastructure-failure environments that motivate the core project.

## License

Mozilla Public License 2.0.
