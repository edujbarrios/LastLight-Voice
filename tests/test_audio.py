# SPDX-License-Identifier: MPL-2.0

import pytest

from lastlight_voice import SpeechEngine
from lastlight_voice.audio import AudioBuffer
from lastlight_voice.errors import AudioError


def test_audio_buffer_save(tmp_path) -> None:
    audio = SpeechEngine(backend="dummy").synthesize("offline")
    output = tmp_path / "speech.wav"

    saved = audio.save(output)

    assert saved == output
    assert output.read_bytes() == audio.data


def test_dummy_audio_exposes_wav_metadata() -> None:
    audio = SpeechEngine(backend="dummy").synthesize("offline")

    assert audio.format == "wav"
    assert audio.sample_rate == 8_000
    assert audio.channels == 1
    assert audio.sample_width == 2
    assert audio.duration == pytest.approx(0.01)


def test_wav_parser_rejects_invalid_bytes() -> None:
    with pytest.raises(AudioError, match="Invalid WAV data"):
        AudioBuffer.from_wav_bytes(b"not-a-wav")


def test_wav_parser_rejects_empty_data() -> None:
    with pytest.raises(AudioError, match="non-empty bytes"):
        AudioBuffer.from_wav_bytes(b"")
