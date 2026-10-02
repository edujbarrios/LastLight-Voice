# SPDX-License-Identifier: MPL-2.0

"""Small public speech engine for LastLight-Voice."""

from __future__ import annotations

from typing import Sequence

from .audio import AudioBuffer
from .backends.base import TTSBackend
from .backends.dummy import DummyTTSBackend
from .backends.espeak import EspeakBackend
from .errors import BackendUnavailableError, ConfigurationError
from .models import BackendCapabilities, Voice

_SUPPORTED_LANGUAGES = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "es": "es",
    "es-es": "es",
    "es-mx": "es",
}


class SpeechEngine:
    """Low-resource offline text-to-speech engine.

    If no backend is supplied, eSpeak NG is selected when locally available.
    The dummy backend is never chosen silently because doing so would make a
    failed audio setup look successful.
    """

    def __init__(
        self,
        *,
        language: str = "en",
        backend: str | TTSBackend | None = None,
    ) -> None:
        self._language = _normalize_language(language)
        self._backend = _resolve_backend(backend)

    @property
    def language(self) -> str:
        return self._language

    @property
    def backend_name(self) -> str:
        return self._backend.name

    def capabilities(self) -> BackendCapabilities:
        return self._backend.capabilities()

    def voices(self) -> Sequence[Voice]:
        return self._backend.voices(self._language)

    def say(self, text: str) -> None:
        self._validate_text(text)
        self._backend.speak(text, language=self._language)

    def synthesize(self, text: str) -> AudioBuffer:
        self._validate_text(text)
        return self._backend.synthesize(text, language=self._language)

    def save(self, text: str, path: str) -> None:
        self.synthesize(text).save(path)

    def stop(self) -> None:
        self._backend.stop()

    @staticmethod
    def _validate_text(text: str) -> None:
        if not isinstance(text, str) or not text.strip():
            raise ConfigurationError("Speech text must be a non-empty string.")


def _normalize_language(language: str) -> str:
    normalized = language.strip().replace("_", "-").lower()
    try:
        return _SUPPORTED_LANGUAGES[normalized]
    except KeyError as exc:
        raise ConfigurationError(
            "Unsupported language. LastLight-Voice v0.1 supports English and Spanish "
            "(en, en-US, en-GB, es, es-ES, es-MX)."
        ) from exc


def _resolve_backend(backend: str | TTSBackend | None) -> TTSBackend:
    if backend is None:
        candidate = EspeakBackend()
        if candidate.available():
            return candidate
        raise BackendUnavailableError(
            "No real offline TTS backend is available. Install eSpeak NG or explicitly "
            "use backend='dummy' for tests."
        )

    if isinstance(backend, str):
        normalized = backend.strip().lower()
        if normalized in {"espeak", "espeak-ng"}:
            candidate = EspeakBackend()
        elif normalized == "dummy":
            candidate = DummyTTSBackend()
        else:
            raise ConfigurationError(f"Unknown TTS backend: {backend!r}")
        if not candidate.available():
            raise BackendUnavailableError(f"TTS backend {candidate.name!r} is unavailable.")
        return candidate

    if not isinstance(backend, TTSBackend):
        raise ConfigurationError("backend must be a backend name or TTSBackend implementation.")
    if not backend.available():
        raise BackendUnavailableError(f"TTS backend {backend.name!r} is unavailable.")
    return backend
