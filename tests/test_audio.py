# SPDX-License-Identifier: MPL-2.0

from lastlight_voice import SpeechEngine


def test_audio_buffer_save(tmp_path) -> None:
    audio = SpeechEngine(backend="dummy").synthesize("offline")
    output = tmp_path / "speech.wav"

    saved = audio.save(output)

    assert saved == output
    assert output.read_bytes() == audio.data
