"""Bind the proven D3D12 mapped-proof lifecycle to Stage02 vegetation."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell03_recovery01_visual_proof01\capture_m01_hero_street_shore_cell03_recovery01_visual_proof01.py"
)
EXPECTED_BYTES = 7_309
EXPECTED_SHA256 = "c2d9b5f79ee53de8539e8ec004b3434cd4a739650ec8be355a219ae8610d4d95"

OLD_PREFIX = "M01_HERO_STREET_SHORE_CELL03_RECOVERY01_VISUAL_PROOF01"
NEW_PREFIX = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
OLD_ID = "M01-HERO-STREET-SHORE-CELL03-RECOVERY01-VISUAL-PROOF01"
NEW_ID = "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_HeroStreetShoreCell03Recovery01"
NEW_MAP = "Lvl_M01_PolyHavenVegetationStaging02"
OLD_CSV = "M01HeroStreetShoreCell03Recovery01VisualProof01.csv"
NEW_CSV = "M01PolyHavenVegetationStaging02VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Cell03 proof binder changed")
    namespace = {"__name__": "cell03_proof_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in ((OLD_PREFIX, NEW_PREFIX), (OLD_ID, NEW_ID), (OLD_MAP, NEW_MAP), (OLD_CSV, NEW_CSV)):
        if old not in transformed:
            raise RuntimeError(f"Stage02 proof binding token absent: {old}")
        transformed = transformed.replace(old, new)

    old_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", "M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_"))'
    new_fingerprint = 'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", "M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", "M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_", "M01_PHV02_"))'
    if transformed.count(old_fingerprint) != 1:
        raise RuntimeError("Stage02 governed-transform fingerprint anchor changed")
    transformed = transformed.replace(old_fingerprint, new_fingerprint)

    authority_start = '''        cell_freeze_path = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL03_RECOVERY01_AUTHORING_ATTEMPT01_ACCEPTANCE_FREEZE.json"'''
    authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_PolyHavenVegetationStaging02.umap"
        )'''
    start = transformed.find(authority_start)
    end = transformed.find(authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage02 authoring-authority block anchor changed")
    new_authority = '''        stage_freeze_path = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_TERMINAL_FREEZE.json"
        stage_freeze = read_json(stage_freeze_path)
        if stage_freeze.get("classification") != "PASSED_AUTOMATIC_AUTHORING_EVIDENCE_INCOMPLETE_AWAITING_D3D12_PROOF":
            raise RuntimeError("Stage02 authoring terminal classification changed")
        if stage_freeze.get("runtime_promotion") is not False:
            raise RuntimeError("Stage02 promotion guard changed")
        verify_record({"absolute_path": str(stage_freeze_path), "bytes": 5617, "sha256": "f59296aa96b7e9b630d1027e2af600520e076532d32695eab61188ff9715c0e7"})
        for stage_record in stage_freeze.get("authorities", []):
            verify_record({"absolute_path": stage_record["path"], "bytes": stage_record["bytes"], "sha256": stage_record["sha256"]})
        inventory_record = stage_freeze.get("inventory")
        verify_record({"absolute_path": inventory_record["path"], "bytes": inventory_record["bytes"], "sha256": inventory_record["sha256"]})
        stage_inventory = read_json(Path(inventory_record["path"]))
        if stage_inventory.get("staged_asset_file_count") != 38:
            raise RuntimeError("Stage02 staged-asset count changed")
        for stage_asset in stage_inventory.get("staged_assets", []):
            verify_record({"absolute_path": stage_asset["path"], "bytes": stage_asset["bytes"], "sha256": stage_asset["sha256"]})
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    insert_anchor = '''        for forbidden_prefix in ("M01_VEK02_City_", "M01_VEK02_Lighthouse_", "M01_RS01_Tree_"):'''
    if transformed.count(insert_anchor) != 1:
        raise RuntimeError("Stage02 vegetation assertion insertion anchor changed")
    vegetation_assertions = '''        vegetation_assets = {
            "M01_PHV02_fir_sapling_": (2, "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling.SM_M01_PHV_FirSapling"),
            "M01_PHV02_pine_sapling_small_": (2, "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall.SM_M01_PHV_PineSaplingSmall"),
            "M01_PHV02_shrub_02_": (6, "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02.SM_M01_PHV_Shrub02"),
            "M01_PHV02_shrub_04_": (8, "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04.SM_M01_PHV_Shrub04"),
            "M01_PHV02_grass_medium_02_": (10, "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02.SM_M01_PHV_GrassMedium02"),
        }
        for vegetation_prefix, (expected_count, mesh_path) in vegetation_assets.items():
            matched = [actor for actor in actors if actor.get_actor_label().startswith(vegetation_prefix)]
            if len(matched) != expected_count:
                raise RuntimeError(f"Stage02 vegetation prefix {vegetation_prefix}: expected {expected_count}, found {len(matched)}")
            expected_mesh = unreal.load_asset(mesh_path)
            if expected_mesh is None:
                raise RuntimeError(f"Stage02 vegetation mesh did not resolve: {mesh_path}")
            for vegetation_actor in matched:
                component = vegetation_actor.get_component_by_class(unreal.StaticMeshComponent)
                if component is None:
                    raise RuntimeError(f"Stage02 vegetation actor lacks StaticMeshComponent: {vegetation_actor.get_actor_label()}")
                actual_mesh = component.get_editor_property("static_mesh")
                if asset_identity(actual_mesh) != asset_identity(expected_mesh):
                    raise RuntimeError(f"Stage02 vegetation mesh identity changed: {vegetation_actor.get_actor_label()}")
'''
    transformed = transformed.replace(insert_anchor, vegetation_assertions + insert_anchor)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::polyhaven-vegetation-stage02-proof01", "exec"), globals(), globals())
