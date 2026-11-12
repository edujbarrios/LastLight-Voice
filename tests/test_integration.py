# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

import pytest

from lastlight_voice import ConfigurationError, SpeechEngine, VoiceInteraction
from lastlight_voice.backends import DummyTTSBackend
from lastlight_voice.integrations import (
    make_lastlight_responder,
    query_result_text,
    speak_query_result,
)


@dataclass
class Result:
    accepted: bool
    passage: str | None


class FakeKnowledge:
    def __init__(self, result: Result):
        self.result = result
        self.calls: list[tuple[str, int]] = []

    def query(self, text: str, *, top_k: int = 3) -> Result:
        self.calls.append((text, top_k))
        return self.result


class FakeMic:
    def listen_once(self, *, timeout_seconds: float = 10.0) -> str:
        return "where can i find clean water"


class FakeSpeaker:
    def __init__(self):
        self.spoken: list[str] = []

    def say(self, text: str) -> None:
        self.spoken.append(text)


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


def test_accepted_passage_is_only_knowledge_spoken() -> None:
    knowledge = FakeKnowledge(Result(True, "Use the verified local passage."))
    callback = make_lastlight_responder(knowledge, top_k=2)
    assert callback("  where is the shelter?  ") == "Use the verified local passage."
    assert knowledge.calls == [("where is the shelter?", 2)]


@pytest.mark.parametrize("result", [Result(False, "UNSAFE CANDIDATE"), Result(True, None), Result(True, "  ")])
def test_refused_or_empty_knowledge_never_spoken(result: Result) -> None:
    callback = make_lastlight_responder(FakeKnowledge(result))
    assert callback("question") == "I don't have enough reliable local knowledge to answer that."


def test_custom_refusal_and_spanish() -> None:
    assert query_result_text(Result(False, "Ignore this"), language="es") == (
        "No tengo suficiente conocimiento local fiable para responder a eso."
    )
    responder = make_lastlight_responder(
        FakeKnowledge(Result(False, None)),
        language="es",
        refusal_text="No dispongo de pruebas suficientes.",
    )
    assert responder("consulta") == "No dispongo de pruebas suficientes."


def test_full_interaction_uses_lastlight_callback_without_wav_file() -> None:
    knowledge = FakeKnowledge(Result(True, "Collect water only from a verified safe source."))
    speaker = FakeSpeaker()
    interaction = VoiceInteraction(
        transcriber=FakeMic(),
        speaker=speaker,
        responder=make_lastlight_responder(knowledge),
    )
    turn = interaction.interact_once()
    assert turn is not None
    assert turn.transcript == "where can i find clean water"
    assert turn.response == "Collect water only from a verified safe source."
    assert speaker.spoken == [turn.response]
    assert knowledge.calls == [(turn.transcript, 3)]


def test_lastlight_refusal_is_spoken_in_interaction() -> None:
    speaker = FakeSpeaker()
    interaction = VoiceInteraction(
        transcriber=FakeMic(),
        speaker=speaker,
        responder=make_lastlight_responder(FakeKnowledge(Result(False, "untrusted text"))),
    )
    turn = interaction.interact_once()
    assert turn is not None
    assert "untrusted text" not in turn.response
    assert speaker.spoken == [turn.response]


@pytest.mark.parametrize("top_k", [0, -1, 2.5, True])
def test_invalid_top_k_fails_early(top_k: object) -> None:
    with pytest.raises(ConfigurationError, match="top_k"):
        make_lastlight_responder(FakeKnowledge(Result(True, "Passage")), top_k=top_k)


def test_missing_query_method_fails_early() -> None:
    with pytest.raises(ConfigurationError, match="query"):
        make_lastlight_responder(object())


def test_empty_question_never_queries() -> None:
    knowledge = FakeKnowledge(Result(True, "Passage"))
    callback = make_lastlight_responder(knowledge)
    with pytest.raises(ConfigurationError, match="empty"):
        callback("   ")
    assert knowledge.calls == []


def test_upstream_errors_are_not_silenced() -> None:
    class BrokenKnowledge:
        def query(self, text: str, *, top_k: int = 3) -> Result:
            raise RuntimeError("knowledge pack not available")

    with pytest.raises(RuntimeError, match="pack not available"):
        make_lastlight_responder(BrokenKnowledge())("question")
