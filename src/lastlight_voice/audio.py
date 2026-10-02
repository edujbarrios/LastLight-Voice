# SPDX-License-Identifier: MPL-2.0

"""Audio container used by LastLight-Voice backends."""

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

    def save(self, path: str | Path) -> Path:
        """Write the encoded audio buffer to disk and return the output path."""
        output = Path(path)
        try:
            output.write_bytes(self.data)
        except OSError as exc:
            raise AudioError(f"Unable to write audio to {output}: {exc}") from exc
        return output
