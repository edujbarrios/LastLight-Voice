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
- Optional dependency-free LastLight query-result adapter.
- WAV metadata extraction for sample rate, channels, sample width, and duration.

### Changed

- Dummy and eSpeak synthesis now share the same WAV validation and metadata path.
- eSpeak configuration now rejects non-positive synthesis timeouts.
