"""Blender 5.2 compatibility binding for Production Reset01 Checkpoint01.

The frozen Checkpoint01 generator is verified and transformed in memory.  The
only functional API correction is NISHITA -> MULTIPLE_SCATTERING.  The output
and blend paths are rebound to fresh Recovery01 namespaces.  No failed output
geometry is opened or read.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py"
EXPECTED_SHA256 = "fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891"


def main() -> None:
    raw = SOURCE.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"Frozen generator hash mismatch: {actual}")
    source = raw.decode("utf-8")
    substitutions = [
        (
            'VisibleEnvironmentProductionReset01_Checkpoint01"',
            'VisibleEnvironmentProductionReset01_Checkpoint01_Recovery01"',
            1,
        ),
        (
            'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01.blend',
            'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY01.blend',
            1,
        ),
        ('sky.sky_type = "NISHITA"', 'sky.sky_type = "MULTIPLE_SCATTERING"', 1),
    ]
    for old, new, expected_count in substitutions:
        count = source.count(old)
        if count != expected_count:
            raise RuntimeError(f"Expected {expected_count} occurrence(s) of {old!r}; found {count}")
        source = source.replace(old, new)
    if "VisibleEnvironmentProductionReset01_Checkpoint01\"" in source:
        raise RuntimeError("Original output binding remains after transformation")
    code = compile(source, str(SOURCE) + "::Recovery01", "exec")
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    exec(code, namespace, namespace)


if __name__ == "__main__":
    main()
