"""Bind the proven eight-camera D3D12 proof to the fresh Stage05 map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_visual_proof01_recovery01\capture_m01_visible_environment_stage04_recovery03_visual_proof01_recovery01.py"
)
EXPECTED_BYTES = 2_370
EXPECTED_SHA256 = "1ca06da1434c0b3b272e1e76a58db188c79bdbed17c42c8ec0e09f3eed3b4241"
OLD_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01"
NEW_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01"
OLD_ID = "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01-RECOVERY01"
NEW_ID = "M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-RECOVERY01-VISUAL-PROOF01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage04 Recovery01 capture binder changed")
    namespace = {"__name__": "stage04_recovery01_capture_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()

    optional = {
        "m01_visible_environment_stage04_recovery03_visual_proof01_recovery01",
        "visible-environment-stage04-recovery03-visual-proof01-recovery01",
    }
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        ("M01VisibleEnvironmentStage04Recovery03VisualProof01Recovery01.csv", "M01VisibleEnvironmentStage05Composition01Recovery01VisualProof01.csv"),
        ("m01_visible_environment_stage04_recovery03_visual_proof01_recovery01", "m01_visible_environment_stage05_composition01_recovery01_visual_proof01"),
        ("visible-environment-stage04-recovery03-visual-proof01-recovery01", "visible-environment-stage05-composition01-recovery01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage04Recovery03", "Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01"),
        ("/Game/M01/VisibleEnvironmentStage03/Materials/MI_M01_Stage03_UrbanGround_GrassRock", "/Game/M01/VisibleEnvironmentStage05Composition01Recovery01/Materials/MI_M01_Stage05_UrbanGround_GrassRock"),
    ):
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Stage05 proof binding token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)

    old_authority_start = '''        postflight_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01/attempt_01/postflight_receipt.json"'''
    old_authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01.umap"
        )'''
    start = transformed.find(old_authority_start)
    end = transformed.find(old_authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage05 authoring-authority block anchor changed")
    new_authority = '''        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01_RECOVERY01/attempt_01/authoring_receipt.json"
        verify_record({"absolute_path": str(authoring_path), "bytes": 38300, "sha256": "e8cbf0f32f123bc27ed890d736b9b6d196e2d159cb198f730f1cb55797ff07b9"})
        authoring = read_json(authoring_path)
        if authoring.get("classification") != "PASSED_STAGE05_COMPOSITION01_AUTHORING_AWAITING_POSTFLIGHT_AND_D3D12_PROOF":
            raise RuntimeError("Stage05 Recovery01 authoring classification changed")
        if int(authoring.get("actor_count_before", 0)) != 230 or int(authoring.get("actor_count_after", 0)) != 217:
            raise RuntimeError("Stage05 Recovery01 actor-count contract changed")
        if len(authoring.get("created_buildings", [])) != 18 or len(authoring.get("created_facades", [])) != 16:
            raise RuntimeError("Stage05 Recovery01 production-art count changed")
        if len(authoring.get("vegetation_adjustments", [])) != 28 or len(authoring.get("prop_adjustments", [])) < 59:
            raise RuntimeError("Stage05 Recovery01 grounding count changed")
        if authoring.get("runtime_promotion_performed") is not False or authoring.get("error") is not None:
            raise RuntimeError("Stage05 Recovery01 authoring safety state changed")
        terminal_path = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01_RECOVERY01_TERMINAL_MANIFEST.json"
        verify_record({"absolute_path": str(terminal_path), "bytes": 4503, "sha256": "fbd89c98e11b2c49de1365f1115503186d5696bc7a58497d0ddad6eee7e8f60f"})
        terminal = read_json(terminal_path)
        if terminal.get("classification") != "PASSED_STAGE05_COMPOSITION01_AUTHORING_AWAITING_POSTFLIGHT_AND_D3D12_PROOF" or terminal.get("exit_code") != 0:
            raise RuntimeError("Stage05 Recovery01 terminal authority changed")
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    assertions_start = '''        exact_labels = (
            "M01_C06R01_Corridor_TERRAIN",'''
    assertions_end = '''        for forbidden_prefix in ("M01_VEK02_City_", "M01_VEK02_Lighthouse_", "M01_RS01_Tree_"):'''
    start = transformed.find(assertions_start)
    end = transformed.find(assertions_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage05 world-assertion block anchor changed")
    stage05_assertions = '''        exact_labels = (
            "M01_C06R01_Corridor_TERRAIN", "M01_C06R01_Corridor_HARDSCAPE",
            "M01_C06R01_Corridor_DETAILS", "M01_ACA03R01_Corridor_CONTACT",
            "M01_HSSC02_CoastalA_TERRAIN", "M01_HSSC02_CoastalA_HARDSCAPE",
        )
        for exact_label in exact_labels:
            if len(by_label.get(exact_label, [])) != 1:
                raise RuntimeError(f"Expected one Stage05 actor {exact_label}; found {len(by_label.get(exact_label, []))}")
        for removed_prefix in ("M01_ACA03R01_City_", "M01_HSSC03_City_", "M01_STAGE04R03_Facade_"):
            if any(label.startswith(removed_prefix) for label in by_label):
                raise RuntimeError(f"Removed Stage04 actor survived Stage05: {removed_prefix}")

        building_assets = {
            "ApartmentA": {
                "STRUCTURAL": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_STRUCTURAL.SM_M01_ApartmentA_STRUCTURAL",
                "GLAZING": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_GLAZING.SM_M01_ApartmentA_GLAZING",
                "DETAILS": "/Game/M01/EnvKit02/M01_APARTMENT_A/StaticMeshes/SM_M01_ApartmentA_DETAILS.SM_M01_ApartmentA_DETAILS",
            },
            "MidriseB": {
                "STRUCTURAL": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_STRUCTURAL.SM_M01_MidriseB_STRUCTURAL",
                "GLAZING": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_GLAZING.SM_M01_MidriseB_GLAZING",
                "DETAILS": "/Game/M01/EnvKit02/M01_MIDRISE_B/StaticMeshes/SM_M01_MidriseB_DETAILS.SM_M01_MidriseB_DETAILS",
            },
            "CornerC": {
                "STRUCTURAL": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_STRUCTURAL.SM_M01_CornerC_STRUCTURAL",
                "GLAZING": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_GLAZING.SM_M01_CornerC_GLAZING",
                "DETAILS": "/Game/M01/EnvKit02/M01_CORNER_RESIDENCE_C/StaticMeshes/SM_M01_CornerC_DETAILS.SM_M01_CornerC_DETAILS",
            },
        }
        expected_buildings = {"B00": "ApartmentA", "B01": "MidriseB", "B02": "CornerC", "B03": "CornerC", "B04": "ApartmentA", "B05": "MidriseB"}
        building_count = 0
        for placement, family in expected_buildings.items():
            for suffix, mesh_path in building_assets[family].items():
                label = f"M01_STAGE05R01_City_{placement}_{family}_{suffix}"
                matched = by_label.get(label, [])
                if len(matched) != 1:
                    raise RuntimeError(f"Stage05 building actor missing: {label}")
                component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
                mesh = unreal.load_asset(mesh_path)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage05 building mesh changed: {label}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage05 building is not visible: {label}")
                building_count += 1
        if building_count != 18:
            raise RuntimeError(f"Stage05 expected 18 building parts; found {building_count}")

        facade_assets = {
            "BalconyDetails": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_BalconyDetails.SM_M01_CoastalFacadeBay_A_BalconyDetails",
            "Glass": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Glass.SM_M01_CoastalFacadeBay_A_Glass",
            "Interior": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Interior.SM_M01_CoastalFacadeBay_A_Interior",
            "StructureFrame": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_StructureFrame.SM_M01_CoastalFacadeBay_A_StructureFrame",
        }
        facade_count = 0
        for placement in ("F00", "F01", "F02", "F03"):
            for suffix, mesh_path in facade_assets.items():
                label = f"M01_STAGE05R01_Facade_{placement}_{suffix}"
                matched = by_label.get(label, [])
                if len(matched) != 1:
                    raise RuntimeError(f"Stage05 facade actor missing: {label}")
                component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
                mesh = unreal.load_asset(mesh_path)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage05 facade mesh changed: {label}")
                facade_count += 1
        if facade_count != 16:
            raise RuntimeError(f"Stage05 expected 16 facade parts; found {facade_count}")

        vegetation_assets = {
            "M01_PHV02_fir_sapling_": (2, "/Game/M01/SourceBacked/VegetationStaging02/fir_sapling/SM_M01_PHV_FirSapling.SM_M01_PHV_FirSapling"),
            "M01_PHV02_pine_sapling_small_": (2, "/Game/M01/SourceBacked/VegetationStaging02/pine_sapling_small/SM_M01_PHV_PineSaplingSmall.SM_M01_PHV_PineSaplingSmall"),
            "M01_PHV02_shrub_02_": (6, "/Game/M01/SourceBacked/VegetationStaging02/shrub_02/SM_M01_PHV_Shrub02.SM_M01_PHV_Shrub02"),
            "M01_PHV02_shrub_04_": (8, "/Game/M01/SourceBacked/VegetationStaging02/shrub_04/SM_M01_PHV_Shrub04.SM_M01_PHV_Shrub04"),
            "M01_PHV02_grass_medium_02_": (10, "/Game/M01/SourceBacked/VegetationStaging02/grass_medium_02/SM_M01_PHV_GrassMedium02.SM_M01_PHV_GrassMedium02"),
        }
        vegetation_count = 0
        for prefix, (expected_count, mesh_path) in vegetation_assets.items():
            matched = [actor for actor in actors if actor.get_actor_label().startswith(prefix)]
            if len(matched) != expected_count:
                raise RuntimeError(f"Stage05 vegetation {prefix}: expected {expected_count}, found {len(matched)}")
            mesh = unreal.load_asset(mesh_path)
            for actor in matched:
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                    raise RuntimeError(f"Stage05 vegetation mesh changed: {actor.get_actor_label()}")
                if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage05 vegetation hidden: {actor.get_actor_label()}")
                vegetation_count += 1
        if vegetation_count != 28:
            raise RuntimeError(f"Stage05 expected 28 vegetation actors; found {vegetation_count}")

        lighthouse_meshes = {
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Details_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Details_A.SM_M01_Lighthouse_Details_A",
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Lantern_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Lantern_A.SM_M01_Lighthouse_Lantern_A",
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Tower_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Tower_A.SM_M01_Lighthouse_Tower_A",
        }
        for label, mesh_path in lighthouse_meshes.items():
            matched = by_label.get(label, [])
            if len(matched) != 1:
                raise RuntimeError(f"Stage05 lighthouse part missing: {label}")
            component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
            mesh = unreal.load_asset(mesh_path)
            if component is None or mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(mesh):
                raise RuntimeError(f"Stage05 lighthouse mesh changed: {label}")
            if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                raise RuntimeError(f"Stage05 lighthouse hidden: {label}")
'''
    transformed = transformed[:start] + stage05_assertions + transformed[end:]

    fingerprint_old = '"M01_STAGE03_", "M01_STAGE04R03_"))'
    fingerprint_new = '"M01_STAGE03_", "M01_STAGE04R03_", "M01_STAGE05R01_"))'
    if transformed.count(fingerprint_old) != 1:
        raise RuntimeError("Stage05 transform-fingerprint anchor changed")
    transformed = transformed.replace(fingerprint_old, fingerprint_new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage05-composition01-recovery01", "exec"), globals(), globals())
