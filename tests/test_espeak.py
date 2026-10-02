# SPDX-License-Identifier: MPL-2.0

import io
import subprocess
import wave

import pytest

from lastlight_voice.backends.espeak import EspeakBackend
from lastlight_voice.errors import BackendUnavailableError, ConfigurationError, SynthesisError


def test_espeak_unavailable_is_explicit(monkeypatch) -> None:
    monkeypatch.setattr("lastlight_voice.backends.espeak.shutil.which", lambda _: None)
    backend = EspeakBackend()

    assert backend.available() is False
    with pytest.raises(BackendUnavailableError):
        backend.speak("hello", language="en")


def test_espeak_uses_argument_list_not_shell(monkeypatch) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("lastlight_voice.backends.espeak.subprocess.run", fake_run)
    backend = EspeakBackend(executable="/usr/bin/espeak-ng")
    backend.speak("hello world", language="en")

    command, kwargs = calls[0]
    assert command == ["/usr/bin/espeak-ng", "-v", "en", "hello world"]
    assert "shell" not in kwargs
    assert kwargs["check"] is True


def test_espeak_timeout_is_wrapped(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=1)

    monkeypatch.setattr("lastlight_voice.backends.espeak.subprocess.run", timeout)
    backend = EspeakBackend(executable="espeak-ng", timeout=1)

    with pytest.raises(SynthesisError, match="timeout"):
        backend.speak("hello", language="en")


def test_espeak_rejects_non_positive_timeout() -> None:
    with pytest.raises(ConfigurationError, match="greater than zero"):
        EspeakBackend(timeout=0)


def test_espeak_synthesis_extracts_wav_metadata(monkeypatch) -> None:
    def fake_run(command, **kwargs):
        output_path = command[command.index("-w") + 1]
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16_000)
            wav.writeframes(b"\x00\x00" * 160)
        with open(output_path, "wb") as handle:
            handle.write(buffer.getvalue())
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("lastlight_voice.backends.espeak.subprocess.run", fake_run)
    backend = EspeakBackend(executable="espeak-ng")

    audio = backend.synthesize("hello", language="en")

    assert audio.sample_rate == 16_000
    assert audio.channels == 1
    assert audio.sample_width == 2
    assert audio.duration == pytest.approx(0.01)
