# SPDX-License-Identifier: MPL-2.0

"""Public API for LastLight-Voice."""

from .audio import AudioBuffer
from .engine import SpeechEngine
from .errors import (
    AudioError,
    BackendError,
    BackendUnavailableError,
    ConfigurationError,
    LastLightVoiceError,
    SynthesisError,
)
from .models import BackendCapabilities, Voice

__all__ = [
    "AudioBuffer",
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
