"""Recovery02 output binding for the frozen Checkpoint01 adjudicator."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\adjudicate_m01_visible_environment_production_reset01_checkpoint01.py"
EXPECTED_SHA256 = "7b74c7d08a0918172b064553865dbd9d1868fca4e56f38be5f2e659c4046b440"


def main() -> None:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("Frozen adjudicator hash mismatch")
    source = raw.decode("utf-8")
    replacements = [
        ('VisibleEnvironmentProductionReset01_Checkpoint01"', 'VisibleEnvironmentProductionReset01_Checkpoint01_Recovery02"'),
        ("M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_POSTFLIGHT.json", "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY02_POSTFLIGHT.json"),
    ]
    for old, new in replacements:
        if source.count(old) != 1:
            raise RuntimeError(f"Expected exactly one adjudicator binding for {old!r}")
        source = source.replace(old, new)
    code = compile(source, str(SOURCE) + "::Recovery02", "exec")
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    exec(code, namespace, namespace)


if __name__ == "__main__":
    main()
