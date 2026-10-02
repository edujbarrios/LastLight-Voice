# SPDX-License-Identifier: MPL-2.0

"""Offline backend detection and diagnostics."""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass

from .backends.dummy import DummyTTSBackend
from .backends.espeak import EspeakBackend


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

    @property
    def offline_ready(self) -> bool:
        """Return whether a real local speech backend is ready to use."""
        return self.espeak_available


def diagnose() -> RuntimeDiagnostics:
    """Inspect only local runtime state. This function never accesses a network."""
    espeak = EspeakBackend()
    return RuntimeDiagnostics(
        platform=platform.system(),
        machine=platform.machine(),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        espeak_available=espeak.available(),
        espeak_executable=espeak.executable,
        dummy_available=DummyTTSBackend().available(),
    )
