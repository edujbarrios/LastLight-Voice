# Piper Amy low — source assets for package review

This directory contains the upstream voice `en_US-amy-low` from
[rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/en/en_US/amy/low),
at the pinned `v1.0.0` snapshot. The model is the work of the Piper/Rhasspy
community; credit Michael Hansen (`synesthesiam`) and upstream dataset
contributors. The corresponding `MODEL_CARD` must travel with any distribution.

Model SHA-256 (upstream Hugging Face file page):
`a5a91abb7de0f104358a25aded480ddacf1ff0762886325886ec406a2e86aab3`

The collection is marked **MIT**, but the individual Amy `MODEL_CARD`
does not expressly establish the model's weight redistribution rights.
Amy is fine-tuned from Ryan low. See
[the upstream dataset and authorship notice](../../THIRD_PARTY_VOICES.md)
and [release review checklist](../../docs/PIPER_RELEASE_REVIEW.md).
The absence of control over training data does not eliminate third-party
license obligations. This is not a legal warranty.

These source assets are **not loaded by the core Python distribution**.
Once distribution rights are reviewed, build an optional voice wheel:
```bash
python scripts/package_piper_voices.py --voice en_US-amy-low \
  --models-dir voice_assets --prepare-packs --acknowledge-licenses
```
The build is local only and makes no PyPI upload.
