# SPDX-License-Identifier: MPL-2.0

"""Small public speech engine for LastLight-Voice."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from .audio import AudioBuffer
from .backends.base import TTSBackend
from .backends.dummy import DummyTTSBackend
from .backends.espeak import EspeakBackend
from .errors import BackendUnavailableError, ConfigurationError
from .models import BackendCapabilities, Voice

_LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})*$", re.IGNORECASE)


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
        self._backend = _resolve_backend(backend)
        self._language = _normalize_language(language, self._backend)

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

    def save(self, text: str, path: str | Path) -> Path:
        """Synthesize text to WAV and return the written output path."""
        return self.synthesize(text).save(path)

    def stop(self) -> None:
        self._backend.stop()

    @staticmethod
    def _validate_text(text: str) -> None:
        if not isinstance(text, str) or not text.strip():
            raise ConfigurationError("Speech text must be a non-empty string.")


def _normalize_language(language: str, backend: TTSBackend) -> str:
    """Recognize locales via the active backend's installed voices."""
    if not isinstance(language, str) or not _LANGUAGE_TAG.fullmatch(language.strip()):
        raise ConfigurationError(f"Invalid language tag: {language!r}")
    family = language.strip().replace("_", "-").split("-", 1)[0].lower()
    supported = {
        voice.language.split("-", 1)[0].split("_", 1)[0].lower()
        for voice in backend.voices(None)
    }
    if family not in supported:
        raise ConfigurationError(
            f"Unsupported language {language!r} for backend {backend.name!r}. "
            f"Locally available languages: {', '.join(sorted(supported)) or 'none'}."
        )
    return family


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
        elif normalized == "piper":
            from .backends.piper import PiperBackend
            candidate = PiperBackend()
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
