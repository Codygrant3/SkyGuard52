"""Mandatory automatic adjudicator for the M01 realism-stack visual proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery07_mapped_visual_proof01_recovery04\adjudicate_recovery07_mapped_visual_proof01_recovery04_once.py")
EXPECTED_SOURCE_BYTES = 16715
EXPECTED_SOURCE_SHA256 = "3f796903be5d595cf91e3035e417c863c2d904eeaffe06d4d986cfa635b47e42"
OLD_PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04"
NEW_PREFIX = "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01"
OLD_CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY04"
NEW_CONTRACT_ID = "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
NEW_MAP = "Lvl_M01_T08_EnvironmentRealismStack01_Recovery02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_SOURCE_BYTES or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Frozen Recovery04 postflight authority changed")
    transformed = SOURCE.read_text(encoding="utf-8")
    for required in (OLD_PREFIX, OLD_CONTRACT_ID, OLD_MAP, "Recovery07MappedVisualProof01Recovery04.csv"):
        if required not in transformed:
            raise RuntimeError(f"Postflight transformation target missing: {required}")
    transformed = transformed.replace(OLD_PREFIX, NEW_PREFIX)
    transformed = transformed.replace(OLD_CONTRACT_ID, NEW_CONTRACT_ID)
    transformed = transformed.replace(OLD_MAP, NEW_MAP)
    transformed = transformed.replace("Recovery07MappedVisualProof01Recovery04.csv", "M01EnvironmentRealismStackVisualProof01.csv")
    transformed = transformed.replace("recovery07_mapped_visual_proof01_recovery04", "m01_environment_realism_stack_visual_proof01")
    transformed = transformed.replace(
        "skyguard.t08.m01.recovery07-mapped-proof01-postflight.v1",
        "skyguard.m01-environment-realism-stack.visual-proof01-postflight.v1",
    )
    for stale in (OLD_PREFIX, OLD_CONTRACT_ID, OLD_MAP, "Recovery07MappedVisualProof01Recovery04.csv"):
        if stale in transformed:
            raise RuntimeError(f"Postflight transformation left stale token: {stale}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE), "exec"), globals(), globals())
