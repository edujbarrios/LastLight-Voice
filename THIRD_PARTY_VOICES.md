# Third-party voice notices and publication review

The **LastLight-Voice** application code is MPL-2.0. The optional neural voice
`en_US-amy-low` is **not authored by LastLight-Voice**.

## Attribution

- **Voice:** `en_US-amy-low`, 16 kHz, single-speaker, Piper Voices (Rhasspy).
- **Voice repository:** https://huggingface.co/rhasspy/piper-voices
- **Version pinned for packaging:** `v1.0.0`.
- **Voice maintainer / upstream contributor:** Michael Hansen (`synesthesiam`)
  and the Rhasspy/Piper voice contributors. No endorsement is implied.
- **Source model card:** https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/low/MODEL_CARD
- **Upstream data reference:** MycroftAI Mimic 3 Voices,
  https://github.com/MycroftAI/mimic3-voices (repository marked CC BY-SA 4.0).
- **Training provenance:** Piper's Amy low model card states that this voice was
  *fine-tuned from the U.S. English Ryan low-quality voice*.
- **Inference engine:** `piper-tts` (OHF-Voice/Piper contributors), **GPL-3.0-or-later**;
  installed as a separate, optional Python dependency, not copied into this
  project's source distribution. See https://github.com/OHF-Voice/piper1-gpl.

## Licensing position requested by the project

The Hugging Face **collection-level** `rhasspy/piper-voices` README declares
`license: mit` and the website displays **MIT**. LastLight-Voice identifies
that public metadata as the basis for considering Amy in its packaging workflow,
retains attribution and ships the original `MODEL_CARD` with any voice wheel.

However, **the `en_US-amy-low` model card does not explicitly license the model
weights under MIT**; it points to Mimic 3 datasets and the Ryan fine-tuning base.
Piper's current maintainers explicitly state that the collection label is not
an independent license grant for each voice, and list Amy/Ryan among voices with
unresolved/restrictive dataset rights. Therefore **MIT coverage of Amy's trained
weights and commercial/redistribution rights have not been established**.

LastLight-Voice did not create, collect, curate or train on the source recordings;
training data and voice recordings were supplied by third parties. This is a
statement of provenance and non-endorsement, **not a warranty, legal immunity,
release from applicable duties, or a replacement for upstream license terms**.
The project does not claim rights it cannot verify.

**Publication gate:** The build tool may stage an *internal review wheel* only
when invoked explicitly with `--acknowledge-licenses`. This flag records a
human review decision; it does not establish legal permission. Before any
public upload, the maintainer must confirm the model's redistribution rights,
review the Ryan base, preserve notices, and re-check the licensing and PyPI
requirements. **No upload action is included in this repository.**

Sources:
- https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/README.md
- https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/low/MODEL_CARD
- https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/LICENSING.md
- https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/COMMERCIAL_USE.md
- https://github.com/MycroftAI/mimic3-voices
