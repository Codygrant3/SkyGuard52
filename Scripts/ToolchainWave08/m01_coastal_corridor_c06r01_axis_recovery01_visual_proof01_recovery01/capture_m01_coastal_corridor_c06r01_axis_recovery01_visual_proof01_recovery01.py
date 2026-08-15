"""Bind the corridor D3D12 proof to a fresh namespace with an exact transient-PCG contract."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01\capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01.py"
)
EXPECTED_BYTES = 6736
EXPECTED_SHA256 = "185b146ead3a0a588b385fed0d4a2b2d23fc04753069eb1990839ad9488413bc"

OLD_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_"
NEW_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01"
OLD_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01"
NEW_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01"
OLD_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv"
NEW_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen corridor Axis Recovery01 proof executor changed")
    namespace = {"__name__": "corridor_axis_recovery01_proof_executor_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_ID, NEW_ID),
        (OLD_CSV, NEW_CSV),
    )
    quoted_old_prefix = f'"{OLD_PREFIX}"'
    quoted_new_prefix = f'"{NEW_PREFIX}"'
    if transformed.count(quoted_old_prefix) != 5:
        raise RuntimeError("Executor Recovery01 prefix-fragment count changed")
    transformed = transformed.replace(quoted_old_prefix, quoted_new_prefix)
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Executor Recovery01 binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    suffix_replacements = (
        ('"VISUAL_PROOF01_CONTRACT.json"', '"_CONTRACT.json"'),
        ('"VISUAL_PROOF01_CAMERAS.json"', '"_CAMERAS.json"'),
        ('"VISUAL_PROOF01/launcher_attempt_01/"', '"/launcher_attempt_01/"'),
    )
    for old, new in suffix_replacements:
        if old not in transformed:
            raise RuntimeError(f"Executor Recovery01 suffix token is absent: {old}")
        transformed = transformed.replace(old, new)
    if quoted_old_prefix in transformed:
        raise RuntimeError(f"Executor Recovery01 retained stale token: {OLD_PREFIX}")
    for old, _ in replacements:
        if f'"{old}"' in transformed:
            raise RuntimeError(f"Executor Recovery01 retained stale token: {old}")
    anchor = "        inventory = [actor_inventory_record(actor) for actor in actors]"
    if transformed.count(anchor) != 1:
        raise RuntimeError("Executor transient-PCG validation anchor changed")
    transient_validation = '''        transient_pcg = corridor_by_label.get("PCGWorldActor0", [])
        if len(transient_pcg) != 1:
            raise RuntimeError(f"Expected exactly one transient PCGWorldActor0; found {len(transient_pcg)}")
        transient_class = transient_pcg[0].get_class().get_path_name()
        if transient_class != "/Script/PCG.PCGWorldActor":
            raise RuntimeError(f"Unexpected transient PCG actor class: {transient_class}")
        transient_transform = actor_transform_record(transient_pcg[0])
        if transient_transform["location_cm"] != [0.0, 0.0, 0.0] or transient_transform["scale"] != [1.0, 1.0, 1.0]:
            raise RuntimeError(f"Transient PCGWorldActor0 transform changed: {transient_transform}")
        inventory = [actor_inventory_record(actor) for actor in actors]'''
    transformed = transformed.replace(anchor, transient_validation)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::corridor-axis-recovery01-proof01-recovery01", "exec"), globals(), globals())
