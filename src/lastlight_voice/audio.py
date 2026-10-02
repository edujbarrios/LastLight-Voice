# SPDX-License-Identifier: MPL-2.0

"""Audio container used by LastLight-Voice backends."""

from __future__ import annotations

import io
import wave
from dataclasses import dataclass
from pathlib import Path

from .errors import AudioError


@dataclass(frozen=True, slots=True)
class AudioBuffer:
    """Encoded audio plus lightweight metadata.

    v0.1 uses WAV as the portable interchange format. The container remains
    intentionally small so backends do not expose arbitrary raw byte blobs.
    """

    data: bytes
    format: str = "wav"
    sample_rate: int | None = None
    channels: int | None = None
    sample_width: int | None = None
    duration: float | None = None

    @classmethod
    def from_wav_bytes(cls, data: bytes) -> "AudioBuffer":
        """Build an audio buffer from WAV bytes and extract basic metadata."""
        if not isinstance(data, bytes) or not data:
            raise AudioError("WAV data must be non-empty bytes.")

        try:
            with wave.open(io.BytesIO(data), "rb") as wav:
                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                sample_rate = wav.getframerate()
                frame_count = wav.getnframes()
        except (EOFError, wave.Error) as exc:
            raise AudioError(f"Invalid WAV data: {exc}") from exc

        duration = frame_count / sample_rate if sample_rate > 0 else 0.0
        return cls(
            data=data,
            format="wav",
            sample_rate=sample_rate,
            channels=channels,
            sample_width=sample_width,
            duration=duration,
        )

    def save(self, path: str | Path) -> Path:
        """Write the encoded audio buffer to disk and return the output path."""
        output = Path(path)
        try:
            output.write_bytes(self.data)
        except OSError as exc:
            raise AudioError(f"Unable to write audio to {output}: {exc}") from exc
        return output
