# SPDX-License-Identifier: MPL-2.0

import subprocess

import pytest

from lastlight_voice.backends.espeak import EspeakBackend
from lastlight_voice.errors import BackendUnavailableError, SynthesisError


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
