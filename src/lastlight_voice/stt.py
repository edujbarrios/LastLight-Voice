# SPDX-License-Identifier: MPL-2.0
"""Offline English speech recognition from a bundled Vosk model and microphone.

The microphone audio and transcripts are never uploaded or written to disk.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

from .errors import BackendUnavailableError, ConfigurationError, SpeechRecognitionError


def _load_catalog(catalog_path: str | Path | None = None) -> dict:
    if catalog_path is None:
        path = Path(__file__).resolve().parent / "stt_catalog.json"
    else:
        path = Path(catalog_path)
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
        if catalog["schema_version"] != 1 or not isinstance(catalog["models"], list):
            raise ValueError("unsupported STT catalog")
        return catalog
    except (OSError, KeyError, ValueError, TypeError) as exc:
        raise ConfigurationError(f"Invalid local STT model catalog: {exc}") from exc


class VoskTranscriber:
    """Transcribe one English utterance from a local microphone, without a cloud API.

    Future languages can be enabled by adding a model to stt_catalog.json.
    """

    def __init__(
        self,
        *,
        language: str = "en",
        model_dir: str | Path | None = None,
        device: int | str | None = None,
        catalog_path: str | Path | None = None,
    ) -> None:
        if not isinstance(language, str) or not language.strip():
            raise ConfigurationError("STT language must be a language code.")
        family = language.strip().replace("_", "-").split("-", 1)[0].lower()
        catalog = _load_catalog(catalog_path)
        matches = [x for x in catalog["models"] if x.get("language") == family]
        if not matches:
            raise ConfigurationError(
                f"No bundled speech recognition model for {language!r}. "
                "The default voice-interaction language is English."
            )
        spec = matches[0]
        identifier = spec.get("id", "")
        if (
            not isinstance(identifier, str)
            or not identifier
            or "/" in identifier
            or "\\" in identifier
            or identifier in {".", ".."}
        ):
            raise ConfigurationError("Invalid STT model identifier.")
        required = spec.get("required_files")
        if not isinstance(required, list) or not required or any(
            not isinstance(x, str)
            or x.startswith("/")
            or "\\" in x
            or any(p in {"", ".", ".."} for p in x.split("/"))
            for x in required
        ):
            raise ConfigurationError("Invalid STT model file list.")
        samplerate = spec.get("sample_rate")
        if not isinstance(samplerate, int) or samplerate <= 0:
            raise ConfigurationError("Invalid STT sample rate.")
        self.language = family
        self.device = device
        self.sample_rate = samplerate
        self.model_dir = (
            Path(model_dir).expanduser()
            if model_dir is not None
            else Path(__file__).resolve().parent / "stt_models" / identifier
        )
        self._required = tuple(required)

    def model_available(self) -> bool:
        return all((self.model_dir / filename).is_file() for filename in self._required)

    def available(self) -> bool:
        if not self.model_available():
            return False
        if importlib.util.find_spec("vosk") is None:
            return False
        try:
            import sounddevice
        except (ImportError, OSError):
            # Linux often needs the system libportaudio2 package.
            return False
        return True

    def listen_once(self, *, timeout_seconds: float = 10.0) -> str:
        """Record at most timeout_seconds of microphone audio, return a transcript.

        Stops on Vosk's first complete nonempty utterance. No audio file is saved.
        """
        if not 0.25 <= timeout_seconds <= 120:
            raise ConfigurationError("Listening timeout must be between 0.25 and 120 seconds.")
        if not self.model_available():
            raise BackendUnavailableError(
                f"Bundled speech recognition model is missing at {self.model_dir}."
            )
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer, Model
        except (ImportError, OSError) as exc:
            raise BackendUnavailableError(
                "Microphone transcription requires the installed vosk and sounddevice packages."
            ) from exc
        # Match the recording device's native rate; Vosk can resample internally.
        # Many microphones do not accept a forced 16 kHz input stream.
        try:
            sample_rate = int(sd.query_devices(self.device, "input")["default_samplerate"])
            if sample_rate <= 0:
                raise ValueError("Invalid microphone sample rate")
        except (sd.PortAudioError, KeyError, TypeError, ValueError, OSError):
            sample_rate = self.sample_rate

        try:
            model = Model(str(self.model_dir))
            recognizer = KaldiRecognizer(model, sample_rate)
        except (OSError, RuntimeError, ValueError) as exc:
            raise SpeechRecognitionError(f"Cannot initialize offline recognizer: {exc}") from exc

        def recognized(payload: str) -> str:
            try:
                result = json.loads(payload)
                text = result.get("text", "")
                if isinstance(text, str):
                    return text.strip()
            except (TypeError, ValueError):
                pass
            raise SpeechRecognitionError("Vosk returned malformed transcription data.")

        frames_per_block = max(1, sample_rate // 4)
        try:
            with sd.RawInputStream(
                samplerate=sample_rate,
                blocksize=frames_per_block,
                device=self.device,
                channels=1,
                dtype="int16",
            ) as stream:
                deadline = time.monotonic() + timeout_seconds
                while time.monotonic() < deadline:
                    chunk, _overflow = stream.read(frames_per_block)
                    if recognizer.AcceptWaveform(bytes(chunk)):
                        text = recognized(recognizer.Result())
                        if text:
                            return text
            return recognized(recognizer.FinalResult())
        except sd.PortAudioError as exc:
            raise BackendUnavailableError(
                "Cannot access an input microphone. Check microphone permissions, "
                "PortAudio and the selected recording device."
            ) from exc
        except OSError as exc:
            raise SpeechRecognitionError(f"Microphone recording failed: {exc}") from exc
