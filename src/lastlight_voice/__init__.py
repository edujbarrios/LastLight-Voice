# SPDX-License-Identifier: MPL-2.0

"""Public API for LastLight-Voice."""

from .audio import AudioBuffer
from .interaction import VoiceInteraction, VoiceTurn
from .stt import VoskTranscriber
from .engine import SpeechEngine
from .errors import (
    AudioError,
    BackendError,
    BackendUnavailableError,
    ConfigurationError,
    LastLightVoiceError,
    SynthesisError,
    SpeechRecognitionError,
)
from .models import BackendCapabilities, Voice

__all__ = [
    "AudioBuffer",
    "VoiceInteraction",
    "VoiceTurn",
    "VoskTranscriber",
    "SpeechRecognitionError",
    "AudioError",
    "BackendCapabilities",
    "BackendError",
    "BackendUnavailableError",
    "ConfigurationError",
    "LastLightVoiceError",
    "SpeechEngine",
    "SynthesisError",
    "Voice",
]

__version__ = "0.1.0"
