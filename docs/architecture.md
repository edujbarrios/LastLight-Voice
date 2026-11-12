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
