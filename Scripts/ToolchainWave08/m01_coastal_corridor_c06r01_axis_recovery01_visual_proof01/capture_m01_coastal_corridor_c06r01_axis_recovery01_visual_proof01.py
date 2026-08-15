"""Bind the proven eight-camera D3D12 executor to the corrected coastal corridor map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01\capture_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01.py"
)
EXPECTED_BYTES = 2485
EXPECTED_SHA256 = "daedea79d0c36cc6b11391aa6095d7dddc5e97b9c03c09642f691fa7e60e1433"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_"
NEW_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-ENVIRONMENT-COMPOSITION-CORRECTION05-RECOVERY02-VISUAL-PROOF01"
NEW_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02"
NEW_MAP = "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
OLD_CSV = "M01PhotorealFoundationWave01EnvironmentCompositionCorrection05Recovery02VisualProof01.csv"
NEW_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen EnvironmentCompositionCorrection05 Recovery02 proof executor changed")
    namespace = {"__name__": "environment_composition_correction05_recovery02_proof_executor_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Executor binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old in transformed:
            raise RuntimeError(f"Executor retained stale token: {old}")
    anchor = "        actors = unreal.EditorLevelLibrary.get_all_level_actors()\n        inventory = [actor_inventory_record(actor) for actor in actors]"
    if transformed.count(anchor) != 1:
        raise RuntimeError("Executor corridor-validation anchor changed")
    corridor_validation = '''        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        corridor_expected_y = {
            "M01_C06R01_Corridor_TERRAIN": 11486.601318359375,
            "M01_C06R01_Corridor_HARDSCAPE": 13060.8935546875,
            "M01_C06R01_Corridor_DETAILS": 9347.952392578125,
        }
        corridor_by_label = {}
        for corridor_actor in actors:
            corridor_by_label.setdefault(corridor_actor.get_actor_label(), []).append(corridor_actor)
        for corridor_label, expected_origin_y in corridor_expected_y.items():
            matches = corridor_by_label.get(corridor_label, [])
            if len(matches) != 1:
                raise RuntimeError(f"Expected exactly one corrected corridor actor {corridor_label}; found {len(matches)}")
            corridor_actor = matches[0]
            corridor_scale = corridor_actor.get_actor_scale3d()
            if abs(float(corridor_scale.x) - 1.0) > 0.001 or abs(float(corridor_scale.y) + 1.0) > 0.001 or abs(float(corridor_scale.z) - 1.0) > 0.001:
                raise RuntimeError(f"Corrected corridor scale changed for {corridor_label}: {corridor_scale}")
            corridor_origin, corridor_extent = corridor_actor.get_actor_bounds(False)
            if abs(float(corridor_origin.y) - expected_origin_y) > 2.0 or float(corridor_origin.y) <= 0.0:
                raise RuntimeError(f"Corrected corridor positive-Y bounds failed for {corridor_label}: {corridor_origin.y}")
            if float(corridor_extent.y) <= 0.0:
                raise RuntimeError(f"Corrected corridor Y extent failed for {corridor_label}: {corridor_extent.y}")
        inventory = [actor_inventory_record(actor) for actor in actors]'''
    transformed = transformed.replace(anchor, corridor_validation)
    authority_anchor = '''        for record in contract["locked_inputs"]:
            verify_record(record)
        map_file = ISOLATED_ROOT / ('''
    if transformed.count(authority_anchor) != 1:
        raise RuntimeError("Executor imported-asset authority anchor changed")
    authority_validation = '''        for record in contract["locked_inputs"]:
            verify_record(record)
        axis_terminal_path = ROOT / "Saved/Reports/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"
        axis_terminal = read_json(axis_terminal_path)
        if axis_terminal.get("classification") != "PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF":
            raise RuntimeError("Axis Recovery01 terminal authority classification changed")
        if axis_terminal.get("imported_assets_unchanged") is not True:
            raise RuntimeError("Axis Recovery01 imported-asset preservation evidence changed")
        prior_contract_path = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01_CONTRACT.json"
        prior_contract = read_json(prior_contract_path)
        for prior_record in prior_contract.get("locked_inputs", []):
            verify_record(prior_record)
        imported_records = axis_terminal.get("imported_assets_after", [])
        if len(imported_records) != 39:
            raise RuntimeError(f"Expected 39 frozen imported corridor assets; found {len(imported_records)}")
        for imported_record in imported_records:
            imported_path = Path(imported_record["path"])
            if not imported_path.is_file():
                raise RuntimeError(f"Frozen imported corridor asset is missing: {imported_path}")
            if imported_path.stat().st_size != int(imported_record["bytes"]):
                raise RuntimeError(f"Frozen imported corridor asset byte count changed: {imported_path}")
            if sha256_file(imported_path) != imported_record["sha256"]:
                raise RuntimeError(f"Frozen imported corridor asset hash changed: {imported_path}")
        map_file = ISOLATED_ROOT / ('''
    transformed = transformed.replace(authority_anchor, authority_validation)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::coastal-corridor-c06r01-axis-recovery01-proof01", "exec"), globals(), globals())
