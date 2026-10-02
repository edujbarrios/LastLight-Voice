# SPDX-License-Identifier: MPL-2.0

import pytest

from lastlight_voice import ConfigurationError, SpeechEngine
from lastlight_voice.backends import DummyTTSBackend


def test_dummy_backend_speaks_without_hardware() -> None:
    backend = DummyTTSBackend()
    engine = SpeechEngine(language="es-ES", backend=backend)

    engine.say("Hola")

    assert engine.backend_name == "dummy"
    assert engine.language == "es"
    assert backend.spoken == [("Hola", "es")]


def test_dummy_synthesis_produces_wav() -> None:
    engine = SpeechEngine(backend="dummy")

    audio = engine.synthesize("Hello")

    assert audio.format == "wav"
    assert audio.data.startswith(b"RIFF")
    assert audio.sample_rate == 8_000


def test_save_returns_written_path(tmp_path) -> None:
    engine = SpeechEngine(backend="dummy")
    output = tmp_path / "answer.wav"

    written = engine.save("Offline answer", output)

    assert written == output
    assert output.read_bytes().startswith(b"RIFF")


@pytest.mark.parametrize("language", ["en", "en-US", "en_GB"])
def test_english_locales_normalize(language: str) -> None:
    assert SpeechEngine(language=language, backend="dummy").language == "en"


@pytest.mark.parametrize("language", ["es", "es-ES", "es_MX"])
def test_spanish_locales_normalize(language: str) -> None:
    assert SpeechEngine(language=language, backend="dummy").language == "es"


def test_rejects_unsupported_language() -> None:
    with pytest.raises(ConfigurationError):
        SpeechEngine(language="fr", backend="dummy")


def test_rejects_empty_text() -> None:
    engine = SpeechEngine(backend="dummy")
    with pytest.raises(ConfigurationError):
        engine.say("   ")
