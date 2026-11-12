# Offline speech-recognition model: credits and license

- **Recognizer and model:** Vosk by Alpha Cephei / Vosk contributors.
- **Model:** `vosk-model-small-en-us-0.15` (US English), bundled unmodified.
- **Official source:** https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- **Official catalog:** https://alphacephei.com/vosk/models (lists this model as Apache-2.0).
- **SHA-256 of original ZIP:** `30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498`.
- **License:** Apache License 2.0. A complete copy is distributed in
  `src/lastlight_voice/stt_models/APACHE-2.0.txt`.
- **Capture:** 16 kHz, mono, signed PCM16 microphone input. No recording or
  transcript is sent to a remote service or saved to a file by default.

The model source is redistributed for offline STT. It is independent of the
English Piper Amy voice; its rights caveat is documented in
[THIRD_PARTY_VOICES.md](THIRD_PARTY_VOICES.md). No endorsement by Alpha Cephei,
Vosk or the upstream contributors is implied.
