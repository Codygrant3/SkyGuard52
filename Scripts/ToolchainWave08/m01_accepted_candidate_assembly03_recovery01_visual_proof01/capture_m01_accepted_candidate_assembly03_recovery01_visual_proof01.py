"""Bind the proven D3D12 mapped-proof lifecycle to Assembly03 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01\capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01.py"
)
EXPECTED_BYTES = 4054
EXPECTED_SHA256 = "7ac4a9e8033e468eec0da4a8148b512675774b02846f1834836b36e99022fe8b"

OLD_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01"
NEW_PREFIX = "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01"
OLD_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01"
NEW_ID = "M01-ACCEPTED-CANDIDATE-ASSEMBLY03-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
NEW_MAP = "Lvl_M01_AcceptedCandidateAssembly03_Recovery01"
OLD_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv"
NEW_CSV = "M01AcceptedCandidateAssembly03Recovery01VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if (
        not SOURCE.is_file()
        or SOURCE.stat().st_size != EXPECTED_BYTES
        or sha256(SOURCE) != EXPECTED_SHA256
    ):
        raise RuntimeError("Frozen corridor visual-proof binder changed")
    namespace = {"__name__": "corridor_visual_proof_binder_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
    ):
        if old not in transformed:
            raise RuntimeError(f"Visual-proof binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for stale in (OLD_PREFIX, OLD_ID, OLD_MAP, OLD_CSV):
        if stale in transformed:
            raise RuntimeError(f"Visual-proof binding retained stale token: {stale}")

    old_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_VEK02_"))'
    new_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_"))'
    if transformed.count(old_fingerprint) != 1:
        raise RuntimeError("Governed-transform fingerprint anchor changed")
    transformed = transformed.replace(old_fingerprint, new_fingerprint)

    old_authority_start = '''        axis_terminal_path = ROOT / "Saved/Reports/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"'''
    old_authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_AcceptedCandidateAssembly03_Recovery01.umap"
        )'''
    start = transformed.find(old_authority_start)
    end = transformed.find(old_authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Imported-corridor authority block anchor changed")
    new_authority = '''        assembly_freeze_path = ROOT / "Docs/AAA_Review/M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_ACCEPTANCE_FREEZE.json"
        assembly_freeze = read_json(assembly_freeze_path)
        if assembly_freeze.get("classification") != "PASSED_M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_STRUCTURAL_ACCEPTED_AWAITING_MAPPED_VISUAL_PROOF":
            raise RuntimeError("Assembly03 Recovery01 acceptance classification changed")
        if assembly_freeze.get("runtime_promotion") is not False:
            raise RuntimeError("Assembly03 Recovery01 promotion guard changed")
        for assembly_record in assembly_freeze.get("authorities", []):
            verify_record({"absolute_path": assembly_record["path"], "bytes": assembly_record["bytes"], "sha256": assembly_record["sha256"]})
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    old_corridor_start = '''        corridor_expected_y = {
            "M01_C06R01_Corridor_TERRAIN": 11486.601318359375,'''
    old_corridor_end = '''        transient_pcg = corridor_by_label.get("PCGWorldActor0", [])'''
    start = transformed.find(old_corridor_start)
    end = transformed.find(old_corridor_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Corridor-runtime assertion block anchor changed")
    new_runtime = '''        by_label = {}
        for governed_actor in actors:
            by_label.setdefault(governed_actor.get_actor_label(), []).append(governed_actor)
        exact_labels = (
            "M01_C06R01_Corridor_TERRAIN",
            "M01_C06R01_Corridor_HARDSCAPE",
            "M01_C06R01_Corridor_DETAILS",
            "M01_ACA03R01_Corridor_CONTACT",
        )
        for exact_label in exact_labels:
            if len(by_label.get(exact_label, [])) != 1:
                raise RuntimeError(f"Expected exactly one Assembly03 actor {exact_label}; found {len(by_label.get(exact_label, []))}")
        for prefix, expected_count in {
            "M01_ACA03R01_City_": 54,
            "M01_Promenade_Bollard_": 13,
            "M01_Promenade_BicycleRack_": 8,
            "M01_Promenade_UtilityCabinet_": 5,
            "M01_Promenade_StormDrain_": 12,
            "M01_Promenade_LitterBin_": 10,
        }.items():
            actual_count = sum(actor.get_actor_label().startswith(prefix) for actor in actors)
            if actual_count != expected_count:
                raise RuntimeError(f"Assembly03 prefix {prefix}: expected {expected_count}, found {actual_count}")
        for forbidden_prefix in ("M01_VEK02_City_", "M01_VEK02_Lighthouse_", "M01_RS01_Tree_"):
            if any(actor.get_actor_label().startswith(forbidden_prefix) for actor in actors):
                raise RuntimeError(f"Rejected proxy actor survived Assembly03: {forbidden_prefix}")
        corridor_by_label = by_label
'''
    transformed = transformed[:start] + new_runtime + transformed[end:]
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::assembly03-proof01", "exec"), globals(), globals())
