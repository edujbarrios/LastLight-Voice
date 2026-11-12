# SPDX-License-Identifier: MPL-2.0
"""Local-only Piper tests; no large weights or network required."""
import json
import subprocess
import wave

import pytest
from lastlight_voice import ConfigurationError, SpeechEngine
from lastlight_voice.backends.piper import PiperBackend
from lastlight_voice.errors import BackendUnavailableError
from lastlight_voice.piper_voices import find_local_model, load_piper_catalog


def test_default_catalog_english_only():
    assert [v.id for v in load_piper_catalog()] == ["en_US-amy-low"]


def test_missing_model_fails_offline(tmp_path, monkeypatch):
    monkeypatch.setattr("lastlight_voice.backends.piper.shutil.which", lambda _: "/usr/bin/piper")
    backend = PiperBackend(models_dir=tmp_path)
    assert not backend.available()
    with pytest.raises(BackendUnavailableError):
        backend.synthesize("hello", language="en")


def test_custom_catalog_supports_future_language(tmp_path, monkeypatch):
    monkeypatch.setattr("lastlight_voice.backends.piper.shutil.which", lambda _: "/usr/bin/piper")
    voice = "fr_FR-test-low"
    files = {
        voice + ".onnx": {"bytes": 3, "md5": "a" * 32},
        voice + ".onnx.json": {"bytes": 2, "md5": "b" * 32},
        "MODEL_CARD": {"bytes": 1, "md5": "c" * 32},
    }
    metadata = {"schema_version": 1, "voices": [{
        "id": voice, "language": "fr_FR", "quality": "low",
        "remote_dir": "fr/fr_FR/test/low", "files": files,
    }]}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps(metadata))
    (tmp_path / (voice + ".onnx")).write_bytes(b"abc")
    (tmp_path / (voice + ".onnx.json")).write_bytes(b"{}")
    backend = PiperBackend(models_dir=tmp_path, catalog_path=catalog)
    assert [v.language for v in backend.voices()] == ["fr"]
    assert SpeechEngine(language="fr-FR", backend=backend).language == "fr"


def test_piper_wav_generation_uses_local_files(tmp_path, monkeypatch):
    monkeypatch.setattr("lastlight_voice.backends.piper.shutil.which", lambda _: "/usr/bin/piper")
    spec = load_piper_catalog()[0]
    model, config = spec.filenames()
    data = {"schema_version": 1, "voices": [{
        "id": spec.id, "language": spec.locale, "quality": "low",
        "remote_dir": spec.remote_dir, "files": {
            model: {"bytes": 3, "md5": "a" * 32},
            config: {"bytes": 2, "md5": "b" * 32},
            "MODEL_CARD": {"bytes": 1, "md5": "c" * 32},
        }
    }]}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps(data))
    (tmp_path / model).write_bytes(b"abc")
    (tmp_path / config).write_bytes(b"{}")
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        with wave.open(cmd[cmd.index("--output_file") + 1], "wb") as wav:
            wav.setframerate(16000)
            wav.setsampwidth(2)
            wav.setnchannels(1)
            wav.writeframes(b"\x00\x00" * 160)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("lastlight_voice.backends.piper.subprocess.run", fake_run)
    engine = SpeechEngine(language="en_US", backend=PiperBackend(models_dir=tmp_path, catalog_path=catalog))
    assert engine.synthesize("Hello").duration == pytest.approx(0.01)
    command, kwargs = calls[0]
    assert "--model" in command and "--config" in command
    assert kwargs["input"] == "Hello\n"
    assert "shell" not in kwargs


def test_other_languages_not_in_dummy():
    with pytest.raises(ConfigurationError):
        SpeechEngine(language="it", backend="dummy")


def test_amy_model_is_bundled_for_editable_and_normal_installs():
    """Real weights and config must ship within lastlight_voice itself."""
    spec = load_piper_catalog()[0]
    model = find_local_model(spec)
    assert model is not None, "Core package must include real Amy model"
    assert "lastlight_voice" in model.parts
    assert model.stat().st_size == spec.files[spec.filenames()[0]]["bytes"]
    assert model.with_name(model.name + ".json").is_file()
    assert (model.parent / (spec.id + ".MODEL_CARD")).is_file()
