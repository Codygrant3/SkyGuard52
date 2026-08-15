"""Nongoverned argv recorder for the Recovery03 exact-host transport test."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    output_value = os.environ.get("SKYGUARD_RECOVERY03_ARGV_OUTPUT")
    if not output_value:
        raise RuntimeError("SKYGUARD_RECOVERY03_ARGV_OUTPUT is required")
    output = Path(output_value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "schema": "skyguard.t08.m01.recovery07-mapped-proof01-recovery03-argv.v1",
                "argv": sys.argv[1:],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

