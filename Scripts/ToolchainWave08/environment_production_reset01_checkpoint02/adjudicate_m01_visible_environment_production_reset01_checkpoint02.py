"""Automatic postflight wrapper for Mission 1 production Checkpoint02."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py"
EXPECTED_SOURCE = "7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440"


def main() -> None:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE:
        raise RuntimeError("Frozen Checkpoint01 adjudicator hash mismatch")
    source = raw.decode("utf-8")
    bindings = [
        ("VisibleEnvironmentProductionReset01_Checkpoint01", "VisibleEnvironmentProductionReset01_Checkpoint02"),
        ("M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01", "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02"),
        ("checkpoint01-postflight", "checkpoint02-postflight"),
    ]
    for old, new in bindings:
        if old not in source:
            raise RuntimeError(f"Missing adjudicator binding: {old}")
        source = source.replace(old, new)
    code = compile(source, str(SOURCE) + "::Checkpoint02", "exec")
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    exec(code, namespace, namespace)


if __name__ == "__main__":
    main()
