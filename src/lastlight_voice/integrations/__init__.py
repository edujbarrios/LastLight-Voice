# SPDX-License-Identifier: MPL-2.0

"""Optional integrations with external local-first projects."""

from .lastlight import (
    LastLightQueryLike,
    QueryResultLike,
    make_lastlight_responder,
    query_result_text,
    speak_query_result,
)

__all__ = [
    "LastLightQueryLike",
    "QueryResultLike",
    "make_lastlight_responder",
    "query_result_text",
    "speak_query_result",
]
