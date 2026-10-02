# Architecture

LastLight-Voice is deliberately split into a small public engine and replaceable local speech backends.

```text
application / LastLight integration
              |
              v
        SpeechEngine
              |
              v
         TTSBackend
          /      \
       eSpeak   Dummy
```

## Dependency direction

`lastlight_voice` does not require `lastlight`. The integration module consumes only the small `accepted` / `passage` result contract through a Python `Protocol`, so the package remains independently useful.

LastLight itself must never depend on LastLight-Voice. Speech is an optional companion capability rather than part of retrieval semantics.

## Offline contract

The runtime performs no HTTP requests, update checks, model downloads, telemetry, or account authentication. eSpeak NG is detected as a local executable and is never installed automatically.

## Backend selection

v0.1 deliberately has a conservative policy:

1. Explicit backend selection always wins.
2. Automatic selection chooses eSpeak NG when installed.
3. The dummy backend is never selected silently because it produces no audible output and exists for tests/integration development.
4. If no real backend is available, construction fails with a clear `BackendUnavailableError`.

This behavior is deterministic and auditable.

## Languages

The initial public support surface is intentionally limited to English and Spanish. Locale variants normalize to the backend language family:

- `en`, `en-US`, `en-GB` -> `en`
- `es`, `es-ES`, `es-MX` -> `es`

## Resource direction

Future neural TTS and STT support must justify its memory, CPU, disk, startup, and energy cost. The smallest viable local engine should remain the default. Piper low-resource voices and lightweight offline STT are roadmap items, not v0.1 dependencies.
