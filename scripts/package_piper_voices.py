#!/usr/bin/env python3
"""Explicit build-time Piper voice download and opt-in local wheel preparation.

Never runs on pip install or at runtime. Does not publish packages.
"""
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


def verify(path: Path, metadata: dict) -> None:
    if not path.is_file() or path.stat().st_size != metadata["bytes"]:
        raise ValueError(f"Missing/incorrect voice file: {path}")
    # MD5 supplied by upstream is for corruption detection, not a secure signature.
    md5 = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            md5.update(chunk)
    if md5.hexdigest() != metadata["md5"]:
        raise ValueError(f"Checksum mismatch: {path}")


def provision(spec, models_dir: Path, allow_download: bool) -> Path:
    location = models_dir / spec.id
    location.mkdir(parents=True, exist_ok=True)
    for remote_file, meta in spec.files.items():
        local_name = spec.id + ".MODEL_CARD" if remote_file == "MODEL_CARD" else remote_file
        local_file = location / local_name
        try:
            verify(local_file, meta)
            continue
        except ValueError:
            if not allow_download:
                raise
        url = SOURCE + "/" + spec.remote_dir + "/" + remote_file
        with tempfile.NamedTemporaryFile(dir=location, suffix=".part", delete=False) as fp:
            part = Path(fp.name)
        try:
            print("Downloading", url, flush=True)
            with urllib.request.urlopen(url, timeout=120) as response, part.open("wb") as out:
                shutil.copyfileobj(response, out)
            verify(part, meta)
            part.replace(local_file)
        finally:
            part.unlink(missing_ok=True)
    return location


def generate_voice_project(spec, local: Path, out: Path) -> Path:
    module = "lastlight_voice_models_" + spec.language
    dist = "lastlight-voice-model-" + spec.language
    target = out / (dist + "-" + spec.id)
    if target.exists():
        raise FileExistsError(f"Already exists: {target}")
    assets = target / "src" / module / "models"
    assets.mkdir(parents=True)
    (assets.parent / "__init__.py").write_text('"""Local Piper voice model files."""\n')
    for name in (*spec.filenames(), spec.id + ".MODEL_CARD"):
        shutil.copy2(local / name, assets / name)
    (target / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=68", "wheel"]\n'
        'build-backend = "setuptools.build_meta"\n\n'
        '[project]\nname = "' + dist + '"\nversion = "0.1.0"\n'
        'requires-python = ">=3.10"\n'
        'description = "Offline English Piper model for LastLight-Voice"\n\n'
        '[tool.setuptools.packages.find]\nwhere = ["src"]\n\n'
        '[tool.setuptools.package-data]\n"' + module + '" = ["models/*"]\n'
    )
    (target / "README.md").write_text(
        "# " + dist + "\n\nGenerated locally; not approved for public redistribution. "
        "Review voice MODEL_CARD, dataset and fine-tuning licenses first.\n"
    )
    return target


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--voice", action="append", default=[])
    ap.add_argument("--download", action="store_true", help="Allow explicit download")
    ap.add_argument("--models-dir", type=Path, default=Path(".piper-model-cache"))
    ap.add_argument("--output-dir", type=Path, default=Path("dist/voice-pack-sources"))
    ap.add_argument("--prepare-packs", action="store_true")
    ap.add_argument("--acknowledge-licenses", action="store_true")
    args = ap.parse_args(argv)
    catalog = {s.id: s for s in load_piper_catalog()}
    if args.list:
        for voice in catalog.values():
            print(voice.id, voice.language)
        return 0
    if not args.voice:
        ap.error("Specify --voice or --list")
    if args.prepare_packs and not args.acknowledge_licenses:
        ap.error("Rights review required: pass --acknowledge-licenses only after confirmation")
    if len(args.voice) != len(set(args.voice)):
        ap.error("Duplicate voice")
    for voice_id in args.voice:
        if voice_id not in catalog:
            ap.error(f"Unknown voice: {voice_id}")
        spec = catalog[voice_id]
        local = provision(spec, args.models_dir, args.download)
        print(f"Verified {voice_id} in {local}")
        if args.prepare_packs:
            target = generate_voice_project(spec, local, args.output_dir)
            print(f"Build locally: python -m build --wheel {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
