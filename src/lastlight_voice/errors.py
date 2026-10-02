# SPDX-License-Identifier: MPL-2.0

"""Exception hierarchy for LastLight-Voice."""


class LastLightVoiceError(Exception):
    """Base exception for LastLight-Voice."""


class ConfigurationError(LastLightVoiceError):
    """Raised when runtime configuration is invalid."""


class BackendError(LastLightVoiceError):
    """Raised when a speech backend fails."""


class BackendUnavailableError(BackendError):
    """Raised when a requested backend is not available locally."""


class SynthesisError(BackendError):
    """Raised when text-to-speech synthesis fails."""


class AudioError(LastLightVoiceError):
    """Raised when audio data cannot be written or handled."""
