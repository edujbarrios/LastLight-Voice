# Architecture

One offline exchange:

```text
microphone -> Vosk STT (English) -> transcript -> responder(transcript)
    -> text response -> Piper TTS (English) -> speaker
```

- `VoiceInteraction().interact_once()` uses a built-in deterministic response.
- Supply `responder: Callable[[str], str]` to connect LastLight later.
- No file paths, internet calls, recordings, or persistent transcripts required.
- The microphone is closed before playback starts to avoid feedback.
- `SpeechEngine` supports other backends: Piper for English and eSpeak NG for Spanish.
- `VoskTranscriber` reads its selected model from `stt_catalog.json`; adding a
  new STT language requires another model and catalog entry, not changes to the
  interaction engine.

The package bundles neural model weights for English STT and TTS. Platform
support depends on installed Vosk/Piper wheels and a functioning audio device.
No runtime model downloads or telemetry.

## Optional original LastLight adapter

The `make_lastlight_responder(knowledge, top_k=3)` adapter accepts an already
initialized `LastLight` instance and calls only its public `query()` method.
It reads `QueryResult.accepted` and `QueryResult.passage`; an unaccepted
result always becomes a deterministic spoken refusal. The default CLI remains
a fixed acknowledgement, with no implicit knowledge-pack access.

The adapter is optional and uses `typing.Protocol`, so LastLight-Voice does
not require or import the `lastlight` package at runtime unless the caller
explicitly wires both libraries together. This keeps their release cycles,
retrieval policies and dependency footprints independent.

See [the integration guide](lastlight_integration.md).
