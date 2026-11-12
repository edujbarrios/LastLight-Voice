# SPDX-License-Identifier: MPL-2.0
"""Opt-in offline Piper CLI backend; never downloads or uses the network."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from ..audio import AudioBuffer
from ..errors import BackendUnavailableError, ConfigurationError, SynthesisError
from ..models import BackendCapabilities, Voice
from ..piper_voices import PiperVoiceSpec, find_local_model, load_piper_catalog


class PiperBackend:
    """Neural TTS through locally installed Piper and an independently managed voice pack."""

    name = "piper"

    def __init__(
        self,
        *,
        executable: str | None = None,
        models_dir: str | Path | None = None,
        catalog_path: str | Path | None = None,
        timeout: float = 120.0,
    ) -> None:
        if timeout <= 0:
            raise ConfigurationError("Piper timeout must be greater than zero.")
        if executable:
            self._executable = shutil.which(executable)
        else:
            # The pip console script belongs to the *same* Python environment,
            # even when the environment's bin/ directory is absent from PATH.
            local_piper = Path(sys.executable).parent / (
                "piper.exe" if sys.platform == "win32" else "piper"
            )
            self._executable = (
                str(local_piper) if local_piper.is_file() else shutil.which("piper")
            )
        self._models_dir = models_dir
        self._specs: tuple[PiperVoiceSpec, ...] = load_piper_catalog(catalog_path)
        self._timeout = timeout

    def _local(self) -> list[tuple[PiperVoiceSpec, Path]]:
        return [(spec, path) for spec in self._specs
                if (path := find_local_model(spec, self._models_dir)) is not None]

    def available(self) -> bool:
        return self._executable is not None and bool(self._local())

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name=self.name, supports_stop=False,
            supports_playback=(sys.platform == "win32" or any(
                shutil.which(cmd) for cmd in ("afplay", "aplay", "ffplay")
            )),
        )

    def voices(self, language: str | None = None) -> Sequence[Voice]:
        return tuple(
            Voice(spec.id, spec.id, spec.language, self.name)
            for spec, _ in self._local()
            if language is None or spec.language == language
        )

    def synthesize(self, text: str, *, language: str) -> AudioBuffer:
        if not self._executable:
            raise BackendUnavailableError("Piper is not installed: pip install lastlight-voice[piper]")
        available = [(spec, path) for spec, path in self._local() if spec.language == language]
        if not available:
            raise BackendUnavailableError(f"No local Piper voice installed for {language!r}.")
        _spec, model = available[0]
        with tempfile.TemporaryDirectory(prefix="lastlight-piper-") as temp:
            wav = Path(temp) / "speech.wav"
            command = [
                self._executable, "--model", str(model), "--config",
                str(model.with_name(model.name + ".json")),
                "--output_file", str(wav),
            ]
            try:
                subprocess.run(
                    command, input=text + "\n", text=True, capture_output=True,
                    timeout=self._timeout, check=True,
                )
                return AudioBuffer.from_wav_bytes(wav.read_bytes())
            except subprocess.TimeoutExpired as exc:
                raise SynthesisError(f"Piper timed out after {self._timeout:g} seconds.") from exc
            except subprocess.CalledProcessError as exc:
                raise SynthesisError(f"Piper failed: {(exc.stderr or '').strip()}") from exc
            except OSError as exc:
                raise SynthesisError(f"Cannot read Piper output: {exc}") from exc

    def speak(self, text: str, *, language: str) -> None:
        audio = self.synthesize(text, language=language)
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(audio.data, winsound.SND_MEMORY)
            return
        player = shutil.which("afplay" if sys.platform == "darwin" else "aplay")
        args = [player] if player else None
        if not args:
            ffplay = shutil.which("ffplay")
            if ffplay:
                args = [ffplay, "-nodisp", "-autoexit", "-loglevel", "error"]
        if args is None:
            raise BackendUnavailableError(
                "No local audio player found (aplay, afplay or ffplay); WAV synthesis is available."
            )
        with tempfile.TemporaryDirectory(prefix="lastlight-player-") as temp:
            output = Path(temp) / "speech.wav"
            output.write_bytes(audio.data)
            try:
                subprocess.run([*args, str(output)], check=True, timeout=self._timeout, capture_output=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
                raise SynthesisError(f"Local audio playback failed: {exc}") from exc

    def stop(self) -> None:
        # CLI speech is blocking; there is no silent stop fallback.
        return None
