# SPDX-License-Identifier: MPL-2.0

"""Command-line interface for LastLight-Voice."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict

from .detection import diagnose
from .engine import SpeechEngine
from .errors import LastLightVoiceError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lastlight-voice",
        description="Low-resource offline speech for LastLight.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    speak = sub.add_parser("speak", help="Speak text using a local TTS backend.")
    speak.add_argument("text")
    speak.add_argument("--language", default="en")
    speak.add_argument("--backend", default=None)

    synthesize = sub.add_parser("synthesize", help="Synthesize text to a local WAV file.")
    synthesize.add_argument("text")
    synthesize.add_argument("output")
    synthesize.add_argument("--language", default="en")
    synthesize.add_argument("--backend", default=None)

    voices = sub.add_parser("voices", help="List supported project voices.")
    voices.add_argument("--language", default="en")
    voices.add_argument("--backend", default=None)

    sub.add_parser("doctor", help="Check whether local offline speech is ready.")
    sub.add_parser("inspect", help="Print local runtime diagnostics as JSON.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "doctor":
            _print_doctor()
            return 0
        if args.command == "inspect":
            print(json.dumps(asdict(diagnose()), indent=2, sort_keys=True))
            return 0
        if args.command == "speak":
            SpeechEngine(language=args.language, backend=args.backend).say(args.text)
            return 0
        if args.command == "synthesize":
            output = SpeechEngine(language=args.language, backend=args.backend).save(
                args.text,
                args.output,
            )
            print(output)
            return 0
        if args.command == "voices":
            engine = SpeechEngine(language=args.language, backend=args.backend)
            for voice in engine.voices():
                print(f"{voice.id}\t{voice.language}\t{voice.name}\t{voice.backend}")
            return 0
    except LastLightVoiceError as exc:
        print(f"lastlight-voice: {exc}", file=sys.stderr)
        return 2
    return 1


def _print_doctor() -> None:
    info = diagnose()
    print("LastLight-Voice Doctor")
    print()
    print(f"Platform             {info.platform} {info.machine}")
    print(f"Python               {info.python}")
    print()
    print("Language support")
    print("English              yes")
    print("Spanish              yes")
    print()
    print("Backends")
    print(f"eSpeak NG            {'available' if info.espeak_available else 'not found'}")
    if info.espeak_executable:
        print(f"eSpeak executable    {info.espeak_executable}")
    print("Dummy                available (testing only)")
    print()
    print("Runtime policy")
    print("Network required     no")
    print("Automatic downloads  no")
    print(f"Offline ready        {'yes' if info.offline_ready else 'no'}")


if __name__ == "__main__":
    raise SystemExit(main())
