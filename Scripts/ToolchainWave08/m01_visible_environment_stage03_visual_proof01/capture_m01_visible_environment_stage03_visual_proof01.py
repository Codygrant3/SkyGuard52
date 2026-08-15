"""Bind the proven mapped-proof lifecycle to the accepted Stage03 environment."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\capture_m01_polyhaven_vegetation_staging02_visual_proof01.py"
)
EXPECTED_BYTES = 6_895
EXPECTED_SHA256 = "0b2f184a3937bf87c56127957bd36101ae633e3ab3f252beb916291bd6851f96"

OLD_PREFIX = "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"
NEW_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE03_VISUAL_PROOF01"
OLD_ID = "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01"
NEW_ID = "M01-VISIBLE-ENVIRONMENT-STAGE03-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PolyHavenVegetationStaging02"
NEW_MAP = "Lvl_M01_VisibleEnvironmentStage03"
OLD_CSV = "M01PolyHavenVegetationStaging02VisualProof01.csv"
NEW_CSV = "M01VisibleEnvironmentStage03VisualProof01.csv"
OLD_MATERIAL = "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_UrbanGround_Tiled"
NEW_MATERIAL = "/Game/M01/VisibleEnvironmentStage03/Materials/MI_M01_Stage03_UrbanGround_GrassRock"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if (
        not SOURCE.is_file()
        or SOURCE.stat().st_size != EXPECTED_BYTES
        or sha256(SOURCE) != EXPECTED_SHA256
    ):
        raise RuntimeError("Frozen Stage02 proof binder changed")
    namespace = {"__name__": "stage02_proof_binder_authority", "__file__": str(SOURCE)}
    exec(
        compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"),
        namespace,
        namespace,
    )
    transformed = namespace["transform_source"]()
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
        (OLD_MATERIAL, NEW_MATERIAL),
    ):
        if old not in transformed:
            raise RuntimeError(f"Stage03 proof binding token absent: {old}")
        transformed = transformed.replace(old, new)

    old_fingerprint = (
        'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", '
        '"M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", '
        '"M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_", "M01_PHV02_"))'
    )
    new_fingerprint = (
        'actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_", '
        '"M01_ACA03R01_", "M01_C06R01_", "M01_Promenade_", '
        '"M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_", "M01_PHV02_", '
        '"M01_STAGE03_"))'
    )
    if transformed.count(old_fingerprint) != 1:
        raise RuntimeError("Stage03 governed-transform fingerprint anchor changed")
    transformed = transformed.replace(old_fingerprint, new_fingerprint)

    authority_start = '''        stage_freeze_path = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_TERMINAL_FREEZE.json"'''
    authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage03.umap"
        )'''
    start = transformed.find(authority_start)
    end = transformed.find(authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage03 authoring-authority block anchor changed")
    new_authority = '''        stage_freeze_path = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01_ATTEMPT01_ACCEPTANCE_FREEZE.json"
        stage_freeze = read_json(stage_freeze_path)
        if stage_freeze.get("classification") != "PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF":
            raise RuntimeError("Stage03 authoring classification changed")
        if stage_freeze.get("runtime_promotion") is not False:
            raise RuntimeError("Stage03 promotion guard changed")
        verify_record({"absolute_path": str(stage_freeze_path), "bytes": 2911, "sha256": "87188f14348811f6b868aad256f56a9f1efe7e9ecd22b754c445c0656252fc8e"})
        for stage_record in stage_freeze.get("members", []):
            verify_record({"absolute_path": stage_record["path"], "bytes": stage_record["bytes"], "sha256": stage_record["sha256"]})
        authoring_receipt = read_json(ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01/attempt_01/authoring_receipt.json")
        if authoring_receipt.get("classification") != "PASSED_STAGE03_AUTHORING_AWAITING_D3D12_VISUAL_PROOF":
            raise RuntimeError("Stage03 authoring receipt changed")
        if int(authoring_receipt.get("actor_count_after", 0)) != 195:
            raise RuntimeError("Stage03 governed actor count changed")
        stage02_freeze_path = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_TERMINAL_FREEZE.json"
        stage02_freeze = read_json(stage02_freeze_path)
        verify_record({"absolute_path": str(stage02_freeze_path), "bytes": 5617, "sha256": "f59296aa96b7e9b630d1027e2af600520e076532d32695eab61188ff9715c0e7"})
        inventory_record = stage02_freeze.get("inventory")
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
        raise RuntimeError("Stage03 assertion insertion anchor changed")
    stage03_assertions = '''        for hidden_label in ("M01_HSSC02_CoastalA_TERRAIN", "M01_HSSC02_CoastalA_HARDSCAPE"):
            hidden_component = by_label[hidden_label][0].get_component_by_class(unreal.StaticMeshComponent)
            if hidden_component is None:
                raise RuntimeError(f"Stage03 hidden overlap lacks StaticMeshComponent: {hidden_label}")
            if bool(hidden_component.get_editor_property("visible")) or not bool(hidden_component.get_editor_property("hidden_in_game")):
                raise RuntimeError(f"Stage03 legacy overlap is not hidden: {hidden_label}")
        lighthouse_assets = {
            "M01_STAGE03_Lighthouse_Hero_STRUCTURAL": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_STRUCTURAL.SM_M01_LighthouseA_STRUCTURAL",
            "M01_STAGE03_Lighthouse_Hero_GLAZING": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_GLAZING.SM_M01_LighthouseA_GLAZING",
            "M01_STAGE03_Lighthouse_Hero_DETAILS": "/Game/M01/EnvKit02/M01_LIGHTHOUSE_A/StaticMeshes/SM_M01_LighthouseA_DETAILS.SM_M01_LighthouseA_DETAILS",
        }
        for lighthouse_label, mesh_path in lighthouse_assets.items():
            if len(by_label.get(lighthouse_label, [])) != 1:
                raise RuntimeError(f"Stage03 lighthouse group missing: {lighthouse_label}")
            component = by_label[lighthouse_label][0].get_component_by_class(unreal.StaticMeshComponent)
            expected_mesh = unreal.load_asset(mesh_path)
            if component is None or expected_mesh is None:
                raise RuntimeError(f"Stage03 lighthouse mesh unresolved: {lighthouse_label}")
            if asset_identity(component.get_editor_property("static_mesh")) != asset_identity(expected_mesh):
                raise RuntimeError(f"Stage03 lighthouse mesh identity changed: {lighthouse_label}")
        structural = by_label["M01_STAGE03_Lighthouse_Hero_STRUCTURAL"][0]
        structural_origin, structural_extent = structural.get_actor_bounds(False)
        if float(structural_origin.z - structural_extent.z) < -5.0:
            raise RuntimeError("Stage03 lighthouse is below the governed ground datum")
'''
    transformed = transformed.replace(insert_anchor, stage03_assertions + insert_anchor)
    return transformed


if __name__ == "__main__":
    exec(
        compile(transform_source(), str(SOURCE) + "::stage03-visual-proof01", "exec"),
        globals(),
        globals(),
    )
