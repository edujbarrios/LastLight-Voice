# Optional LastLight integration

The original [edujbarrios/lastlight](https://github.com/edujbarrios/lastlight)
exports the stable `LastLight` Python facade, with
`query(text, *, top_k=3) -> QueryResult`. The result exposes
`accepted: bool` and `passage: str | None`.

LastLight-Voice uses **only those public fields**. It does not import LastLight
internals, alter the retrieval decision or add `lastlight` to its default
dependencies.

## Voice-driven retrieval

Install LastLight separately and provide a local LastLight knowledge pack.
Then:

```python
from lastlight import LastLight
from lastlight_voice import VoiceInteraction
from lastlight_voice.integrations import make_lastlight_responder

knowledge = LastLight("my-knowledge-pack.zip", strategy="lexical")
session = VoiceInteraction(responder=make_lastlight_responder(knowledge, top_k=3))
turn = session.interact_once(timeout_seconds=12)
```

The pipeline is:

```text
microphone → Vosk transcript → LastLight.query(transcript)
  → accepted passage OR fixed refusal → Piper speech
```

The adapter **never speaks a candidate passage from a rejected LastLight
query**. If `accepted` is false or `passage` is missing, it returns a
deterministic refusal. LastLight errors propagate rather than being disguised
as successful answers. Nothing is sent to a remote endpoint.

## Options

`make_lastlight_responder(knowledge, top_k=3, language="en", refusal_text=None)`
returns a standard `Callable[[str], str]`. It can be supplied to any
`VoiceInteraction`. The earlier
`speak_query_result(result, speech)` API is retained.

The regular `lastlight-voice interact` command still uses the fixed
acknowledgement unless a responder is provided in Python; the CLI is not
silently connected to a knowledge pack. Future UI/CLI integrations can choose
the pack and strategy explicitly.

## Compatibility boundary

Checked against the public `LastLight.query` / `QueryResult` contract of
the original project. The adapter has no hard dependency on a particular
LastLight release or a specific pack layout. An optional CI smoke test uses
LastLight 0.3.1 and the original example pack to detect contract regressions.
English Vosk/Piper are currently bundled; other languages can be added later.
