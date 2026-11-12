# SPDX-License-Identifier: MPL-2.0
"""Local Piper voice catalog and discovery: no runtime network calls."""

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
    """Load a package or custom catalog, validating voice IDs and asset filenames."""
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
            specs.append(PiperVoiceSpec(name, raw["language"], raw["quality"], directory, raw["files"]))
        if len({x.id for x in specs}) != len(specs):
            raise ValueError("Duplicate voice IDs")
        return tuple(specs)
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Invalid Piper voice catalog: {exc}") from exc


def find_local_model(spec: PiperVoiceSpec, models_dir: str | Path | None = None) -> Path | None:
    """Find a complete local model in a directory or an optional installed voice wheel."""
    paths: list[Path] = []
    root = models_dir or os.environ.get("LASTLIGHT_VOICE_MODELS_DIR")
    if root:
        directory = Path(root).expanduser()
        paths.extend((directory, directory / spec.id))
    # A separately packaged voice is discoverable without importing Piper or accessing a network.
    package_name = "lastlight_voice_models_" + spec.language
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError as exc:
        if exc.name != package_name:
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
