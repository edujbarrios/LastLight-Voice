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

- no required network access;
- no telemetry or automatic downloads;
- prefer small dependencies and standard-library solutions;
- keep English and Spanish behavior tested;
- make backend selection deterministic and explainable;
- provide graceful failure when optional software or hardware is unavailable;
- add typing and tests for new public behavior.

Large dependencies require a clear justification including RAM, CPU, disk, startup, and energy implications.

## Pull requests

Keep changes focused, document behavior changes, and include tests. Do not present roadmap functionality as implemented until it is actually available.
