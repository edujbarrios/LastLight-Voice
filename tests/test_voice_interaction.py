# SPDX-License-Identifier: MPL-2.0
"""Mic-to-voice integration: deterministic, no physical microphone in CI."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from lastlight_voice import (
    ConfigurationError,
    SpeechEngine,
    VoiceInteraction,
    VoskTranscriber,
)
from lastlight_voice.errors import BackendUnavailableError
from lastlight_voice.interaction import DEFAULT_ACKNOWLEDGEMENT, VoiceTurn


class FakeMic:
    def __init__(self, transcript: str) -> None:
        self.transcript = transcript
        self.timeouts: list[float] = []

    def listen_once(self, *, timeout_seconds: float = 10.0) -> str:
        self.timeouts.append(timeout_seconds)
        return self.transcript


class FakeSpeaker:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def say(self, text: str) -> None:
        self.spoken.append(text)


def test_default_voice_interaction_speaks_without_output_path() -> None:
    mic = FakeMic("hello last light")
    speaker = FakeSpeaker()
    turn = VoiceInteraction(transcriber=mic, speaker=speaker).interact_once(timeout_seconds=7)
    assert turn == VoiceTurn("hello last light", DEFAULT_ACKNOWLEDGEMENT)
    assert mic.timeouts == [7]
    assert speaker.spoken == [DEFAULT_ACKNOWLEDGEMENT]


def test_empty_transcript_never_speaks() -> None:
    speaker = FakeSpeaker()
    assert VoiceInteraction(transcriber=FakeMic(" "), speaker=speaker).interact_once() is None
    assert speaker.spoken == []


def test_custom_responder_is_lastlight_seam() -> None:
    captured = []
    speaker = FakeSpeaker()

    def future_lastlight(query: str) -> str:
        captured.append(query)
        return "Approved local knowledge."

    result = VoiceInteraction(
        transcriber=FakeMic("where is the shelter"),
        speaker=speaker,
        responder=future_lastlight,
    ).interact_once()
    assert captured == ["where is the shelter"]
    assert result is not None and result.response == "Approved local knowledge."
    assert speaker.spoken == ["Approved local knowledge."]


@pytest.mark.parametrize("response", ["", "   ", None, 1])
def test_invalid_response_is_not_spoken(response: object) -> None:
    speaker = FakeSpeaker()
    with pytest.raises(ConfigurationError):
        VoiceInteraction(
            transcriber=FakeMic("hello"),
            speaker=speaker,
            responder=lambda _: response,
        ).interact_once()
    assert not speaker.spoken


def test_bundled_stt_model_is_ready_for_offline_use() -> None:
    recognizer = VoskTranscriber(language="en_US")
    assert recognizer.language == "en"
    assert recognizer.model_available()
    # An available model does not guarantee CI has a physical microphone
    # or the system PortAudio library.
    assert (recognizer.model_dir / "graph" / "HCLr.fst").stat().st_size > 1_000


def test_unsupported_stt_language_fails_explicitly() -> None:
    with pytest.raises(ConfigurationError, match="No bundled speech recognition model"):
        VoskTranscriber(language="es")


def test_missing_model_fails_without_network(tmp_path: Path) -> None:
    recog = VoskTranscriber(model_dir=tmp_path)
    assert not recog.available()
    with pytest.raises(BackendUnavailableError, match="Bundled speech recognition model"):
        recog.listen_once()


@pytest.mark.parametrize("seconds", [-1, 0, 0.1, 121])
def test_invalid_listen_timeout(seconds: float) -> None:
    with pytest.raises(ConfigurationError, match="timeout"):
        VoskTranscriber().listen_once(timeout_seconds=seconds)


def test_streaming_recognition_uses_pcm16_and_returns_text(monkeypatch, tmp_path: Path) -> None:
    recog = VoskTranscriber(model_dir=tmp_path, device=2)
    for name in recog._required:
        filename = tmp_path / name
        filename.parent.mkdir(exist_ok=True, parents=True)
        filename.write_bytes(b"test")

    class FakeStream:
        def __init__(self, **kwargs) -> None:
            assert kwargs == {
                "samplerate": 16000, "blocksize": 4000, "device": 2,
                "channels": 1, "dtype": "int16",
            }
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            return None
        def read(self, count: int):
            return b"\x00\x00" * count, False

    class FakeKaldi:
        def __init__(self, model, sample_rate: int) -> None:
            assert model == str(tmp_path)
            assert sample_rate == 16000
        def AcceptWaveform(self, data: bytes) -> bool:
            assert len(data) == 8000
            return True
        def Result(self) -> str:
            return json.dumps({"text": "recognized microphone phrase"})

    fake_sd = types.SimpleNamespace(RawInputStream=FakeStream, PortAudioError=type("PortAudioError", (Exception,), {}))
    fake_vosk = types.SimpleNamespace(Model=lambda path: path, KaldiRecognizer=FakeKaldi)
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sd)
    monkeypatch.setitem(sys.modules, "vosk", fake_vosk)
    assert recog.listen_once(timeout_seconds=2.0) == "recognized microphone phrase"


def test_cli_interact_does_not_require_file_or_path(monkeypatch, capsys) -> None:
    from lastlight_voice import cli

    class FakeSession:
        def __init__(self, **kwargs):
            assert kwargs["language"] == "en"
        def interact_once(self, *, timeout_seconds=10.0):
            assert timeout_seconds == 3.0
            return VoiceTurn("hello", DEFAULT_ACKNOWLEDGEMENT)

    monkeypatch.setattr(cli, "VoskTranscriber", lambda **kw: object())
    monkeypatch.setattr(cli, "VoiceInteraction", FakeSession)
    assert cli.main(["interact", "--seconds", "3"]) == 0
    out = capsys.readouterr().out
    assert "Heard: hello" in out
    assert DEFAULT_ACKNOWLEDGEMENT in out


def test_cli_interact_no_speech(monkeypatch, capsys) -> None:
    from lastlight_voice import cli

    class NoSpeech:
        def __init__(self, **kw):
            pass
        def interact_once(self, **kw):
            return None

    monkeypatch.setattr(cli, "VoskTranscriber", lambda **kw: object())
    monkeypatch.setattr(cli, "VoiceInteraction", NoSpeech)
    assert cli.main(["interact"]) == 1
    assert "No speech recognized" in capsys.readouterr().err


def test_speaker_can_use_raw_portaudio_without_output_file(monkeypatch) -> None:
    import io
    import wave
    from lastlight_voice.audio import AudioBuffer
    from lastlight_voice.backends.piper import PiperBackend

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 160)
    backend = PiperBackend()
    monkeypatch.setattr(backend, "synthesize", lambda text, language: AudioBuffer.from_wav_bytes(buf.getvalue()))
    played = []

    class RawOutput:
        def __init__(self, **kw):
            assert kw == {"samplerate": 16000, "channels": 1, "dtype": "int16"}
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return None
        def write(self, data):
            played.append(data)

    fake_sd = types.SimpleNamespace(RawOutputStream=RawOutput)
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sd)
    backend.speak("hello", language="en")
    assert played == [b"\x00\x00" * 160]
