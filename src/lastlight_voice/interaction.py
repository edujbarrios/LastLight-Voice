# SPDX-License-Identifier: MPL-2.0
"""Voice interaction: microphone -> transcription -> response -> spoken audio.

The response callback is the seam for a future LastLight query adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .engine import SpeechEngine
from .errors import ConfigurationError
from .stt import VoskTranscriber

DEFAULT_ACKNOWLEDGEMENT = "Hello, I have received your message."


class Transcriber(Protocol):
    def listen_once(self, *, timeout_seconds: float = 10.0) -> str: ...


class Speaker(Protocol):
    def say(self, text: str) -> None: ...


@dataclass(frozen=True, slots=True)
class VoiceTurn:
    transcript: str
    response: str


class VoiceInteraction:
    """Perform one local microphone-to-speaker exchange, without writing WAV files.

    'responder' receives the transcript and returns text that will be spoken.
    The default response is fixed; pass a LastLight-backed callback later.
    """

    def __init__(
        self,
        *,
        language: str = "en",
        transcriber: Transcriber | None = None,
        speaker: Speaker | None = None,
        responder: Callable[[str], str] | None = None,
    ) -> None:
        self._transcriber = transcriber if transcriber is not None else VoskTranscriber(language=language)
        self._speaker = speaker if speaker is not None else SpeechEngine(language=language)
        self._responder = responder if responder is not None else lambda _text: DEFAULT_ACKNOWLEDGEMENT

    def interact_once(self, *, timeout_seconds: float = 10.0) -> VoiceTurn | None:
        """Speak a generic acknowledgement only if speech was recognized."""
        text = self._transcriber.listen_once(timeout_seconds=timeout_seconds)
        if not isinstance(text, str):
            raise ConfigurationError("The speech recognizer must return a text transcript.")
        transcript = text.strip()
        if not transcript:
            return None
        response = self._responder(transcript)
        if not isinstance(response, str) or not response.strip():
            raise ConfigurationError("The response handler must return non-empty text.")
        self._speaker.say(response)
        return VoiceTurn(transcript=transcript, response=response)
