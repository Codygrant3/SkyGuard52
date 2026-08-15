"""Bind the proven eight-camera D3D12 proof to the authored Stage06 map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage05_composition01_recovery01_visual_proof01\capture_m01_visible_environment_stage05_composition01_recovery01_visual_proof01.py"
)
EXPECTED_BYTES = 14_648
EXPECTED_SHA256 = "3033e3364ca6d7df2b0a377d7e15cade0f13a7565c22f1ea8fb33aa1ab486032"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"{label} anchor count changed: {source.count(old)}")
    return source.replace(old, new, 1)


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage05 capture binder changed")
    namespace = {"__name__": "stage05_capture_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()

    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-RECOVERY01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage05Composition01Recovery01VisualProof01.csv", "M01VisibleEnvironmentStage06DistrictCorrection01VisualProof01.csv"),
        ("m01_visible_environment_stage05_composition01_recovery01_visual_proof01", "m01_visible_environment_stage06_district_correction01_visual_proof01"),
        ("visible-environment-stage05-composition01-recovery01-visual-proof01", "visible-environment-stage06-district-correction01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01", "Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01"),
        ("/Game/M01/VisibleEnvironmentStage05Composition01Recovery01/Materials/MI_M01_Stage05_UrbanGround_GrassRock", "/Game/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_UrbanGround_Tiled"),
    )
    optional = {
        "m01_visible_environment_stage05_composition01_recovery01_visual_proof01",
        "visible-environment-stage05-composition01-recovery01-visual-proof01",
    }
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Stage06 proof binding token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)

    old_authority_start = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01_RECOVERY01/attempt_01/authoring_receipt.json"'''
    old_authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01.umap"
        )'''
    start = transformed.find(old_authority_start)
    end = transformed.find(old_authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage06 authoring-authority block anchor changed")
    new_authority = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_AUTHORING01/attempt_01/authoring_receipt.json"
        verify_record({"absolute_path": str(authoring_path), "bytes": 21235, "sha256": "4795429ddb96a786f808410068370f74e854c2310a2312731052c65bc385dad6"})
        authoring = read_json(authoring_path)
        if authoring.get("classification") != "PASSED_STAGE06_DISTRICT_CORRECTION01_AUTHORING_AWAITING_D3D12_PROOF":
            raise RuntimeError("Stage06 authoring classification changed")
        if int(authoring.get("actor_count_before", 0)) != 217 or int(authoring.get("actor_count_after", 0)) != 225:
            raise RuntimeError("Stage06 actor-count contract changed")
        if len(authoring.get("created_buildings", [])) != 9 or len(authoring.get("created_vegetation", [])) != 28:
            raise RuntimeError("Stage06 production-art count changed")
        if len(authoring.get("removed_facades", [])) != 16 or len(authoring.get("removed_bollards", [])) != 13:
            raise RuntimeError("Stage06 replacement count changed")
        if authoring.get("runtime_promotion_performed") is not False or authoring.get("error") is not None:
            raise RuntimeError("Stage06 authoring safety state changed")
        terminal_path = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_AUTHORING01_TERMINAL_MANIFEST.json"
        verify_record({"absolute_path": str(terminal_path), "bytes": 4723, "sha256": "f701bd70ddd844281f633211650652b032c8803cfa463793c9f0706aa329d1df"})
        terminal = read_json(terminal_path)
        if terminal.get("classification") != "PASSED_STAGE06_DISTRICT_CORRECTION01_AUTHORING_AWAITING_D3D12_PROOF" or terminal.get("exit_code") != 0:
            raise RuntimeError("Stage06 terminal authority changed")
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    old_removed = '''        for removed_prefix in ("M01_ACA03R01_City_", "M01_HSSC03_City_", "M01_STAGE04R03_Facade_"):
            if any(label.startswith(removed_prefix) for label in by_label):
                raise RuntimeError(f"Removed Stage04 actor survived Stage05: {removed_prefix}")'''
    new_removed = '''        for removed_prefix in ("M01_ACA03R01_City_", "M01_HSSC03_City_", "M01_STAGE04R03_Facade_", "M01_STAGE05R01_Facade_", "M01_Promenade_Bollard_"):
            if any(label.startswith(removed_prefix) for label in by_label):
                raise RuntimeError(f"Removed legacy actor survived Stage06: {removed_prefix}")'''
    transformed = replace_once(transformed, old_removed, new_removed, "removed-actor")

    facade_start = transformed.find('''        facade_assets = {''')
    vegetation_start = transformed.find('''        vegetation_assets = {''', facade_start)
    if facade_start < 0 or vegetation_start < 0:
        raise RuntimeError("Stage05 facade assertion block anchor changed")
    stage06_buildings = '''        stage06_expected_buildings = {"D06": "MidriseB", "D07": "ApartmentA", "D08": "CornerC"}
        stage06_building_count = 0
        for placement, family in stage06_expected_buildings.items():
            for suffix, mesh_path in building_assets[family].items():
                label = f"M01_STAGE06_City_{placement}_{family}_{suffix}"
                matched = by_label.get(label, [])
                if len(matched) != 1:
                    raise RuntimeError(f"Stage06 building actor missing: {label}")
                component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
                mesh = unreal.load_asset(mesh_path)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage06 building mesh changed: {label}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage06 building is not visible: {label}")
                stage06_building_count += 1
        if stage06_building_count != 9:
            raise RuntimeError(f"Stage06 expected 9 building parts; found {stage06_building_count}")

'''
    transformed = transformed[:facade_start] + stage06_buildings + transformed[vegetation_start:]

    old_vegetation_end = '''        if vegetation_count != 28:
            raise RuntimeError(f"Stage05 expected 28 vegetation actors; found {vegetation_count}")

        lighthouse_meshes = {'''
    new_vegetation_end = '''        if vegetation_count != 28:
            raise RuntimeError(f"Stage05 expected 28 vegetation actors; found {vegetation_count}")

        stage06_vegetation_assets = {
            "M01_STAGE06_Vegetation_fir_sapling_": (2, "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling.SM_M01_PHV_FirSapling"),
            "M01_STAGE06_Vegetation_pine_sapling_small_": (2, "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall.SM_M01_PHV_PineSaplingSmall"),
            "M01_STAGE06_Vegetation_shrub_02_": (6, "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02.SM_M01_PHV_Shrub02"),
            "M01_STAGE06_Vegetation_shrub_04_": (8, "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04.SM_M01_PHV_Shrub04"),
            "M01_STAGE06_Vegetation_grass_medium_02_": (10, "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02.SM_M01_PHV_GrassMedium02"),
        }
        stage06_vegetation_count = 0
        for prefix, (expected_count, mesh_path) in stage06_vegetation_assets.items():
            matched = [actor for actor in actors if actor.get_actor_label().startswith(prefix)]
            if len(matched) != expected_count:
                raise RuntimeError(f"Stage06 vegetation {prefix}: expected {expected_count}, found {len(matched)}")
            mesh = unreal.load_asset(mesh_path)
            for actor in matched:
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage06 vegetation mesh changed: {actor.get_actor_label()}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage06 vegetation hidden: {actor.get_actor_label()}")
                stage06_vegetation_count += 1
        if stage06_vegetation_count != 28:
            raise RuntimeError(f"Stage06 expected 28 vegetation actors; found {stage06_vegetation_count}")

        lighthouse_meshes = {'''
    transformed = replace_once(transformed, old_vegetation_end, new_vegetation_end, "vegetation")

    fingerprint_old = '"M01_STAGE03_", "M01_STAGE04R03_", "M01_STAGE05R01_"))'
    fingerprint_new = '"M01_STAGE03_", "M01_STAGE04R03_", "M01_STAGE05R01_", "M01_STAGE06_"))'
    transformed = replace_once(transformed, fingerprint_old, fingerprint_new, "transform-fingerprint")

    for stale in (
        "M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01",
        "Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01",
    ):
        if stale in transformed:
            raise RuntimeError(f"Stage06 capture retained stale proof token: {stale}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage06-district-correction01", "exec"), globals(), globals())
