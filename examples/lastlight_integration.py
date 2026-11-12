"""Optional microphone -> LastLight query -> Piper voice example.

Requires a separate LastLight installation and a local knowledge pack.
No dependency on LastLight is added to LastLight-Voice.
"""

from __future__ import annotations

import argparse

from lastlight_voice import VoiceInteraction
from lastlight_voice.integrations import make_lastlight_responder


def main() -> None:
    parser = argparse.ArgumentParser(description="Speak to a local LastLight knowledge pack.")
    parser.add_argument("knowledge", help="Local LastLight knowledge directory or ZIP")
    args = parser.parse_args()

    # Import only in this opt-in example, not in the LastLight-Voice package.
    from lastlight import LastLight

    knowledge = LastLight(args.knowledge)
    voice = VoiceInteraction(responder=make_lastlight_responder(knowledge))
    voice.interact_once()


if __name__ == "__main__":
    main()
