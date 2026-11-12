# SPDX-License-Identifier: MPL-2.0
"""Local diagnostics should not contact a server or fabricate available voices."""

from lastlight_voice.detection import RuntimeDiagnostics


def test_offline_ready_when_piper_is_installed():
    status = RuntimeDiagnostics(platform="Linux", machine="aarch64", python="3.11.0",
                                espeak_available=False, espeak_executable=None,
                                piper_available=True, piper_voices=("en_US-amy-low",))
    assert status.offline_ready
    assert not status.network_required
    assert not status.automatic_downloads


def test_offline_unavailable_without_both_real_backends():
    status = RuntimeDiagnostics(platform="Linux", machine="x86_64", python="3.11.0",
                                espeak_available=False, espeak_executable=None)
    assert not status.offline_ready
