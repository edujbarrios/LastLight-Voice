# SPDX-License-Identifier: MPL-2.0
"""Offline backend detection and diagnostics; no network checks."""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass

from .backends.dummy import DummyTTSBackend
from .backends.espeak import EspeakBackend
from .backends.piper import PiperBackend


@dataclass(frozen=True, slots=True)
class RuntimeDiagnostics:
    platform: str
    machine: str
    python: str
    espeak_available: bool
    espeak_executable: str | None
    supported_languages: tuple[str, ...] = ("en", "es")
    dummy_available: bool = True
    network_required: bool = False
    automatic_downloads: bool = False
    piper_available: bool = False
    piper_voices: tuple[str, ...] = ()

    @property
    def offline_ready(self) -> bool:
        """At least one real locally installed engine is usable."""
        return self.espeak_available or self.piper_available


def diagnose() -> RuntimeDiagnostics:
    """Inspect only local executable/model availability (never download)."""
    espeak = EspeakBackend()
    piper = PiperBackend()
    return RuntimeDiagnostics(
        platform=platform.system(),
        machine=platform.machine(),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        espeak_available=espeak.available(),
        espeak_executable=espeak.executable,
        piper_available=piper.available(),
        piper_voices=tuple(v.id for v in piper.voices()),
        dummy_available=DummyTTSBackend().available(),
    )
