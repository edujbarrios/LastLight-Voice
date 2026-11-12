# SPDX-License-Identifier: MPL-2.0
"""Offline Piper voice catalog and resource discovery; never downloads at runtime."""

from __future__ import annotations

import importlib
import json
import os
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from .errors import ConfigurationError

_ID = re.compile(r"^[a-z]{2,3}_[A-Z]{2}-[A-Za-z0-9_]+-(?:x_low|low|medium|high)$")


@dataclass(frozen=True, slots=True)
class PiperVoiceSpec:
    id: str
    locale: str
    quality: str
    remote_dir: str
    files: dict[str, dict[str, Any]]

    @property
    def language(self) -> str:
        return self.locale.split("_", 1)[0]

    def filenames(self) -> tuple[str, str]:
        return self.id + ".onnx", self.id + ".onnx.json"


def load_piper_catalog(path: str | Path | None = None) -> tuple[PiperVoiceSpec, ...]:
    """Read a checked-in or explicitly supplied catalog with validated filenames."""
    if path is None:
        text = resources.files("lastlight_voice").joinpath("piper_catalog.json").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
        if payload["schema_version"] != 1 or not isinstance(payload["voices"], list):
            raise ValueError("Unsupported catalog schema")
        specs = []
        for raw in payload["voices"]:
            name = raw["id"]
            if not _ID.fullmatch(name) or raw["language"] != name.split("-", 1)[0]:
                raise ValueError(f"Invalid voice identifier or locale: {name!r}")
            directory = raw["remote_dir"]
            if not isinstance(directory, str) or any(p in ("", ".", "..") for p in directory.split("/")):
                raise ValueError(f"Invalid voice directory: {directory!r}")
            model, config = name + ".onnx", name + ".onnx.json"
            if not all(x in raw["files"] for x in (model, config, "MODEL_CARD")):
                raise ValueError(f"Voice files missing: {name}")
            for filename, meta in raw["files"].items():
                if filename not in (model, config, "MODEL_CARD"):
                    raise ValueError(f"Unexpected filename: {filename}")
                if type(meta["bytes"]) is not int or meta["bytes"] <= 0 or not re.fullmatch(r"[0-9a-f]{32}", meta["md5"]):
                    raise ValueError(f"Invalid file metadata: {filename}")
                if "sha256" in meta and not re.fullmatch(r"[0-9a-f]{64}", meta["sha256"]):
                    raise ValueError(f"Invalid SHA-256: {filename}")
            specs.append(PiperVoiceSpec(name, raw["language"], raw["quality"], directory, raw["files"]))
        if len({x.id for x in specs}) != len(specs):
            raise ValueError("Duplicate voice IDs")
        return tuple(specs)
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Invalid Piper voice catalog: {exc}") from exc


def find_local_model(spec: PiperVoiceSpec, models_dir: str | Path | None = None) -> Path | None:
    """Locate a complete locally installed model in a directory or language wheel."""
    paths = []
    root = models_dir or os.environ.get("LASTLIGHT_VOICE_MODELS_DIR")
    if root:
        directory = Path(root).expanduser()
        paths.extend((directory, directory / spec.id))
    # Optional, independently published voice data wheel (no network access).
    try:
        package = importlib.import_module("lastlight_voice_models_" + spec.language)
    except ModuleNotFoundError as exc:
        if exc.name != "lastlight_voice_models_" + spec.language:
            raise
    else:
        paths.append(Path(package.__file__).parent / "models")
    model, config = spec.filenames()
    for directory in paths:
        first, second = directory / model, directory / config
        try:
            if (first.is_file() and second.is_file()
                    and first.stat().st_size == spec.files[model]["bytes"]
                    and second.stat().st_size == spec.files[config]["bytes"]):
                return first
        except OSError:
            continue
    return None
