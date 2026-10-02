# SPDX-License-Identifier: MPL-2.0

"""Backend contract for text-to-speech implementations."""

from typing import Protocol, Sequence, runtime_checkable

from ..audio import AudioBuffer
from ..models import BackendCapabilities, Voice


@runtime_checkable
class TTSBackend(Protocol):
    """Minimal contract implemented by every LastLight-Voice TTS backend."""

    name: str

    def available(self) -> bool:
        """Return whether the backend can run on the current machine."""

    def capabilities(self) -> BackendCapabilities:
        """Return static backend capabilities."""

    def voices(self, language: str | None = None) -> Sequence[Voice]:
        """Return supported voices, optionally filtered by language."""

    def speak(self, text: str, *, language: str) -> None:
        """Speak text using local audio output."""

    def synthesize(self, text: str, *, language: str) -> AudioBuffer:
        """Synthesize text and return encoded audio."""

    def stop(self) -> None:
        """Stop active playback when supported."""
