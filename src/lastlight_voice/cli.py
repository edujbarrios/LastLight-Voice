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
from .interaction import VoiceInteraction
from .stt import VoskTranscriber
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

    interact = sub.add_parser("interact", help="Listen to the microphone and reply aloud offline.")
    interact.add_argument("--language", default="en", help="STT language (currently en).")
    interact.add_argument("--seconds", type=float, default=10.0, help="Maximum recording time.")
    interact.add_argument("--device", default=None, help="Input microphone device ID or name.")

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
            info = diagnose()
            payload = asdict(info)
            payload["offline_ready"] = info.offline_ready
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.command == "interact":
            device = int(args.device) if args.device and args.device.isdecimal() else args.device
            session = VoiceInteraction(
                language=args.language,
                transcriber=VoskTranscriber(language=args.language, device=device),
            )
            print("Listening... speak into your microphone.", flush=True)
            turn = session.interact_once(timeout_seconds=args.seconds)
            if turn is None:
                print("No speech recognized.", file=sys.stderr)
                return 1
            print(f"Heard: {turn.transcript}")
            print(f"Replied: {turn.response}")
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
    print("Piper (Amy low)      " + ("available" if info.piper_available else "not found"))
    if info.piper_voices:
        print("Piper voices         " + ", ".join(info.piper_voices))
    print("Vosk STT (English)   " + ("available" if info.stt_available else "not found"))
    print("Dummy                available (testing only)")
    print()
    print("Runtime policy")
    print("Network required     no")
    print("Automatic downloads  no")
    print(f"Offline ready        {'yes' if info.offline_ready else 'no'}")


if __name__ == "__main__":
    raise SystemExit(main())
