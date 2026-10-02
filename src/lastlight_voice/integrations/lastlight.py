# SPDX-License-Identifier: MPL-2.0

"""Small dependency-free adapter for LastLight query results."""

from __future__ import annotations

from typing import Protocol

from ..engine import SpeechEngine


class QueryResultLike(Protocol):
    """Subset of LastLight's QueryResult contract used by this integration."""

    accepted: bool
    passage: str | None


_DEFAULT_REFUSALS = {
    "en": "I don't have enough reliable local knowledge to answer that.",
    "es": "No tengo suficiente conocimiento local fiable para responder a eso.",
}


def speak_query_result(
    result: QueryResultLike,
    speech: SpeechEngine,
    *,
    refusal_text: str | None = None,
) -> None:
    """Speak an accepted LastLight passage or a deterministic local refusal.

    The adapter never generates or rewrites knowledge. LastLight remains the
    authority for whether a retrieved passage is safe to present as an answer.
    """
    if result.accepted and result.passage:
        speech.say(result.passage)
        return

    speech.say(refusal_text or _DEFAULT_REFUSALS[speech.language])
