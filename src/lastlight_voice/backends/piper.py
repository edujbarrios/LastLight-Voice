# SPDX-License-Identifier: MPL-2.0
"""Offline Piper CLI backend using bundled local voices; no runtime downloads."""

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
    """Neural TTS through the installed Piper CLI and local voice catalog."""

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
            raise BackendUnavailableError("Piper is unavailable in this Python environment.")
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
        """Speak through local speakers without requiring a user-provided output WAV."""
        audio = self.synthesize(text, language=language)
        # Use the same PortAudio stack as microphone capture when possible.
        # This avoids requiring ffplay/aplay for a normal pip installation.
        try:
            import io
            import wave
            import sounddevice as sd

            with wave.open(io.BytesIO(audio.data), "rb") as wav:
                if wav.getsampwidth() != 2 or wav.getcomptype() != "NONE":
                    raise ValueError("Unsupported Piper WAV sample format")
                with sd.RawOutputStream(
                    samplerate=wav.getframerate(),
                    channels=wav.getnchannels(),
                    dtype="int16",
                ) as output:
                    output.write(wav.readframes(wav.getnframes()))
            return
        except Exception as audio_error:
            # PortAudio device failures are implementation-specific exceptions.
            # Fall back to native local players; never send audio to a service.
            fallback_error = audio_error

        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(audio.data, winsound.SND_MEMORY)
                return
            except (OSError, RuntimeError) as exc:
                raise SynthesisError(f"Unable to play speech on Windows: {exc}") from exc
        player = shutil.which("afplay" if sys.platform == "darwin" else "aplay")
        args = [player] if player else None
        if args is None:
            ffplay = shutil.which("ffplay")
            if ffplay:
                args = [ffplay, "-nodisp", "-autoexit", "-loglevel", "error"]
        if args is None:
            raise BackendUnavailableError(
                "No usable audio output device or local player found. "
                f"Sounddevice error: {fallback_error}"
            )
        with tempfile.TemporaryDirectory(prefix="lastlight-player-") as temp:
            wav_path = Path(temp) / "speech.wav"
            wav_path.write_bytes(audio.data)
            try:
                subprocess.run([*args, str(wav_path)], check=True, timeout=self._timeout, capture_output=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
                raise SynthesisError(f"Local audio playback failed: {exc}") from exc

    def stop(self) -> None:
        # CLI speech is blocking; there is no silent stop fallback.
        return None
