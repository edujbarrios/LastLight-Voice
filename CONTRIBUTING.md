# Contributing to LastLight-Voice

Thanks for helping improve offline speech on constrained hardware.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Project rules

Contributions should preserve the runtime principles:

- no network access during speech synthesis; dependency installation may fetch packages;
- no telemetry or downloads at import/runtime; all bundled weights are tracked and verified;
- prefer small dependencies and standard-library solutions;
- keep English and Spanish behavior tested;
- make backend selection deterministic and explainable;
- provide graceful failure when optional software or hardware is unavailable;
- add typing and tests for new public behavior.

Large models or dependencies require a clear justification including RAM, CPU, disk, startup, licensing, and energy implications. New voice models require a model card, source attribution and documented redistribution rights.

## Pull requests

Keep changes focused, document behavior changes, and include tests. Do not present roadmap functionality as implemented until it is actually available.
