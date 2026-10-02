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
    dummy_available: bool = True
    network_required: bool = False

    @property
    def offline_ready(self) -> bool:
        return self.espeak_available


def diagnose() -> RuntimeDiagnostics:
    """Inspect only local runtime state. This function never accesses a network."""
    return RuntimeDiagnostics(
        platform=platform.system(),
        machine=platform.machine(),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        espeak_available=EspeakBackend().available(),
        dummy_available=DummyTTSBackend().available(),
    )
