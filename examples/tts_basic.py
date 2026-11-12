# SPDX-License-Identifier: MPL-2.0
"""Smallest offline text-to-WAV example (does not need audio playback hardware)."""

from lastlight_voice import SpeechEngine


def main() -> None:
    voice = SpeechEngine(language="en")  # Bundled Piper Amy
    audio = voice.synthesize("Hello from LastLight!")
    output = audio.save("hello.wav")
    print(f"Wrote {output} ({len(audio.data)} WAV bytes)")


if __name__ == "__main__":
    main()
