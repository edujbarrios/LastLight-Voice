# Architecture

LastLight-Voice exposes a single `SpeechEngine` API with interchangeable offline TTS backends.

```text
application / optional LastLight integration
                |
           SpeechEngine
                |
             TTSBackend
           /     |      \
        Piper  eSpeak   Dummy
         en    en/es    tests
```

## Backend selection

1. A backend explicitly supplied by the caller takes precedence.
2. For English, the engine selects **Piper Amy low** when the installed binary and bundled model are available; otherwise it uses locally installed eSpeak NG.
3. For Spanish, the engine uses locally installed eSpeak NG.
4. Dummy is selected only explicitly. If no real backend is ready, the engine raises `BackendUnavailableError`.

All backend selection is local, deterministic, and free of runtime downloads.

## Packaging and voice discovery

- `pip install -e .` or a standard wheel install includes the Piper runtime dependency and `en_US-amy-low` ONNX, JSON and original model card.
- Models are discovered under `lastlight_voice/voices/`; a validated JSON catalog maps voice IDs to languages.
- New voices can be added to the catalog and packaged inside the library or provided by a separately installed language package, without rewriting `SpeechEngine`.
- `LASTLIGHT_VOICE_MODELS_DIR` and the `PiperBackend(models_dir=...)` override support external model assets for development and testing.

The core does not download models during import, initialization or speech synthesis. Standard pip dependency resolution still requires network access unless its dependencies are locally cached.

## Integration and constraints

`lastlight_voice` does **not** depend on the LastLight retrieval package. The optional adapter speaks accepted responses and deterministic refusals; it does not modify knowledge.

The package contains about 63 MB of neural voice weights and depends on Piper/ONNX Runtime. eSpeak NG remains an OS-installed alternative, including for Spanish. Resource and license implications are described in [the README](../README.md) and [third-party voice notice](../THIRD_PARTY_VOICES.md).
