# SPDX-License-Identifier: MPL-2.0
"""Optional, dependency-free bridge to the public LastLight.query() API.

LastLight-Voice never imports or installs LastLight automatically. The caller
passes an initialized LastLight instance, which remains the source of truth
for acceptance and the retrieved passage.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from ..engine import SpeechEngine
from ..errors import ConfigurationError


class QueryResultLike(Protocol):
    """Stable LastLight QueryResult fields required by the voice integration."""

    accepted: bool
    passage: str | None


class LastLightQueryLike(Protocol):
    """Public LastLight 0.3.x facade: query(text, *, top_k=3)."""

    def query(self, text: str, *, top_k: int = 3) -> QueryResultLike: ...


_DEFAULT_REFUSALS = {
    "en": "I don't have enough reliable local knowledge to answer that.",
    "es": "No tengo suficiente conocimiento local fiable para responder a eso.",
}


def query_result_text(
    result: QueryResultLike,
    *,
    language: str = "en",
    refusal_text: str | None = None,
) -> str:
    """Return ONLY an accepted passage; otherwise a local, fixed refusal.

    Never synthesize unsupported content or use low-confidence candidate
    passages when the upstream decision says the answer was rejected.
    """
    if result.accepted and isinstance(result.passage, str) and result.passage.strip():
        return result.passage.strip()
    if refusal_text is not None:
        if not isinstance(refusal_text, str) or not refusal_text.strip():
            raise ConfigurationError("Refusal text must be a non-empty string.")
        return refusal_text.strip()
    family = language.replace("_", "-").split("-", 1)[0].lower()
    return _DEFAULT_REFUSALS.get(family, _DEFAULT_REFUSALS["en"])


def make_lastlight_responder(
    knowledge: LastLightQueryLike,
    *,
    top_k: int = 3,
    language: str = "en",
    refusal_text: str | None = None,
) -> Callable[[str], str]:
    """Create a VoiceInteraction-compatible callback from an existing LastLight.

    Requires the *caller* to initialize LastLight with local knowledge first.
    No runtime import of 'lastlight', network call or hidden model dependency.
    """
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ConfigurationError("top_k must be a positive integer.")
    if not callable(getattr(knowledge, "query", None)):
        raise ConfigurationError("LastLight integration requires a query(text, *, top_k=...) method.")
    if refusal_text is not None and (
        not isinstance(refusal_text, str) or not refusal_text.strip()
    ):
        raise ConfigurationError("Refusal text must be a non-empty string.")

    def respond(transcript: str) -> str:
        if not isinstance(transcript, str) or not transcript.strip():
            raise ConfigurationError("LastLight query text must not be empty.")
        result = knowledge.query(transcript.strip(), top_k=top_k)
        return query_result_text(
            result,
            language=language,
            refusal_text=refusal_text,
        )

    return respond


def speak_query_result(
    result: QueryResultLike,
    speech: SpeechEngine,
    *,
    refusal_text: str | None = None,
) -> None:
    """Speak only accepted LastLight knowledge or a deterministic refusal."""
    speech.say(
        query_result_text(
            result,
            language=speech.language,
            refusal_text=refusal_text,
        )
    )
