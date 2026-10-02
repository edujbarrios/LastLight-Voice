# SPDX-License-Identifier: MPL-2.0

import json

from lastlight_voice.cli import main


def test_doctor_runs_without_audio_backend(capsys) -> None:
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "LastLight-Voice Doctor" in output
    assert "Network required     no" in output
    assert "Automatic downloads  no" in output


def test_inspect_returns_json(capsys) -> None:
    assert main(["inspect"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["network_required"] is False
    assert payload["automatic_downloads"] is False
    assert payload["supported_languages"] == ["en", "es"]
    assert payload["offline_ready"] == payload["espeak_available"]
    assert "espeak_available" in payload
    assert "espeak_executable" in payload


def test_dummy_cli_speak(capsys) -> None:
    assert main(["speak", "Hello", "--backend", "dummy"]) == 0
    assert capsys.readouterr().err == ""


def test_dummy_cli_synthesize_writes_wav(tmp_path, capsys) -> None:
    output = tmp_path / "speech.wav"

    assert main(["synthesize", "Offline", str(output), "--backend", "dummy"]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.strip() == str(output)
    assert output.read_bytes().startswith(b"RIFF")
