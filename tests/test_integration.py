# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

from lastlight_voice import SpeechEngine
from lastlight_voice.backends import DummyTTSBackend
from lastlight_voice.integrations import speak_query_result


@dataclass
class Result:
    accepted: bool
    passage: str | None


def test_lastlight_adapter_speaks_only_accepted_passage() -> None:
    backend = DummyTTSBackend()
    speech = SpeechEngine(backend=backend)

    speak_query_result(Result(True, "Boil the water."), speech)

    assert backend.spoken[-1][0] == "Boil the water."


def test_lastlight_adapter_speaks_refusal_for_rejected_result() -> None:
    backend = DummyTTSBackend()
    speech = SpeechEngine(backend=backend)

    speak_query_result(Result(False, None), speech)

    assert "enough reliable local knowledge" in backend.spoken[-1][0]
