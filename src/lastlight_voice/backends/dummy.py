# SPDX-License-Identifier: MPL-2.0

"""Deterministic no-hardware backend used by tests and integrators."""

from __future__ import annotations

import io
import wave
from typing import Sequence

from ..audio import AudioBuffer
from ..models import BackendCapabilities, Voice


class DummyTTSBackend:
    """A zero-dependency backend that records calls and emits silent WAV data."""

    name = "dummy"

    def __init__(self) -> None:
        self.spoken: list[tuple[str, str]] = []

    def available(self) -> bool:
        return True

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name,
            supports_playback=False,
            supports_stop=False,
        )

    def voices(self, language: str | None = None) -> Sequence[Voice]:
        voices = (
            Voice("dummy-en", "Dummy English", "en", self.name),
            Voice("dummy-es", "Dummy Spanish", "es", self.name),
        )
        if language is None:
            return voices
        return tuple(voice for voice in voices if voice.language == language)

    def speak(self, text: str, *, language: str) -> None:
        self.spoken.append((text, language))

    def synthesize(self, text: str, *, language: str) -> AudioBuffer:
        self.spoken.append((text, language))
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(8_000)
            wav.writeframes(b"\x00\x00" * 80)
        return AudioBuffer(
            data=buffer.getvalue(),
            sample_rate=8_000,
            channels=1,
            sample_width=2,
            duration=0.01,
        )

    def stop(self) -> None:
        return None
