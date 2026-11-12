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
    """Local text-to-speech engine with English Piper as the default.

    English uses bundled Piper Amy when available, falling back to eSpeak NG.
    Spanish requires eSpeak NG. The dummy backend is opt-in for testing.
    """

    def __init__(
        self,
        *,
        language: str = "en",
        backend: str | TTSBackend | None = None,
    ) -> None:
        # Validate user input before probing backends. Invalid tags should
        # always raise ConfigurationError, not AttributeError or backend errors.
        family = _language_family(language)
        self._backend = _resolve_backend(backend, language=family)
        self._language = _normalize_language(family, self._backend)

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


def _language_family(language: str) -> str:
    """Validate BCP-47-like language input before selecting a backend."""
    if not isinstance(language, str) or not _LANGUAGE_TAG.fullmatch(language.strip()):
        raise ConfigurationError(f"Invalid language tag: {language!r}")
    return language.strip().replace("_", "-").split("-", 1)[0].lower()


def _normalize_language(language: str, backend: TTSBackend) -> str:
    """Check that the selected backend offers the normalized language."""
    family = _language_family(language)
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


def _resolve_backend(backend: str | TTSBackend | None, *, language: str = "en") -> TTSBackend:
    if backend is None:
        # English uses the bundled offline Piper voice by default. Preserve
        # eSpeak NG as the lightweight alternative and Spanish backend.
        family = language.strip().replace("_", "-").lower().split("-", 1)[0]
        if family == "en":
            from .backends.piper import PiperBackend
            piper = PiperBackend()
            if piper.available():
                return piper
        candidate = EspeakBackend()
        if candidate.available():
            return candidate
        raise BackendUnavailableError(
            "No local real TTS backend is ready. Install Piper for English or "
            "eSpeak NG for English/Spanish; use backend='dummy' only for tests."
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
