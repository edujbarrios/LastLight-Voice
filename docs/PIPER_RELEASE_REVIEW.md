# Piper Amy — release checklist (review only)

The default `lastlight-voice` distribution now **includes** the Piper
`en_US-amy-low` model and automatically installs the `piper-tts` runtime.
There is no extra, separate language wheel, manual configuration or runtime
model download required for the default English voice.

## Build and test

```bash
python -m pip install -e ".[dev]"
pytest
python -m build
python -m pip install --force-reinstall dist/lastlight_voice-0.1.0-*.whl
lastlight-voice synthesize --language en "Stay safe." voice.wav
```

Verify the built wheel and source archive include these files:

- `lastlight_voice/voices/en_US-amy-low/en_US-amy-low.onnx` (63,104,526 bytes)
- `lastlight_voice/voices/en_US-amy-low/en_US-amy-low.onnx.json` (4,164 bytes)
- `lastlight_voice/voices/en_US-amy-low/en_US-amy-low.MODEL_CARD` (273 bytes)
- `lastlight_voice/voices/THIRD_PARTY_VOICES.md` (attribution)

Model SHA-256:
`a5a91abb7de0f104358a25aded480ddacf1ff0762886325886ec406a2e86aab3`.

The above build is for **local review**. For a real offline end-to-end test,
install the package and dependencies, disconnect the network, and synthesize.
Existing mocked backend tests cannot substitute for that real voice test.

## Before any PyPI upload

- [ ] Review written rights for **Amy**, its Ryan low training base and original
  data; the collection-level MIT label alone does not resolve those rights.
- [ ] Confirm the GPL-3.0-or-later obligations of the now-required Piper runtime.
- [ ] Check wheel and sdist contents, integrity, PyPI per-file size and Windows,
  macOS, Linux, ARM64 / Raspberry Pi compatibility.
- [ ] Test installation from a wheel in a clean virtual environment and
  synthesize a WAV **with Internet disconnected**.
- [ ] Run `pytest`, `python -m build` and `twine check dist/*`.
- [ ] Review version number and changelog with the maintainer.

**No publishing credentials, PyPI uploads or publishing workflows are included.**
See [THIRD_PARTY_VOICES.md](../THIRD_PARTY_VOICES.md).
