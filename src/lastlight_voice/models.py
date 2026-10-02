# SPDX-License-Identifier: MPL-2.0

"""Small immutable data models used by the public API."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Voice:
    """A speech voice exposed by a backend."""

    id: str
    name: str
    language: str
    backend: str


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    """Capabilities advertised by a TTS backend."""

    name: str
    offline: bool = True
    supports_synthesis: bool = True
    supports_playback: bool = True
    supports_stop: bool = False
