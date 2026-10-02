# SPDX-License-Identifier: MPL-2.0

"""Built-in TTS backends."""

from .base import TTSBackend
from .dummy import DummyTTSBackend
from .espeak import EspeakBackend

__all__ = ["DummyTTSBackend", "EspeakBackend", "TTSBackend"]
