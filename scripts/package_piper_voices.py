#!/usr/bin/env python3
"""Explicit, build-time Piper voice pack builder (never runs on pip install)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lastlight_voice.piper_voices import load_piper_catalog  # noqa: E402

SOURCE = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"


def verify(path: Path, expected: dict) -> None:
    if not path.is_file() or path.stat().st_size != expected["bytes"]:
        raise ValueError(f"Wrong size or missing voice asset: {path}")
    digest = hashlib.md5()  # nosec: upstream checksum for corruption detection, not security
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected["md5"]:
        raise ValueError(f"Upstream checksum mismatch: {path}")
    if "sha256" in expected:
        digest256 = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest256.update(chunk)
        if digest256.hexdigest() != expected["sha256"]:
            raise ValueError(f"Upstream SHA-256 mismatch: {path}")


def prepare(spec, models_dir: Path, download: bool) -> Path:
    """Copy/verify voice assets; optional explicit upstream fetch, never at runtime."""
    directory = models_dir / spec.id
    directory.mkdir(parents=True, exist_ok=True)
    for filename, expected in spec.files.items():
        local = directory / (spec.id + ".MODEL_CARD" if filename == "MODEL_CARD" else filename)
        try:
            verify(local, expected)
            continue
        except ValueError:
            if not download:
                raise
        url = SOURCE + "/" + spec.remote_dir + "/" + filename
        print(f"Downloading {url}", flush=True)
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".part", delete=False) as handle:
            temp = Path(handle.name)
        try:
            with urllib.request.urlopen(url, timeout=120) as response, temp.open("wb") as target:
                shutil.copyfileobj(response, target, length=1024 * 1024)
            verify(temp, expected)
            temp.replace(local)
        finally:
            temp.unlink(missing_ok=True)
    return directory


def make_pack(spec, source: Path, target_root: Path) -> Path:
    """Generate a separate, build-ready Python distribution for one voice."""
    family = spec.language
    module = f"lastlight_voice_models_{family}"
    dist = f"lastlight-voice-model-{family}"
    out = target_root / (dist + "-" + spec.id)
    if out.exists():
        raise FileExistsError(f"Destination already exists: {out}")
    destination = out / "src" / module / "models"
    destination.mkdir(parents=True)
    (destination.parent / "__init__.py").write_text('"""Bundled offline Piper data for LastLight-Voice."""\n', encoding="utf-8")
    for filename in (*spec.filenames(), spec.id + ".MODEL_CARD"):
        shutil.copy2(source / filename, destination / filename)
    (out / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=68", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n'
        '[project]\nname = "' + dist + '"\nversion = "0.1.0"\n'
        'description = "Offline Piper voice ' + spec.id + ' for LastLight-Voice"\n'
        'requires-python = ">=3.10"\n\n'
        '[tool.setuptools.packages.find]\nwhere = ["src"]\n\n'
        '[tool.setuptools.package-data]\n"' + module + '" = ["models/*"]\n',
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        f"# {dist}\n\nContains `{spec.id}` for offline synthesis in LastLight-Voice.\n"
        "Attribution and a license-risk warning are included in THIRD_PARTY_VOICES.md.\n"
        "The original upstream MODEL_CARD ships alongside the ONNX weights.\n"
        "This internal review bundle is NOT approved for public redistribution.\n",
        encoding="utf-8",
    )
    shutil.copy2(ROOT / "THIRD_PARTY_VOICES.md", out / "THIRD_PARTY_VOICES.md")
    shutil.copy2(ROOT / "THIRD_PARTY_VOICES.md", destination / "THIRD_PARTY_VOICES.md")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="Show available catalog entries")
    parser.add_argument("--voice", action="append", default=[], help="Selected voice ID (repeatable)")
    parser.add_argument("--models-dir", type=Path, default=Path(".piper-model-cache"))
    parser.add_argument("--output-dir", type=Path, default=Path("dist/voice-pack-sources"))
    parser.add_argument("--download", action="store_true", help="Explicitly download model assets (requires Internet)")
    parser.add_argument("--prepare-packs", action="store_true", help="Generate one independent package per selected voice")
    parser.add_argument("--acknowledge-licenses", action="store_true", help="Explicitly acknowledge unresolved licensing and prepare an internal review package")
    args = parser.parse_args(argv)
    catalog = {voice.id: voice for voice in load_piper_catalog()}
    if args.list:
        for voice in catalog.values():
            print(f"{voice.id}\t{voice.language}\t{sum(v['bytes'] for v in voice.files.values()) / 1_048_576:.2f} MiB")
        return 0
    if not args.voice:
        parser.error("Select one or more --voice IDs, or use --list")
    if args.prepare_packs and not args.acknowledge_licenses:
        parser.error("--prepare-packs requires --acknowledge-licenses (internal review only; NOT a redistribution grant)")
    chosen = []
    for name in args.voice:
        if name not in catalog:
            parser.error(f"Unknown voice: {name}")
        if name in (v.id for v in chosen):
            parser.error(f"Repeated voice: {name}")
        chosen.append(catalog[name])
    if args.prepare_packs and len({v.language for v in chosen}) != len(chosen):
        parser.error("This packaging version supports one voice per language pack")
    for voice in chosen:
        directory = prepare(voice, args.models_dir, args.download)
        print(f"Verified {voice.id}: {directory}")
        if args.prepare_packs:
            result = make_pack(voice, directory, args.output_dir)
            print(f"Ready to build: python -m build --wheel {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
