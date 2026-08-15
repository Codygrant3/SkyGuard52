"""Bind the proven eight-camera D3D12 proof to the authored Stage07A map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage06_district_correction01_visual_proof01\capture_m01_visible_environment_stage06_district_correction01_visual_proof01.py"
)
EXPECTED_BYTES = 11_050
EXPECTED_SHA256 = "e7402561b73899296da3a73f2ab800edf6fb74e8007a1ea583e3cc0e5c95a4a0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"{label} anchor count changed: {source.count(old)}")
    return source.replace(old, new, 1)


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage06 capture binder changed")
    namespace = {"__name__": "stage06_capture_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()

    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage06DistrictCorrection01VisualProof01.csv", "M01VisibleEnvironmentStage07AHeroCorridor01VisualProof01.csv"),
        ("m01_visible_environment_stage06_district_correction01_visual_proof01", "m01_visible_environment_stage07a_hero_corridor01_visual_proof01"),
        ("visible-environment-stage06-district-correction01-visual-proof01", "visible-environment-stage07a-hero-corridor01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01", "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01"),
        ("/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_UrbanGround_Tiled", "/Game/M01/VisibleEnvironmentStage07AHeroCorridor01/Materials/MI_M01_Stage07A_DistrictGround"),
    )
    optional = {
        "m01_visible_environment_stage06_district_correction01_visual_proof01",
        "visible-environment-stage06-district-correction01-visual-proof01",
    }
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Stage07A proof binding token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)

    old_authority_start = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_AUTHORING01/attempt_01/authoring_receipt.json"'''
    old_authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01.umap"
        )'''
    start = transformed.find(old_authority_start)
    end = transformed.find(old_authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage07A authoring-authority block anchor changed")
    new_authority = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_AUTHORING01/attempt_01/authoring_receipt.json"
        verify_record({"absolute_path": str(authoring_path), "bytes": 46036, "sha256": "5084c737ea45169adf00b98a8d26fdc4143a04c37d1ac8f0b308326aa31fabcf"})
        authoring = read_json(authoring_path)
        if authoring.get("classification") != "PASSED_STAGE07A_HERO_CORRIDOR01_AUTHORING_AWAITING_CHECKPOINT_VISUAL":
            raise RuntimeError("Stage07A authoring classification changed")
        if int(authoring.get("actor_count_before_governed", 0)) != 225 or int(authoring.get("actor_count_after_governed", 0)) != 301:
            raise RuntimeError("Stage07A actor-count contract changed")
        if len(authoring.get("created_buildings", [])) != 12 or len(authoring.get("created_vegetation", [])) != 48 or len(authoring.get("created_street_details", [])) != 16:
            raise RuntimeError("Stage07A production-art count changed")
        if len(authoring.get("building_materials", [])) != 39 or len(authoring.get("semantic_materials", [])) != 5:
            raise RuntimeError("Stage07A material-binding count changed")
        contact = authoring.get("contact_preservation", {})
        if contact.get("visible") is not False or contact.get("hidden_in_game") is not True:
            raise RuntimeError("Stage07A rejected-contact state changed")
        if authoring.get("runtime_promotion_performed") is not False or authoring.get("error") is not None:
            raise RuntimeError("Stage07A authoring safety state changed")
        terminal_path = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_AUTHORING01_TERMINAL_MANIFEST.json"
        verify_record({"absolute_path": str(terminal_path), "bytes": 9253, "sha256": "dfd863593f765e655cf701c619bc320cc5425d25efb3db2ade34f2a05330d897"})
        terminal = read_json(terminal_path)
        if terminal.get("classification") != "PASSED_STAGE07A_HERO_CORRIDOR01_AUTHORING_AWAITING_CHECKPOINT_VISUAL" or terminal.get("exit_code") != 0:
            raise RuntimeError("Stage07A terminal authority changed")
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    insert_anchor = '''        lighthouse_meshes = {'''
    insertion = '''        stage07a_buildings = {"H01": "ApartmentA", "H02": "CornerC", "H03": "MidriseB", "H04": "ApartmentA"}
        stage07a_building_count = 0
        for placement, family in stage07a_buildings.items():
            for suffix, mesh_path in building_assets[family].items():
                label = f"M01_STAGE07A_City_{placement}_{family}_{suffix}"
                matched = by_label.get(label, [])
                if len(matched) != 1:
                    raise RuntimeError(f"Stage07A building actor missing: {label}")
                component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
                mesh = unreal.load_asset(mesh_path)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage07A building mesh changed: {label}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage07A building hidden: {label}")
                stage07a_building_count += 1
        if stage07a_building_count != 12:
            raise RuntimeError(f"Stage07A expected 12 building parts; found {stage07a_building_count}")

        stage07a_vegetation_assets = {
            "M01_STAGE07A_Vegetation_fir_sapling_": (9, "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling.SM_M01_PHV_FirSapling"),
            "M01_STAGE07A_Vegetation_pine_sapling_small_": (9, "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall.SM_M01_PHV_PineSaplingSmall"),
            "M01_STAGE07A_Vegetation_shrub_02_": (10, "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02.SM_M01_PHV_Shrub02"),
            "M01_STAGE07A_Vegetation_shrub_04_": (10, "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04.SM_M01_PHV_Shrub04"),
            "M01_STAGE07A_Vegetation_grass_medium_02_": (10, "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02.SM_M01_PHV_GrassMedium02"),
        }
        stage07a_vegetation_count = 0
        for prefix, (expected_count, mesh_path) in stage07a_vegetation_assets.items():
            matched = [actor for actor in actors if actor.get_actor_label().startswith(prefix)]
            if len(matched) != expected_count:
                raise RuntimeError(f"Stage07A vegetation {prefix}: expected {expected_count}, found {len(matched)}")
            mesh = unreal.load_asset(mesh_path)
            for actor in matched:
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage07A vegetation mesh changed: {actor.get_actor_label()}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage07A vegetation hidden: {actor.get_actor_label()}")
                stage07a_vegetation_count += 1
        if stage07a_vegetation_count != 48:
            raise RuntimeError(f"Stage07A expected 48 vegetation actors; found {stage07a_vegetation_count}")

        stage07a_prop_assets = {
            "M01_STAGE07A_Street_Bollard_": (4, "/Game/M01/PromenadeBollardRecovery01/StaticMeshes/SM_M01_Promenade_Bollard_A.SM_M01_Promenade_Bollard_A"),
            "M01_STAGE07A_Street_BicycleRack_": (4, "/Game/M01/PromenadeBicycleRackRecovery02/StaticMeshes/SM_M01_Promenade_BicycleRack_A.SM_M01_Promenade_BicycleRack_A"),
            "M01_STAGE07A_Street_LitterBin_": (4, "/Game/M01/PromenadeLitterBinProduction01/StaticMeshes/SM_M01_Promenade_LitterBin_A.SM_M01_Promenade_LitterBin_A"),
            "M01_STAGE07A_Street_UtilityCabinet_": (4, "/Game/M01/PromenadeUtilityCabinetRecovery04/StaticMeshes/SM_M01_Promenade_UtilityCabinet_A.SM_M01_Promenade_UtilityCabinet_A"),
        }
        stage07a_prop_count = 0
        for prefix, (expected_count, mesh_path) in stage07a_prop_assets.items():
            matched = [actor for actor in actors if actor.get_actor_label().startswith(prefix)]
            if len(matched) != expected_count:
                raise RuntimeError(f"Stage07A street detail {prefix}: expected {expected_count}, found {len(matched)}")
            mesh = unreal.load_asset(mesh_path)
            for actor in matched:
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage07A street-detail mesh changed: {actor.get_actor_label()}")
                stage07a_prop_count += 1
        if stage07a_prop_count != 16:
            raise RuntimeError(f"Stage07A expected 16 street-detail actors; found {stage07a_prop_count}")

'''
    if transformed.count(insert_anchor) != 1:
        raise RuntimeError("Stage07A identity-check insertion anchor changed")
    transformed = transformed.replace(insert_anchor, insertion + insert_anchor, 1)

    fingerprint_old = '"M01_STAGE03_", "M01_STAGE04R03_", "M01_STAGE05R01_", "M01_STAGE06_"))'
    fingerprint_new = '"M01_STAGE03_", "M01_STAGE04R03_", "M01_STAGE05R01_", "M01_STAGE06_", "M01_STAGE07A_"))'
    transformed = replace_once(transformed, fingerprint_old, fingerprint_new, "transform-fingerprint")

    for stale in (
        "M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01",
        "Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01",
    ):
        if stale in transformed:
            raise RuntimeError(f"Stage07A capture retained stale proof token: {stale}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage07a-hero-corridor01", "exec"), globals(), globals())
