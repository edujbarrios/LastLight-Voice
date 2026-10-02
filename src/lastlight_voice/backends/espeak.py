# SPDX-License-Identifier: MPL-2.0

"""Low-resource eSpeak NG backend."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from ..audio import AudioBuffer
from ..errors import BackendUnavailableError, ConfigurationError, SynthesisError
from ..models import BackendCapabilities, Voice


class EspeakBackend:
    """Offline TTS through a locally installed ``espeak-ng`` executable."""

    name = "espeak-ng"

    def __init__(self, *, timeout: float = 30.0, executable: str | None = None) -> None:
        if timeout <= 0:
            raise ConfigurationError("eSpeak NG timeout must be greater than zero.")
        self._timeout = timeout
        self._executable = executable or shutil.which("espeak-ng")

    @property
    def executable(self) -> str | None:
        """Return the resolved executable path/name, if available."""
        return self._executable

    def available(self) -> bool:
        return self._executable is not None

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(name=self.name, supports_stop=False)

    def voices(self, language: str | None = None) -> Sequence[Voice]:
        voices = (
            Voice("en", "eSpeak NG English", "en", self.name),
            Voice("es", "eSpeak NG Spanish", "es", self.name),
        )
        if language is None:
            return voices
        return tuple(voice for voice in voices if voice.language == language)

    def speak(self, text: str, *, language: str) -> None:
        executable = self._require_executable()
        self._run([executable, "-v", language, "--stdin"], text=text)

    def synthesize(self, text: str, *, language: str) -> AudioBuffer:
        executable = self._require_executable()
        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
                path = Path(handle.name)
            self._run(
                [executable, "-v", language, "-w", str(path), "--stdin"],
                text=text,
            )
            return AudioBuffer.from_wav_bytes(path.read_bytes())
        except OSError as exc:
            raise SynthesisError(f"Unable to read synthesized audio: {exc}") from exc
        finally:
            if path is not None:
                path.unlink(missing_ok=True)

    def stop(self) -> None:
        # v0.1 synthesis is blocking; interruption will require a managed Popen
        # lifecycle in a later release.
        return None

    def _require_executable(self) -> str:
        if self._executable is None:
            raise BackendUnavailableError(
                "eSpeak NG is not installed or 'espeak-ng' is not on PATH. "
                "Install it using your operating system package manager."
            )
        return self._executable

    def _run(self, command: list[str], *, text: str) -> None:
        try:
            subprocess.run(
                command,
                check=True,
                timeout=self._timeout,
                input=text,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise SynthesisError(
                f"eSpeak NG exceeded the {self._timeout:g}s timeout."
            ) from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip()
            suffix = f": {detail}" if detail else ""
            raise SynthesisError(
                f"eSpeak NG failed with exit code {exc.returncode}{suffix}"
            ) from exc
