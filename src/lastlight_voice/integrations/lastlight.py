# SPDX-License-Identifier: MPL-2.0

"""Small dependency-free adapter for LastLight query results."""

from __future__ import annotations

from typing import Protocol

from ..engine import SpeechEngine


class QueryResultLike(Protocol):
    """Subset of LastLight's QueryResult contract used by this integration."""

    accepted: bool
    passage: str | None


def speak_query_result(
    result: QueryResultLike,
    speech: SpeechEngine,
    *,
    refusal_text: str = "I don't have enough reliable local knowledge to answer that.",
) -> None:
    """Speak an accepted LastLight passage or a deterministic refusal.

    The adapter never generates or rewrites knowledge. LastLight remains the
    authority for whether a retrieved passage is safe to present as an answer.
    """
    if result.accepted and result.passage:
        speech.say(result.passage)
    else:
        speech.say(refusal_text)
