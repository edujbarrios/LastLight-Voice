# Piper Amy voice — internal release checklist (no upload)

This is a **review candidate**, not evidence of a license grant. LastLight-Voice
keeps its main MPL-2.0 package lightweight. Models are distributed only as
separate optional language wheels; today the catalog contains **English Amy low
only**. Future languages can be added to `piper_catalog.json` and packaged
using the same build tool without changing `SpeechEngine` or `PiperBackend`.

## Setup and local smoke test

```bash
python -m pip install -e '.[dev,piper]'
python scripts/package_piper_voices.py --list
# A human must review THIRD_PARTY_VOICES.md before the next command.
python scripts/package_piper_voices.py --voice en_US-amy-low \
    --models-dir voice_assets --prepare-packs --acknowledge-licenses
python -m pip wheel --no-deps --wheel-dir dist/review-wheels \
    dist/voice-pack-sources/lastlight-voice-model-en-en_US-amy-low
python -m pip install dist/review-wheels/lastlight_voice_model_en-*.whl
lastlight-voice voices --backend piper --language en
lastlight-voice synthesize 'Knowledge is available offline.' voice.wav \
    --backend piper --language en
```

This review branch already contains verified Amy voice assets at
`voice_assets/en_US-amy-low/`. No network access is needed for the commands
above once dependencies have been installed. `--download` is optional for
provisioning missing assets from upstream, and never runs at inference time.
Piper CLI synthesis and model lookup never download anything. To test offline:
install Piper and the voice wheel, disconnect the network, then run the
`synthesize` command again. The default eSpeak NG backend is preserved for
backward compatibility and low-RAM setups.

The optional wheel can be built from the GitHub-tracked weights without any
new model download. The voice wheel bundles `en_US-amy-low.onnx`, its `.onnx.json`, the upstream
`MODEL_CARD`, and `THIRD_PARTY_VOICES.md`. The main code package carries none
of these large model files. The inference engine is provided by optional
`piper-tts` (GPL-3.0-or-later), installed separately. We have not verified a
real Piper inference in the development container; the integration test uses a
mocked executable to check subprocess arguments, WAV parsing and offline-only
behavior.

## Before uploading anything to PyPI

**Note:** The full model is already present in the publicly accessible review
branch, as requested. This is a source-repository upload, not a PyPI release
or a validated grant of redistribution rights. Ensure the upstream rights
review accounts for this existing GitHub distribution.

- [ ] Verify the complete Amy/Ryan training/license chain and written rights
      for redistributing the model and intended uses. The umbrella MIT metadata
      and an exculpatory statement are **not enough**.
- [ ] Preserve the original `MODEL_CARD` and all attribution notices in the
      voice wheel; validate its metadata and source revision.
- [ ] Build a real wheel from verified weights; inspect the wheel ZIP to confirm
      the `.onnx`, `.onnx.json`, `MODEL_CARD`, and notices are present.
- [ ] Install the wheel in a clean venv with `piper-tts`, disconnect networking,
      and run speech synthesis on each supported operating system/CPU.
- [ ] Confirm installed footprint, model checksum, package file-size limit,
      platform tags, naming and distribution metadata. The ONNX file is ~63 MB.
- [ ] Run `pytest`, `python -m build` and `twine check dist/*` in a properly
      provisioned release environment.
- [ ] Review GPL-3.0-or-later obligations for optional Piper runtime use.
- [ ] Only after maintainer approval, explicitly publish the **voice wheel** and
      the **core package**. There is no uploader or automated publishing.

## Attribution and risk disclosure

See [`THIRD_PARTY_VOICES.md`](../THIRD_PARTY_VOICES.md). This project did not
collect or train the underlying recordings. Source links and rights uncertainties
are disclosed there. That non-involvement does not remove any legal duties.
