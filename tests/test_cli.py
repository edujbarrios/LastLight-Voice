# SPDX-License-Identifier: MPL-2.0

import json

from lastlight_voice.cli import main


def test_doctor_runs_without_audio_backend(capsys) -> None:
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "LastLight-Voice Doctor" in output
    assert "Network required  no" in output


def test_inspect_returns_json(capsys) -> None:
    assert main(["inspect"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["network_required"] is False
    assert "espeak_available" in payload


def test_dummy_cli_speak(capsys) -> None:
    assert main(["speak", "Hello", "--backend", "dummy"]) == 0
    assert capsys.readouterr().err == ""
