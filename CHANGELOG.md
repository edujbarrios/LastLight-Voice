# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and the project intends to follow Semantic Versioning once releases begin.

## [Unreleased]

### Added

- Initial low-resource offline TTS architecture.
- `SpeechEngine` public API.
- Dummy backend for deterministic testing.
- eSpeak NG backend for local English and Spanish speech.
- Offline `doctor` and `inspect` commands.
- CLI `synthesize` command for writing local WAV files.
- Optional dependency-free LastLight query-result adapter.
- WAV metadata extraction for sample rate, channels, sample width, and duration.
- Diagnostics for the resolved eSpeak executable, supported languages, network policy, automatic downloads, and offline readiness.

### Changed

- `SpeechEngine.save()` now returns the written output path.
- Dummy and eSpeak synthesis now share the same WAV validation and metadata path.
- eSpeak configuration now rejects non-positive synthesis timeouts.
- README now documents the implemented v0.1 API and offline contract rather than presenting them as planned work.
